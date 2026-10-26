"""Retrospective G.17 paper-input -> printing output forecast falsification.

Never infer historical release-vintage validity from the latest-revised snapshot.
No security-return or issuer-fundamental claims are made.
"""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = ROOT/'data'; OUT = ROOT/'results'; FIG = ROOT/'figures'
SOURCE = DATA/'fed_g17_transcribed_rows_2026-10-16.txt'
SERIES = {'G322':'paper_ip','G323':'printing_ip','B00004':'manufacturing_ip'}


def read_official_transcription(path=SOURCE):
    rows = []
    for raw in Path(path).read_text().splitlines():
        if not raw.strip() or raw.startswith('#'): continue
        cols = raw.split()
        code, year, vals = cols[0], int(cols[1]), cols[2:]
        if code not in SERIES or not (2010 <= year <= 2026): raise ValueError('Unexpected source code or year')
        if len(vals) != (9 if year == 2026 else 12): raise ValueError(f'Wrong month count: {code} {year}')
        for m,v in enumerate(vals, 1):
            rows.append({'date':f'{year}-{m:02d}-01','series':code,'value':float(v)})
    long = pd.DataFrame(rows)
    if long.duplicated(['date','series']).any(): raise ValueError('Duplicate observations')
    if len(long)!=603: raise ValueError(f'Expected 603 observations, got {len(long)}')
    wide = long.pivot(index='date', columns='series',values='value').rename(columns=SERIES)
    wide.index = pd.to_datetime(wide.index)
    wide.index.name = 'date'
    wide=wide.sort_index()
    if len(wide)!=201 or wide.isna().any().any() or (wide<=0).any().any():
        raise ValueError('Incomplete/nonpositive source panel')
    checks={'2010-01-01':(99.9533,102.8123,91.0661),
            '2020-04-01':(95.7202,69.2298,79.7713),
            '2026-09-01':(78.3155,74.0432,98.4387)}
    for dt, expected in checks.items():
        got=wide.loc[dt,['paper_ip','printing_ip','manufacturing_ip']].to_numpy()
        if not np.allclose(got,expected,rtol=0,atol=1e-6):
            raise ValueError(f'Official row spot-check mismatch: {dt} {got} vs {expected}')
    return wide


def make_panel(raw, h=3, lag=1, paper_weight=1.0):
    """Forecast origin t: inputs observed at t-lag; y is printing YoY at t+h.

    `lag` is a conservative publication buffer, NOT a historical-vintage guarantee.
    """
    if h<1 or lag<1: raise ValueError('h and lag must be >= 1')
    yprint=100*np.log(raw['printing_ip']/raw['printing_ip'].shift(12))
    ypaper=100*np.log(raw['paper_ip']/raw['paper_ip'].shift(12))
    ymfg=100*np.log(raw['manufacturing_ip']/raw['manufacturing_ip'].shift(12))
    panel=pd.DataFrame(index=raw.index)
    panel['print_momentum']=yprint.shift(lag)
    panel['mfg_growth']=ymfg.shift(lag)
    panel['paper_growth']=ypaper.shift(lag)
    panel['factor']=paper_weight*panel['paper_growth']-panel['mfg_growth']
    panel['target']=yprint.shift(-h)
    panel['outcome_date']=pd.Series(raw.index,index=raw.index).shift(-h)
    panel['latest_input_date']=pd.Series(raw.index,index=raw.index).shift(lag)
    panel['release_vintage']='UNKNOWN (latest-revised 2026-10-16 snapshot)'
    return panel.dropna(subset=['print_momentum','mfg_growth','paper_growth','factor','target'])


def ridge_predict(X, y, xt, alpha=8.0):
    """Intercept unpenalized; training-only feature scaling, no tuning on test."""
    X=np.asarray(X,float);y=np.asarray(y,float);xt=np.asarray(xt,float)
    mu=X.mean(axis=0); sd=X.std(axis=0,ddof=0);sd[sd<1e-8]=1.
    Z=(X-mu)/sd; zt=(xt-mu)/sd
    ym=y.mean()
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(Z.shape[1]),Z.T@(y-ym))
    return float(ym+zt@beta)


