"""Reproducible retrospective US pharmaceutical-manufacturing factor falsification.

Fixed 2026-10-26 Federal Reserve/FRED snapshot, NOT publication-vintage data.
No securities or company fundamentals are claimed. No internet required to rerun.
"""
from pathlib import Path
import hashlib, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
RAW = ROOT/'data'/'official_snapshot.csv'
RNG_SEED = 20261026
ALPHA = 20.0
BASE_FEATURES = ['pharma_yoy','pharma_3m','manuf_yoy']
FEATURES = BASE_FEATURES+['gap']


def read_data(path=RAW):
    raw = pd.read_csv(path)
    assert list(raw.columns)==['DATE','PHARMA','CHEM','MANUF']
    raw['date']=pd.to_datetime(raw['DATE']+'-01')
    assert raw['date'].is_unique and raw['date'].is_monotonic_increasing
    assert raw['date'].dt.to_period('M').tolist()==list(pd.period_range(raw.date.min(),raw.date.max(),freq='M'))
    assert raw[['PHARMA','CHEM','MANUF']].notna().all().all()
    assert (raw[['PHARMA','CHEM','MANUF']]>0).all().all()
    return raw.set_index('date')[['PHARMA','CHEM','MANUF']].astype(float)


def make_panel(raw, horizon=6, release_lag=2, gap_weights=(1.0,1.0), stale=0):
    """Origin t is calendar month-end; all signal inputs <= t-release_lag.

    y = 100 log(PHARMA[t+h] / PHARMA[t-release_lag]).
    Purging is enforced separately in walk_forward with u+h+release_lag <= t.
    """
    lag=int(release_lag); h=int(horizon)
    assert lag>=1 and h>=1
    d=pd.DataFrame(index=raw.index)
    lp=np.log(raw.PHARMA); lc=np.log(raw.CHEM); lm=np.log(raw.MANUF)
    d['pharma_yoy']=(100*(lp-lp.shift(12))).shift(lag)
    d['pharma_3m']=(100*(lp-lp.shift(3))).shift(lag)
    d['manuf_yoy']=(100*(lm-lm.shift(12))).shift(lag)
    d['chem_yoy']=(100*(lc-lc.shift(12))).shift(lag+stale)
    d['gap']=np.tanh((gap_weights[0]*d.chem_yoy-gap_weights[1]*d.manuf_yoy)/10.0)
    d['target']=100*(lp.shift(-h)-lp.shift(lag))
    d['origin_index']=np.arange(len(d))
    return d.dropna().copy()


def ridge_array(X, y, x, alpha=ALPHA):
    mu=X.mean(axis=0); sd=X.std(axis=0)
    sd[sd<1e-12]=1.0
    A=(X-mu)/sd; a=(x-mu)/sd
    beta=np.linalg.solve(A.T@A+alpha*np.eye(X.shape[1]),A.T@(y-y.mean()))
    return float(y.mean()+a@beta)


def ridge_predict(train, test, features, alpha=ALPHA):
    return ridge_array(train[features].to_numpy(float),train.target.to_numpy(float),test[features].to_numpy(float)[0],alpha)


def walk_forward(panel, horizon=6, lag=2, min_train=48, start='2017-01-01', train_window=None):
    """Array-backed expanding OOS; labels matured at u+h+lag <= t."""
    dates=panel.index
    origin=panel.origin_index.to_numpy(int)
    y=panel.target.to_numpy(float)
    X=panel[FEATURES].to_numpy(float)
    out=[]
    first=np.searchsorted(dates,np.datetime64(start))
    for i in range(first,len(panel)):
        end=np.searchsorted(origin,origin[i]-horizon-lag,side='right')
        beg=max(0,end-train_window) if train_window else 0
        if end-beg<min_train:continue
        train=X[beg:end]; yi=y[beg:end]; xi=X[i]
        out.append((dates[i],int(origin[i]),end-beg,float(y[i]),float(yi.mean()),
                    ridge_array(train[:,:2],yi,xi[:2]),
                    ridge_array(train[:,:3],yi,xi[:3]),
                    ridge_array(train,yi,xi),
                    ridge_array(train[:,3:4],yi,xi[3:4]),float(xi[3])))
    return pd.DataFrame(out,columns=['date','origin_index','n_train','actual','mean','persistence','macro','full','gap_only','gap']).set_index('date')


def score(pred):
    if len(pred)==0: return {}
    y=pred.actual.to_numpy(float)
    return {col:{'rmse':float(np.sqrt(np.mean((y-pred[col])**2))),
                 'mae':float(np.mean(np.abs(y-pred[col])))}
            for col in ['mean','persistence','macro','full','gap_only']}


