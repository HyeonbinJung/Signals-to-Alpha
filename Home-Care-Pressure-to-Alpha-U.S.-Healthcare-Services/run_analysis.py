"""Home-health-to-residential-care retrospective macro factor pilot.
All input observations are frozen revised FRED/BLS values, NOT PIT vintages.
No equity alpha, returns, or causal inference claimed.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data/fred_ces_2010_2026_snapshot.csv'
FEATURES=['nursing_yoy','payroll_yoy','hospital_yoy']
SEED=20261026


def load_data(path=DATA):
    d=pd.read_csv(path,parse_dates=['date']).set_index('date').sort_index()
    assert list(d.columns)==['home','hospital','nursing','ambulatory','payroll']
    assert d.index.is_unique and d.index.is_monotonic_increasing
    assert len(d)==201 and d.index[0]==pd.Timestamp('2010-01-01') and d.index[-1]==pd.Timestamp('2026-09-01')
    assert (d>0).all().all() and d.notna().all().all()
    assert d.index.to_period('M').equals(pd.period_range('2010-01','2026-09',freq='M'))
    assert np.isclose(d.loc['2026-09-01','nursing'],3489.4)
    return d


def make_panel(raw, horizon=6, lag=2, home_weight=1.0):
    """Formation month t: predictors from t-lag, target nursing YoY at t+horizon.
    Availability buffer is assumed, not actual historical publication-vintage proof.
    """
    if not 0<=home_weight<=1: raise ValueError('home_weight outside [0,1]')
    if horizon<1 or lag<1: raise ValueError('horizon and lag must be positive')
    out=pd.DataFrame(index=raw.index)
    for col in raw.columns:
        out[col+'_yoy']=100*np.log(raw[col].shift(lag)/raw[col].shift(lag+12))
    spread=(home_weight*out['home_yoy']+(1-home_weight)*out['ambulatory_yoy']-out['hospital_yoy'])
    out['factor']=np.tanh(spread/5.0)
    out['home_only']=np.tanh(out['home_yoy']/5.0)
    out['alternative']=np.tanh((out['ambulatory_yoy']-out['hospital_yoy'])/5.0)
    out['target']=100*np.log(raw['nursing'].shift(-horizon)/raw['nursing'].shift(12-horizon))
    out=out.dropna()
    out.index.name='formation_date'
    return out


def ridge_predict(xtrain,ytrain,xtest,alpha=10):
    xtrain=np.asarray(xtrain,dtype=float); xtest=np.asarray(xtest,dtype=float)
    if xtrain.ndim==1:xtrain=xtrain[:,None]
    if xtest.ndim==1:xtest=xtest.reshape(1,-1)
    mu=xtrain.mean(axis=0); sd=xtrain.std(axis=0); sd=np.where(sd<1e-12,1,sd)
    x=(xtrain-mu)/sd; z=(xtest-mu)/sd
    yc=ytrain.mean(); a=x.T@x+alpha*np.eye(x.shape[1]); b=x.T@(ytrain-yc)
    return float(yc+z[0]@np.linalg.solve(a,b))


def walk_forward(panel,horizon=6,rolling=None,start='2018-01-01',feature_override=None,model_subset=None):
    p=panel.copy()
    if feature_override is not None:
        assert len(feature_override)==len(p)
        p['factor']=feature_override
    dates=p.index
    records=[]
    for t in dates:
        if t<pd.Timestamp(start): continue
        # A label for formation u uses an outcome observation at u+h, released
        # no sooner than u+h+1. Strictly exclude later labels at origin t.
        eligible=(dates<=t-pd.DateOffset(months=horizon+1))
        train=p.loc[eligible]
        if rolling:train=train.tail(rolling)
        if len(train)<60:continue
        row=p.loc[t]
        preds={'mean':float(train.target.mean())}
        models={
            'persistence':['nursing_yoy'],
            'macro':FEATURES,
            'full':FEATURES+['factor'],
            'factor_only':['factor'],
            'home_only':FEATURES+['home_only'],
            'alt_ambulatory':FEATURES+['alternative'],
            'no_payroll':['nursing_yoy','hospital_yoy','factor'],
            'no_hospital':['nursing_yoy','payroll_yoy','factor']
        }
        if model_subset is not None: models={k:v for k,v in models.items() if k in model_subset}
        for name,cols in models.items():
            preds[name]=ridge_predict(train[cols].to_numpy(),train.target.to_numpy(),row[cols].to_numpy().reshape(1,-1))
        records.append({'date':t,'actual':float(row.target),'factor':float(row.factor),
                        'train_n':len(train),**preds})
    return pd.DataFrame(records).set_index('date')


def fast_full_predictions(panel,horizon=6,start='2018-01-01'):
    """Vectorized-array walk-forward refit of the full model, used for large falsification grids."""
    y=panel.target.to_numpy(dtype=float)
    x=panel[FEATURES+['factor']].to_numpy(dtype=float)
    dates=panel.index
    start_i=int(np.searchsorted(dates.values,np.datetime64(start)))
    out=[]
    for i in range(start_i,len(panel)):
        end=i-horizon
        if end<60: continue
        train=x[:end];yt=y[:end]
        mu=train.mean(axis=0);sd=train.std(axis=0);sd=np.where(sd<1e-12,1,sd)
        z=(train-mu)/sd
        coeff=np.linalg.solve(z.T@z+10*np.eye(4),z.T@(yt-yt.mean()))
        out.append(float(yt.mean()+((x[i]-mu)/sd)@coeff))
    return np.array(out)

def score(oos,models=None):
    if models is None:models=['mean','persistence','macro','full','factor_only','home_only','alt_ambulatory','no_payroll','no_hospital']
    return {m:{'rmse':float(np.sqrt(np.mean((oos.actual-oos[m])**2))),
               'mae':float(np.mean(np.abs(oos.actual-oos[m]))),'n':len(oos)} for m in models}


def moving_block_bootstrap(oos,draws=2000,block=12,seed=SEED):
    rng=np.random.default_rng(seed); n=len(oos); vals=oos[['actual','macro','full','persistence']].to_numpy()
    diffs=[]; persist=[]
    for _ in range(draws):
        starts=rng.integers(0,n-block+1,size=int(np.ceil(n/block)))
        ind=np.concatenate([np.arange(s,s+block) for s in starts])[:n]
        a,b,c,d=vals[ind].T
        diffs.append(float(np.sqrt(np.mean((a-b)**2))-np.sqrt(np.mean((a-c)**2))))
        persist.append(float(np.sqrt(np.mean((a-d)**2))-np.sqrt(np.mean((a-c)**2))))
    return {'macro_minus_full_ci95':np.quantile(diffs,[.025,.975]).tolist(),
            'persistence_minus_full_ci95':np.quantile(persist,[.025,.975]).tolist(),
            'draws':draws,'block_months':block}


def shuffle_blocks(series,block,rng):
    arr=np.asarray(series); groups=[arr[i:i+block] for i in range(0,len(arr),block)]
    perm=rng.permutation(len(groups));return np.concatenate([groups[i] for i in perm])


def block_placebo(panel,oos,draws=1000,block=12,seed=SEED):
    rng=np.random.default_rng(seed+1); base=score(oos); observed=base['macro']['rmse']-base['full']['rmse']
    null=[]
    for i in range(draws):
        shuffled=shuffle_blocks(panel.factor.to_numpy(),block,rng)
        trial=panel.copy();trial['factor']=shuffled
        predictions=fast_full_predictions(trial)
        assert len(predictions)==len(oos)
        null.append(float(base['macro']['rmse']-np.sqrt(np.mean((oos.actual.to_numpy()-predictions)**2))))
    return {'observed_improvement':observed,'tail_fraction_exploratory':float((np.sum(np.asarray(null)>=observed)+1)/(draws+1)),
            'draws':draws,'block_months':block,'null':null}


def exposure_sensitivity(raw,macro_rmse,draws=1000,seed=SEED):
    rng=np.random.default_rng(seed+2); out=[]
    for _ in range(draws):
        weight=float(rng.uniform(.5,1))
        trial=make_panel(raw,home_weight=weight)
        preds=fast_full_predictions(trial)
        out.append({'home_weight':weight,'full_rmse':float(np.sqrt(np.mean((trial.loc[trial.index>='2018-01-01','target'].to_numpy()-preds)**2)))})
    df=pd.DataFrame(out);df['delta_rmse_macro_minus_full']=macro_rmse-df['full_rmse'];return df


def period_score(oos,mask):
    q=oos.loc[mask];return {'n':len(q),'macro_rmse':score(q,['macro'])['macro']['rmse'],
                             'full_rmse':score(q,['full'])['full']['rmse'],
                             'persistence_rmse':score(q,['persistence'])['persistence']['rmse']}


def create_figures(raw,panel,oos,placebo,exposure,robust):
    figdir=ROOT/'figures';figdir.mkdir(exist_ok=True)
    plt.rcParams.update({'figure.dpi':75,'axes.grid':True,'grid.alpha':.22,'font.size':10})
    fig,ax=plt.subplots(figsize=(11,4)); (raw[['home','hospital','nursing','ambulatory']]/raw[['home','hospital','nursing','ambulatory']].iloc[0]*100).plot(ax=ax)
    ax.set_title('U.S. care-setting employment index (Jan 2010 = 100)');ax.set_ylabel('Index');fig.tight_layout();fig.savefig(figdir/'01_care_setting_levels.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4));panel[['home_yoy','hospital_yoy','nursing_yoy']].plot(ax=ax)
    ax.axhline(0,color='black',lw=.7);ax.set_title('Observed YoY employment growth by care setting');ax.set_ylabel('Log YoY, pp');fig.tight_layout();fig.savefig(figdir/'02_care_setting_growth.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4));panel.factor.plot(ax=ax);ax.axhline(0,color='black',lw=.7);ax.set_title('Home-health minus hospital growth: fixed tanh factor');fig.tight_layout();fig.savefig(figdir/'03_factor.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4));oos[['actual','persistence','macro','full']].plot(ax=ax,lw=1.3)
    ax.set_title('Purged expanding-window OOS nursing growth forecasts');ax.set_ylabel('Log YoY, pp');fig.tight_layout();fig.savefig(figdir/'04_oos_forecasts.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4));((oos.actual-oos.macro)**2-(oos.actual-oos.full)**2).plot(ax=ax)
    ax.axhline(0,color='black',lw=.8);ax.set_title('Paired squared-loss advantage (macro minus full)');ax.set_ylabel('pp²');fig.tight_layout();fig.savefig(figdir/'05_loss_difference.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.hist(placebo['null'],bins=35);ax.axvline(placebo['observed_improvement'],color='red',lw=2,label='observed');ax.legend()
    ax.set_title('Exploratory 12-month block-shuffle refits (not exact p-values)');ax.set_xlabel('RMSE improvement, pp');fig.tight_layout();fig.savefig(figdir/'06_block_placebo.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4));ax.scatter(exposure.home_weight,exposure.delta_rmse_macro_minus_full,s=5,alpha=.3)
    ax.axhline(0,color='black',lw=.8);ax.set_title('Exposure-definition sensitivity: home vs ambulatory');ax.set_xlabel('Home-care growth weight');ax.set_ylabel('Macro minus full RMSE, pp');fig.tight_layout();fig.savefig(figdir/'07_exposure_sensitivity.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4));names=list(robust);vals=[robust[n]['macro_rmse']-robust[n]['full_rmse'] for n in names];ax.barh(names,vals);ax.axvline(0,color='black',lw=.8)
    ax.set_title('Regime and specification sensitivity (not independent trials)');ax.set_xlabel('Macro minus full RMSE, pp');fig.tight_layout();fig.savefig(figdir/'08_robustness.png');plt.close(fig)


def run(draws=1000,bootstrap=2000,write=True):
    raw=load_data();panel=make_panel(raw);oos=walk_forward(panel)
    primary=score(oos)
    placebo=block_placebo(panel,oos,draws=draws)
    exposure=exposure_sensitivity(raw,primary['macro']['rmse'],draws=draws)
    boot=moving_block_bootstrap(oos,draws=bootstrap)
    robust={
        'pre_2020':period_score(oos,oos.index<'2020-01-01'),
        '2020_onward':period_score(oos,oos.index>='2020-01-01'),
        'excluding_2020_2021':period_score(oos,~oos.index.year.isin([2020,2021])),
    }
    for h in [3,9]:
        trial=walk_forward(make_panel(raw,horizon=h),horizon=h)
        robust[f'horizon_{h}m']=period_score(trial,trial.index==trial.index)
    for lag in [3,4]:
        trial=walk_forward(make_panel(raw,lag=lag))
        robust[f'lag_{lag}m']=period_score(trial,trial.index==trial.index)
    rolling=walk_forward(panel,rolling=84)
    robust['rolling_84m']=period_score(rolling,rolling.index==rolling.index)
    leave_year=[]
    for year in sorted(oos.index.year.unique()):
        q=oos.loc[oos.index.year!=year];s=score(q,['macro','full'])
        leave_year.append({'excluded_year':int(year),'n':len(q),'macro_minus_full_rmse':s['macro']['rmse']-s['full']['rmse']})
    metrics={'source_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),
             'raw_observations':len(raw),'panel_observations':len(panel),
             'oos_n':len(oos),'oos_first':str(oos.index[0].date()),'oos_last':str(oos.index[-1].date()),
             'scorecard':primary,'bootstrap':boot,
             'block_placebo':{k:v for k,v in placebo.items() if k!='null'},
             'exposure_sensitivity':{'n':len(exposure),'median_delta_rmse':float(exposure.delta_rmse_macro_minus_full.median()),
                                     'fraction_positive':float((exposure.delta_rmse_macro_minus_full>0).mean())},
             'robustness':robust,'leave_one_year_out':leave_year,
             'PIT_verified':False,'equity_alpha_established':False,
             'target':'Nursing/residential care employment YoY at formation t+6; revised-data retrospective',
             'data_as_of':'2026-10-26','source_latest_release':'2026-10-02'}
    if write:
        res=ROOT/'results';res.mkdir(exist_ok=True)
        panel.to_csv(ROOT/'data/derived_factor_panel.csv')
        oos.to_csv(res/'walk_forward_oos.csv')
        pd.DataFrame(primary).T.to_csv(res/'scorecard.csv')
        exposure.to_csv(res/'exposure_sensitivity.csv',index=False)
        pd.DataFrame({'block_shuffle_rmse_improvement':placebo['null']}).to_csv(res/'block_placebo_null.csv',index=False)
        pd.DataFrame(robust).T.to_csv(res/'robustness.csv')
        pd.DataFrame(leave_year).to_csv(res/'leave_one_year_out.csv',index=False)
        (res/'metrics.json').write_text(json.dumps(metrics,indent=2,allow_nan=False)+'\n')
        create_figures(raw,panel,oos,placebo,exposure,robust)
        (res/'run_log.txt').write_text('python run_analysis.py\nPASS: 1000 block-shuffle refits, 1000 exposure perturbations, 2000 bootstrap draws; figures generated.\nNOT PIT; NOT equity alpha.\n')
    return metrics,raw,panel,oos,placebo,exposure


if __name__=='__main__':
    m,*_=run()
    print(json.dumps({k:m[k] for k in ['raw_observations','panel_observations','oos_n','oos_first','oos_last','scorecard','bootstrap','block_placebo','exposure_sensitivity']},indent=2))