def walk_forward(panel, horizon=3, lag=1, start='2017-01-01', factor_override=None):
    """Purged expanding-window forecasts; labels available only after h+1 months."""
    p=panel.copy()
    if factor_override is not None:
        if len(factor_override)!=len(p):raise ValueError('Factor override length')
        p['factor']=np.asarray(factor_override,float)
    out=[]
    for t in p.index:
        if t<pd.Timestamp(start): continue
        # Outcome y_j at j+h released no earlier than j+h+1. At t, inputs end t-lag.
        # Conservatively require j+h+1 <= t-lag.
        cutoff=t-pd.DateOffset(months=horizon+1+lag)
        train=p.loc[p.index<=cutoff]
        if len(train)<36:continue
        y=train['target'].to_numpy(); actual=float(p.loc[t,'target'])
        ctr=['print_momentum','mfg_growth'];full=ctr+['factor']
        out.append({'origin':t,'outcome_date':p.loc[t,'outcome_date'],
                    'n_train':len(train),'last_train_origin':train.index.max(),
                    'last_train_outcome_date':train['outcome_date'].max(),
                    'actual':actual,'mean':float(y.mean()),
                    'persistence':float(p.loc[t,'print_momentum']),
                    'control':ridge_predict(train[ctr],y,p.loc[t,ctr].to_numpy()),
                    'full':ridge_predict(train[full],y,p.loc[t,full].to_numpy()),
                    'paper_only':ridge_predict(train[['factor']],y,p.loc[t,['factor']].to_numpy())})
    result=pd.DataFrame(out)
    if result.empty:raise ValueError('No OOS origins')
    result['origin']=pd.to_datetime(result['origin'])
    result['outcome_date']=pd.to_datetime(result['outcome_date'])
    result['last_train_origin']=pd.to_datetime(result['last_train_origin'])
    result['last_train_outcome_date']=pd.to_datetime(result['last_train_outcome_date'])
    if not (result['last_train_outcome_date'] < result['origin']).all():
        raise AssertionError('Training label availability leak')
    return result


def metrics(oos):
    a=oos['actual'].to_numpy();out={}
    for col in ['mean','persistence','control','full','paper_only']:
        p=oos[col].to_numpy();out[col]={'n':len(a),'rmse':float(np.sqrt(np.mean((a-p)**2))),
                                         'mae':float(np.mean(np.abs(a-p)))}
    return out


def moving_block_bootstrap(oos, draws=2000, block=12, seed=26026):
    """Paired moving-block resampling of origin-wise squared errors; overlap-aware descriptive CI."""
    rng=np.random.default_rng(seed); n=len(oos)
    a=oos.actual.to_numpy();c=oos.control.to_numpy();f=oos.full.to_numpy()
    d=[]
    for _ in range(draws):
        starts=rng.integers(0,n,size=int(np.ceil(n/block)))
        idx=np.concatenate([(s+np.arange(block))%n for s in starts])[:n]
        d.append(float(np.sqrt(np.mean((a[idx]-c[idx])**2))-np.sqrt(np.mean((a[idx]-f[idx])**2))))
    return np.asarray(d)


def block_permutation_factor(panel, rng, block=12):
    """Block-order shuffle; exploratory, not an exact exchangeability-based p-value."""
    x=panel['factor'].to_numpy(); blocks=[x[i:i+block] for i in range(0,len(x),block)]
    order=rng.permutation(len(blocks))
    return np.concatenate([blocks[i] for i in order])[:len(x)] if all(len(b)==block for b in blocks) else _shuffle_unequal(blocks,rng,len(x))

def _shuffle_unequal(blocks,rng,n):
    # Shifted blocks with unequal tail lengths: circular moving-block draw preserving length.
    x=np.concatenate(blocks); starts=rng.integers(0,n,size=int(np.ceil(n/12)))
    return np.concatenate([x[(s+np.arange(12))%n] for s in starts])[:n]


def fast_full_predictions(panel, factor_override, h=3, lag=1, start='2017-01-01'):
    """Array-only version of full-model OOS predictions, exactly matching walk_forward."""
    idx=panel.index
    X=np.column_stack([panel['print_momentum'].to_numpy(),panel['mfg_growth'].to_numpy(),np.asarray(factor_override,float)])
    y=panel['target'].to_numpy()
    out=[]
    for i,t in enumerate(idx):
        if t<pd.Timestamp(start): continue
        cutoff=t-pd.DateOffset(months=h+1+lag)
        n=int(idx.searchsorted(cutoff,side='right'))
        if n<36: continue
        out.append(ridge_predict(X[:n],y[:n],X[i]))
    return np.asarray(out)