def improvement(pred, base='macro', challenger='full'):
    return score(pred)[base]['rmse']-score(pred)[challenger]['rmse']


def block_bootstrap(pred, draws=2000, block=12, seed=RNG_SEED):
    rng=np.random.default_rng(seed); n=len(pred)
    y=pred.actual.to_numpy(); b=pred.macro.to_numpy(); f=pred.full.to_numpy()
    results=[]
    for _ in range(draws):
        starts=rng.integers(0,n,size=int(np.ceil(n/block)))
        idx=np.concatenate([(s+np.arange(block))%n for s in starts])[:n]
        results.append(np.sqrt(np.mean((y[idx]-b[idx])**2))-np.sqrt(np.mean((y[idx]-f[idx])**2)))
    return np.asarray(results)


def shuffle_gap_blocks(panel, block, rng):
    """Exploratory alignment placebo: permute non-overlapping 12-month blocks.

    This is NOT an exact null randomization p-value for autocorrelated data.
    """
    p=panel.copy(); x=p.gap.to_numpy()
    groups=[x[i:i+block] for i in range(0,len(x),block)]
    perm=rng.permutation(len(groups))
    p['gap']=np.concatenate([groups[i] for i in perm])[:len(p)] if len(x)%block==0 else np.concatenate([groups[i] for i in perm])[:len(p)]
    # Last short block can move; total length is unchanged.
    return p


def block_placebo(panel, observed, draws=1000, block=12, seed=RNG_SEED):
    rng=np.random.default_rng(seed); results=[]
    for _ in range(draws):
        p=shuffle_gap_blocks(panel,block,rng)
        o=walk_forward(p)
        results.append(improvement(o))
    a=np.asarray(results)
    return a,float((1+np.sum(a>=observed))/(len(a)+1))


def exposure_sensitivity(raw, draws=1000, seed=RNG_SEED):
    rng=np.random.default_rng(seed); results=[]
    for _ in range(draws):
        weights=rng.uniform(0.5,1.5,2)
        p=make_panel(raw,gap_weights=weights)
        o=walk_forward(p)
        results.append([weights[0],weights[1],improvement(o)])
    return pd.DataFrame(results,columns=['chemical_weight','manufacturing_weight','rmse_improvement_pp'])


def summarize_regimes(pred):
    out={}
    slices={'pre_2020':pred[pred.index<'2020-01-01'],
            '2020_2021':pred[(pred.index>='2020-01-01')&(pred.index<'2022-01-01')],
            'post_2021':pred[pred.index>='2022-01-01'],
            'exclude_2020_2021':pred[(pred.index<'2020-01-01')|(pred.index>='2022-01-01')]}
    for k,v in slices.items():
        out[k]={'n':len(v),'improvement_pp':improvement(v) if len(v) else None,
                'scores':score(v)}
    return out


def save_figures(raw,panel,oos,placebo,boot,sens):
    (ROOT/'figures').mkdir(exist_ok=True)
    figs={}
    def store(name):
        plt.tight_layout(); p=ROOT/'figures'/f'{name}.svg';plt.savefig(p,bbox_inches='tight');plt.close();figs[name]=str(p.relative_to(ROOT))
    ax=raw.plot(figsize=(11,4),title='Official G.17 fixed snapshot (2010–2026); index 2017=100')
    ax.set_ylabel('Industrial production index');ax.grid(alpha=.2);store('01_industrial_indices')
    ax=panel[['pharma_yoy','chem_yoy','manuf_yoy']].plot(figsize=(11,4),title='At-origin known t−2 log YoY growth (%)')
    ax.set_ylabel('percentage points');ax.axhline(0,color='black',lw=.5);ax.grid(alpha=.2);store('02_growth_features')
    fig,ax=plt.subplots(figsize=(11,4));ax.plot(panel.index,panel.gap,label='chemical vs manufacturing gap');ax.axhline(0,color='black',lw=.6);ax.legend();ax.set_title('Fixed tanh chemical-input factor');ax.grid(alpha=.2);store('03_factor')
    ax=oos[['actual','mean','persistence','macro','full']].plot(figsize=(11,5),title='Purged 6-month ahead pharma output forecasts')
    ax.set_ylabel('8-month forward log growth (pp)');ax.grid(alpha=.2);store('04_oos_forecasts')
    e=(oos.actual-oos.macro)**2-(oos.actual-oos.full)**2
    fig,ax=plt.subplots(figsize=(11,4));ax.plot(e.index,e.cumsum());ax.axhline(0,color='black',lw=.5);ax.set_title('Cumulative paired squared-loss advantage (macro minus full)');ax.grid(alpha=.2);store('05_loss_differential')
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(placebo,bins=35,alpha=.7);ax.axvline(improvement(oos),color='red',lw=2,label='observed');ax.set_title('12-month block-alignment placebo (exploratory, not exact p)');ax.legend();store('06_placebo')
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(boot,bins=35,alpha=.7);ax.axvline(0,color='black',lw=1);ax.set_title('12-month circular moving-block bootstrap: RMSE improvement');store('07_bootstrap')
    fig,ax=plt.subplots(figsize=(9,4));ax.scatter(sens.chemical_weight,sens.rmse_improvement_pp,c=sens.manufacturing_weight,s=8,alpha=.5);ax.axhline(0,color='black',lw=1);ax.set_title('1,000 exposure-weight perturbations (analyst priors)');ax.set_xlabel('chemical weight');ax.set_ylabel('RMSE improvement (pp)');store('08_exposure_sensitivity')
    return figs