def run_placebo(panel, oos, observed_delta, draws=1000, seed=1127):
    rng=np.random.default_rng(seed); values=[]
    actual=oos.actual.to_numpy();control=oos.control.to_numpy()
    c_rmse=float(np.sqrt(np.mean((actual-control)**2)))
    for _ in range(draws):
        shuffled=block_permutation_factor(panel,rng)
        preds=fast_full_predictions(panel,shuffled)
        values.append(c_rmse-float(np.sqrt(np.mean((actual-preds)**2))))
    arr=np.asarray(values)
    tail=float((1+(arr>=observed_delta).sum())/(len(arr)+1))
    return arr,tail

def robustness(raw, baseline_oos):
    rows=[]
    for h in (1,3,6):
        for lag in (1,2,3):
            o=walk_forward(make_panel(raw,h=h,lag=lag),horizon=h,lag=lag)
            m=metrics(o);rows.append({'horizon_months':h,'publication_buffer_months':lag,'n':len(o),
                                       'rmse_control':m['control']['rmse'],'rmse_full':m['full']['rmse'],
                                       'delta_control_minus_full':m['control']['rmse']-m['full']['rmse']})
    for label, mask in [('exclude_2020',baseline_oos.origin.dt.year!=2020),
                        ('pre_2020',baseline_oos.origin.dt.year<2020),
                        ('post_2021',baseline_oos.origin.dt.year>=2022)]:
        sub=baseline_oos[mask]
        if len(sub)>8:
            m=metrics(sub);rows.append({'horizon_months':3,'publication_buffer_months':1,'regime':label,
                                        'n':len(sub),'rmse_control':m['control']['rmse'],'rmse_full':m['full']['rmse'],
                                        'delta_control_minus_full':m['control']['rmse']-m['full']['rmse']})
    return pd.DataFrame(rows)


def save_figures(raw,panel,oos,score,bootstrap,placebo,exposure,robust):
    plt.rcParams.update({'font.size':10,'figure.figsize':(9,4.3)})
    def save(name):
        plt.tight_layout();plt.savefig(FIG/name,format='svg',bbox_inches='tight');plt.close()
    raw.plot(title='G.17 seasonally adjusted output indices (2017=100)',lw=1.6)
    plt.ylabel('Index');save('01_output_levels.svg')
    yoy=100*np.log(raw/raw.shift(12))
    yoy.plot(title='Year-over-year industrial production growth (log pp)',lw=1.1)
    plt.axhline(0,color='gray',lw=.6);plt.ylabel('log percentage points');save('02_growth_rates.svg')
    panel[['factor','print_momentum']].plot(title='Predefined paper minus manufacturing signal and printing persistence')
    plt.ylabel('log percentage points');save('03_factor_and_momentum.svg')
    plt.plot(oos.origin,oos.actual,label='actual',lw=1.6)
    plt.plot(oos.origin,oos.control,label='macro control',alpha=.8)
    plt.plot(oos.origin,oos.full,label='paper augmented',alpha=.8)
    plt.title('Purged expanding-window 3-month-ahead OOS forecasts');plt.legend();plt.ylabel('Printing YoY growth (log pp)');save('04_oos_forecasts.svg')
    score.sort_values('rmse').plot.bar(x='model',y='rmse',legend=False,title='OOS RMSE, identical origins')
    plt.ylabel('RMSE (log pp)');save('05_baseline_scorecard.svg')
    d=(oos.actual-oos.control)**2-(oos.actual-oos.full)**2
    plt.plot(oos.origin,np.cumsum(d),lw=1.7);plt.axhline(0,color='gray',lw=.6)
    plt.title('Cumulative squared-error advantage: control minus full');plt.ylabel('Cumulative difference');save('06_cumulative_loss.svg')
    plt.hist(placebo,bins=32);plt.axvline(float(score.set_index('model').loc['control','rmse']-score.set_index('model').loc['full','rmse']),color='black',lw=1.5)
    plt.title('Exploratory block-shuffle placebo distribution');plt.xlabel('RMSE control − full (log pp)');save('07_placebo.svg')
    plt.hist(bootstrap,bins=32);plt.axvline(0,color='black',lw=1.5)
    plt.title('Paired moving-block bootstrap: RMSE improvement');plt.xlabel('RMSE control − full (log pp)');save('08_bootstrap.svg')
    plt.scatter(exposure.weight,exposure.delta_control_minus_full,s=10,alpha=.5)
    plt.axhline(0,color='black',lw=.8);plt.title('Paper-weight perturbation (re-fit OOS)')
    plt.xlabel('Paper exposure weight');plt.ylabel('RMSE control − full');save('09_exposure.svg')
    rr=robust[robust['regime'].isna()] if 'regime' in robust else robust
    rr.plot.bar(x='horizon_months',y='delta_control_minus_full',legend=False,title='Horizon / release-buffer robustness (3 buffers per horizon)')
    plt.axhline(0,color='black',lw=.7);plt.ylabel('RMSE control − full');save('10_robustness.svg')