def run(write=True, fast=False):
    raw=read_data();panel=make_panel(raw);oos=walk_forward(panel)
    assert len(oos)>=50
    metrics={'study':'Basic Chemical to Pharma Output, U.S. 2026-10-26',
             'source_snapshot':'FRED G.17 current revised data collected 2026-10-26; NOT archival publication vintages',
             'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
             'n_months':len(raw),'start':str(raw.index.min().date()),'end':str(raw.index.max().date()),
             'oos_n':len(oos),'oos_start':str(oos.index.min().date()),'oos_end':str(oos.index.max().date()),
             'horizon_months':6,'feature_lag_months':2,'label_purge_months':8,
             'metrics':score(oos),'rmse_improvement_macro_minus_full_pp':improvement(oos),
             'regimes':summarize_regimes(oos),'robustness':{}}
    for h in (3,9):
        x=walk_forward(make_panel(raw,horizon=h),horizon=h)
        metrics['robustness'][f'horizon_{h}m']={'n':len(x),'delta_rmse':improvement(x),'scores':score(x)}
    p3=walk_forward(make_panel(raw,release_lag=3),lag=3)
    metrics['robustness']['lag_3m']={'n':len(p3),'delta_rmse':improvement(p3),'scores':score(p3)}
    stale=walk_forward(make_panel(raw,stale=12))
    metrics['robustness']['stale_chemical_12m']={'n':len(stale),'delta_rmse':improvement(stale),'scores':score(stale)}
    rolling=walk_forward(panel,train_window=72)
    metrics['robustness']['rolling_72m']={'n':len(rolling),'delta_rmse':improvement(rolling),'scores':score(rolling)}
    nperm=20 if fast else 1000
    nsens=20 if fast else 1000
    nboot=50 if fast else 2000
    placebo,tail=block_placebo(panel,improvement(oos),draws=nperm)
    boot=block_bootstrap(oos,draws=nboot)
    sens=exposure_sensitivity(raw,draws=nsens)
    metrics['placebo']={'method':'Exploratory 12m block alignment shuffle, not an exact null p-value',
                        'draws':nperm,'one_sided_tail_fraction':tail,'mean_delta':float(placebo.mean())}
    metrics['bootstrap']={'draws':nboot,'block_months':12,'ci95':list(map(float,np.quantile(boot,[.025,.975])))}
    metrics['exposure_sensitivity']={'draws':nsens,'fraction_positive':float((sens.rmse_improvement_pp>0).mean()),
                                     'ci95':list(map(float,np.quantile(sens.rmse_improvement_pp,[.025,.975])))}
    if write:
        (ROOT/'results').mkdir(exist_ok=True)
        oos.to_csv(ROOT/'results'/'oos_forecasts.csv')
        panel.to_csv(ROOT/'data'/'derived_panel.csv')
        pd.DataFrame({'delta_rmse':placebo}).to_csv(ROOT/'results'/'placebo_1000.csv',index=False)
        pd.DataFrame({'delta_rmse':boot}).to_csv(ROOT/'results'/'bootstrap_2000.csv',index=False)
        sens.to_csv(ROOT/'results'/'exposure_1000.csv',index=False)
        figs=save_figures(raw,panel,oos,placebo,boot,sens)
        metrics['figures']=figs
        (ROOT/'results'/'metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False))
    return metrics,raw,panel,oos,placebo,boot,sens

if __name__=='__main__':
    m,*_=run()
    print(json.dumps({k:v for k,v in m.items() if k in ('oos_n','metrics','rmse_improvement_macro_minus_full_pp','placebo','bootstrap','exposure_sensitivity','robustness')},indent=2))