def main():
    for folder in [DATA,OUT,FIG]:folder.mkdir(exist_ok=True)
    raw=read_official_transcription();raw.to_csv(DATA/'frozen_g17_2010_2026.csv',float_format='%.4f')
    panel=make_panel(raw);panel.to_csv(DATA/'derived_formation_panel.csv')
    oos=walk_forward(panel);oos.to_csv(OUT/'walk_forward_oos.csv',index=False)
    m=metrics(oos)
    score=pd.DataFrame([{'model':k,**v} for k,v in m.items()]);score.to_csv(OUT/'scorecard.csv',index=False)
    delta=m['control']['rmse']-m['full']['rmse']
    boot=moving_block_bootstrap(oos);pd.DataFrame({'delta_rmse':boot}).to_csv(OUT/'bootstrap_2000.csv',index=False)
    placebo,tail=run_placebo(panel,oos,delta);pd.DataFrame({'delta_rmse':placebo}).to_csv(OUT/'block_placebo_1000.csv',index=False)
    # Exposure is a proxy coefficient on sector-level signal, not an issuer exposure.
    rng=np.random.default_rng(6601); exposure=[]
    for weight in rng.uniform(.7,1.3,200):
        preds=fast_full_predictions(panel,weight*panel['paper_growth'].to_numpy()-panel['mfg_growth'].to_numpy())
        alt_delta=m['control']['rmse']-float(np.sqrt(np.mean((oos.actual.to_numpy()-preds)**2)))
        exposure.append({'weight':weight,'delta_control_minus_full':alt_delta})
    exposure=pd.DataFrame(exposure);exposure.to_csv(OUT/'exposure_perturbation_200.csv',index=False)
    rob=robustness(raw,oos);rob.to_csv(OUT/'robustness.csv',index=False)
    lo=[]
    for year in sorted(oos.origin.dt.year.unique()):
        sub=oos[oos.origin.dt.year!=year];mm=metrics(sub)
        lo.append({'excluded_year':int(year),'n':len(sub),'delta_control_minus_full':mm['control']['rmse']-mm['full']['rmse']})
    pd.DataFrame(lo).to_csv(OUT/'leave_one_year_out.csv',index=False)
    # Ablation: full minus paper = control, and paper only is scored in primary scorecard.
    save_figures(raw,panel,oos,score,boot,placebo,exposure,rob)
    sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    result={'as_of':'2026-10-26','source_release_date':'2026-10-16','source_file_sha256':sha,
            'source_status':'manually transcribed official G.17 latest-revised release, not historical vintages',
            'observations':len(raw),'formation_panel':len(panel),'oos_n':len(oos),
            'oos_start':str(oos.origin.min().date()),'oos_end':str(oos.origin.max().date()),
            'horizon_months':3,'publication_buffer_months':1,'training_target_purge_months':5,
            'scorecard':m,'delta_control_minus_full':delta,
            'bootstrap_draws':len(boot),'bootstrap_ci95':np.quantile(boot,[.025,.975]).tolist(),
            'placebo_draws':len(placebo),'exploratory_block_shuffle_tail_fraction':tail,
            'exposure_draws':len(exposure),'exposure_positive_share':float((exposure.delta_control_minus_full>0).mean()),
            'leave_one_year_out_range':list(map(float,[min(x['delta_control_minus_full'] for x in lo),max(x['delta_control_minus_full'] for x in lo)])),
            'historical_pit_verified':False,'firm_fundamentals_tested':False,'equity_alpha_tested':False,
            'notes':'Retrospective macro falsification only; latest-revised official release; source rows manually transcribed.'}
    (OUT/'metrics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (OUT/'execution.log').write_text(f'PASS analysis; {len(raw)} months; {len(oos)} OOS origins; 1000 placebo, 2000 bootstrap, 200 exposure.\n')
    print(json.dumps(result,indent=2));return result

if __name__=='__main__':main()
