"""Retrospective U.S. broiler-production factor falsification; fixed, non-vintage plotnine/USDA snapshot.

All formation features use monthly values at most origin-2. Every training label must
have its forecast target month at least two months before the forecast origin.
No claim of historically archived release vintages or tradable returns is made.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
RAW = HERE/'data/raw_plotnine_meat_2023_snapshot.csv'
RESULTS = HERE/'results'
FIGURES = HERE/'figures'
LAG = 2
HORIZON = 3
OOS_START = '2010-01-01'
MIN_TRAIN = 240
ALPHA = 10.0
SEED = 20261028
CONTROL = ['broiler_yoy_lag2', 'broiler_yoy_lag5', 'broiler_mom3_lag2', 'red_yoy_lag2']
AR = ['broiler_yoy_lag2', 'broiler_yoy_lag5', 'broiler_mom3_lag2']
MODELS = ['historical_mean','persistence','momentum','ar_ridge','macro_control','factor_only','augmented']


def load_raw():
    df = pd.read_csv(RAW, parse_dates=['date']).sort_values('date').reset_index(drop=True)
    expected=['date','beef','veal','pork','lamb_and_mutton','broilers','other_chicken','turkey']
    assert df.columns.tolist()==expected, 'Source schema changed'
    assert len(df)==960 and df.date.min()==pd.Timestamp('1944-01-01') and df.date.max()==pd.Timestamp('2023-12-01'), 'Unexpected data window'
    assert df.date.is_unique and df.date.diff().dropna().dt.days.between(28,31).all(), 'Date continuity failure'
    assert df[['beef','pork','broilers','turkey']].min().min()>0, 'Nonpositive production'
    assert df.broilers.notna().sum()==768 and df.turkey.notna().sum()==768, 'Poultry availability changed'
    return df


def make_panel(raw, horizon=HORIZON, lag=LAG, beef_weight=.5, pork_weight=.5, turkey_weight=1.0):
    assert lag>=1 and horizon>=1 and 0<=beef_weight<=1 and 0<=pork_weight<=1
    assert abs(beef_weight+pork_weight-1)<1e-8
    df=raw.copy()
    for c in ['beef','pork','broilers','turkey']:
        df[c+'_yoy'] = 100*np.log(df[c]/df[c].shift(12))
        df[c+'_mom3'] = 100*np.log(df[c]/df[c].shift(3))
    df['red_yoy']=.5*(df.beef_yoy+df.pork_yoy)
    for c in ['broilers_yoy','broilers_mom3','beef_yoy','pork_yoy','turkey_yoy','red_yoy','turkey_mom3']:
        df[c.replace('broilers','broiler')+'_lag2' if c!='broilers_yoy' else 'broiler_yoy_lag2'] = df[c].shift(lag)
    df['broiler_yoy_lag5'] = df.broilers_yoy.shift(lag+3)
    # The two-month release buffer applies to *all* candidate signals and controls.
    df['factor_raw'] = (beef_weight*df.beef_yoy.shift(lag)
                        + pork_weight*df.pork_yoy.shift(lag)
                        - turkey_weight*df.turkey_yoy.shift(lag))
    df['factor'] = np.tanh(df.factor_raw/20.0)
    df['target'] = df.broilers_yoy.shift(-horizon)
    df['target_date'] = df.date + pd.DateOffset(months=horizon)
    df['label_available'] = df.target_date + pd.DateOffset(months=lag)
    keep=['date','target_date','label_available','target','factor','factor_raw',
          'broiler_yoy_lag2','broiler_yoy_lag5','broiler_mom3_lag2',
          'red_yoy_lag2','beef_yoy_lag2','pork_yoy_lag2','turkey_yoy_lag2','turkey_mom3_lag2']
    panel=df[keep].dropna().reset_index(drop=True)
    assert (panel.label_available>panel.date).all()
    return panel


def ridge_forecast(train, row, features, alpha=ALPHA):
    if not features: return float(train.target.mean())
    x=train[features].to_numpy(float)
    y=train.target.to_numpy(float)
    mu=x.mean(axis=0)
    sd=x.std(axis=0)
    sd=np.where(sd<1e-10,1.,sd)
    z=(x-mu)/sd
    z0=(row[features].to_numpy(float)-mu)/sd
    ym=y.mean()
    coef=np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]),z.T@(y-ym))
    return float(ym+z0@coef)


def walkforward(panel, oos_start=OOS_START, min_train=MIN_TRAIN, feature_override=None, models=None):
    models=models or MODELS
    out=[]
    for i,row in panel.iterrows():
        if row.date<pd.Timestamp(oos_start):continue
        # Training labels must have been published by the formation month,
        # even under the fixed 2-month proxy lag; never fit on overlapping future labels.
        train=panel.loc[(panel.label_available<=row.date)&(panel.date<row.date)]
        if len(train)<min_train:continue
        pred={'date':row.date,'target_date':row.target_date,'target':float(row.target),
              'factor':float(row.factor),'n_train':len(train),'max_training_target_date':train.target_date.max(),
              'max_training_label_available':train.label_available.max()}
        if 'historical_mean' in models:pred['historical_mean']=float(train.target.mean())
        if 'persistence' in models:pred['persistence']=float(row.broiler_yoy_lag2)
        if 'momentum' in models:pred['momentum']=float(2*row.broiler_yoy_lag2-row.broiler_yoy_lag5)
        if 'ar_ridge' in models:pred['ar_ridge']=ridge_forecast(train,row,AR)
        if 'macro_control' in models:pred['macro_control']=ridge_forecast(train,row,CONTROL)
        if 'factor_only' in models:pred['factor_only']=ridge_forecast(train,row,['factor'])
        if 'augmented' in models:pred['augmented']=ridge_forecast(train,row,CONTROL+['factor'])
        out.append(pred)
    return pd.DataFrame(out)


def rmse(y,p):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(p))**2)))


def scorecard(pred):
    out=[]
    for name in MODELS:
        out.append({'model':name,'n_oos':len(pred),'rmse_log_pp':rmse(pred.target,pred[name]),
                    'mae_log_pp':float(np.abs(pred.target-pred[name]).mean()),
                    'bias_log_pp':float((pred[name]-pred.target).mean())})
    return pd.DataFrame(out).sort_values('rmse_log_pp')


def block_reorder_factor(factor, rng, block=12):
    # Non-overlapping contiguous calendar blocks, reordered as whole blocks.
    # Retains within-block dependence, not a valid exact conditional null test.
    n=len(factor)
    blocks=[np.arange(i,min(i+block,n)) for i in range(0,n,block)]
    perm=rng.permutation(len(blocks))
    return np.asarray(factor)[np.concatenate([blocks[k] for k in perm])]


def block_bootstrap_gain(pred, draws=2000, block=12, seed=SEED+1):
    rng=np.random.default_rng(seed)
    n=len(pred)
    out=np.empty(draws)
    y=pred.target.to_numpy();a=pred.macro_control.to_numpy();b=pred.augmented.to_numpy()
    for k in range(draws):
        starts=rng.integers(0,n,size=int(np.ceil(n/block)))
        ix=np.concatenate([(np.arange(s,s+block)%n) for s in starts])[:n]
        out[k]=rmse(y[ix],a[ix])-rmse(y[ix],b[ix])
    return out


def _fast_augmented_forecasts(panel, factor_values=None):
    """Equivalent train-only standardized ridge via cumulative sufficient statistics.

    Avoids 1000 x OOS x pandas fits while preserving the exact expanding
    training cutoff and target-release purge used by walkforward().
    """
    x0=panel[CONTROL].to_numpy(dtype=float)
    factor=np.asarray(panel.factor if factor_values is None else factor_values,dtype=float)
    x=np.column_stack((x0,factor))
    y=panel.target.to_numpy(float)
    dates=panel.date.to_numpy(dtype='datetime64[ns]')
    label=panel.label_available.to_numpy(dtype='datetime64[ns]')
    origins=np.flatnonzero(dates>=np.datetime64(OOS_START))
    cutoffs=np.searchsorted(label,dates[origins],side='right')
    mask=cutoffs>=MIN_TRAIN
    origins=origins[mask];cutoffs=cutoffs[mask]
    sums=np.vstack([np.zeros(x.shape[1]),np.cumsum(x,axis=0)])
    sums2=np.vstack([np.zeros(x.shape[1]),np.cumsum(x*x,axis=0)])
    xx=np.concatenate([np.zeros((1,x.shape[1],x.shape[1])),np.cumsum(x[:,:,None]*x[:,None,:],axis=0)])
    xy=np.vstack([np.zeros(x.shape[1]),np.cumsum(x*y[:,None],axis=0)])
    sy=np.concatenate([[0],np.cumsum(y)])
    out=np.empty(len(origins))
    eye=np.eye(x.shape[1])
    for j,(i,k) in enumerate(zip(origins,cutoffs)):
        mu=sums[k]/k
        sd=np.sqrt(np.maximum(0,sums2[k]/k-mu**2))
        sd=np.where(sd<1e-10,1.,sd)
        ym=sy[k]/k
        gram=(xx[k]-k*np.outer(mu,mu))/np.outer(sd,sd)
        rhs=(xy[k]-k*mu*ym)/sd
        beta=np.linalg.solve(gram+ALPHA*eye,rhs)
        out[j]=ym+((x[i]-mu)/sd)@beta
    return out


def permutation_test(panel, observed_gain, draws=1000, block=12, seed=SEED+2):
    rng=np.random.default_rng(seed)
    null=np.empty(draws)
    baseline=walkforward(panel,models=['macro_control'])
    baseline_rmse=rmse(baseline.target,baseline.macro_control)
    for k in range(draws):
        shuffled=block_reorder_factor(panel.factor.to_numpy(),rng,block)
        p=_fast_augmented_forecasts(panel,shuffled)
        null[k]=baseline_rmse-rmse(baseline.target,p)
    tail=(1+int(np.sum(null>=observed_gain)))/(draws+1)
    return null,tail


def weight_sensitivity(raw, observed_gain, draws=1000, seed=SEED+3):
    rng=np.random.default_rng(seed)
    w=rng.uniform(.2,.8,size=draws)
    base=make_panel(raw)
    baseline=walkforward(base,models=['macro_control'])
    baseline_rmse=rmse(baseline.target,baseline.macro_control)
    beef=base.beef_yoy_lag2.to_numpy()
    pork=base.pork_yoy_lag2.to_numpy()
    turkey=base.turkey_yoy_lag2.to_numpy()
    gain=np.empty(draws)
    for k,wbeef in enumerate(w):
        factor=np.tanh((wbeef*beef+(1-wbeef)*pork-turkey)/20.)
        p=_fast_augmented_forecasts(base,factor)
        gain[k]=baseline_rmse-rmse(baseline.target,p)
    return pd.DataFrame({'beef_weight':w,'pork_weight':1-w,'gain_log_pp':gain})


def alternative_checks(raw):
    rows=[]
    for lag in [1,2,3,6]:
        for h in [1,3,6,12]:
            p=make_panel(raw,horizon=h,lag=lag)
            pr=walkforward(p,models=['macro_control','augmented'])
            rows.append({'lag_months':lag,'horizon_months':h,'n_oos':len(pr),
                         'control_rmse':rmse(pr.target,pr.macro_control),
                         'augmented_rmse':rmse(pr.target,pr.augmented),
                         'gain_log_pp':rmse(pr.target,pr.macro_control)-rmse(pr.target,pr.augmented)})
    return pd.DataFrame(rows)


def ablations(raw):
    base=make_panel(raw)
    cases={
      'base_equal_beef_pork_minus_turkey':base.factor.to_numpy(),
      'beef_only_minus_turkey':np.tanh((base.beef_yoy_lag2-base.turkey_yoy_lag2)/20),
      'pork_only_minus_turkey':np.tanh((base.pork_yoy_lag2-base.turkey_yoy_lag2)/20),
      'red_meat_only':np.tanh(base.red_yoy_lag2/20),
      'negative_turkey_only':np.tanh(-base.turkey_yoy_lag2/20),
      'factor_sign_flipped':-base.factor.to_numpy(),
    }
    rows=[]
    for label,values in cases.items():
        p=base.copy();p['factor']=values
        pr=walkforward(p,models=['macro_control','augmented'])
        rows.append({'case':label,'n_oos':len(pr),'gain_log_pp':rmse(pr.target,pr.macro_control)-rmse(pr.target,pr.augmented)})
    return pd.DataFrame(rows)


def regime_checks(pred):
    rows=[]
    groups={'2010-2019':pred.date<'2020-01-01',
            '2020-2021':pred.date.between('2020-01-01','2021-12-31'),
            '2022-2023':pred.date>='2022-01-01'}
    for name,mask in groups.items():
        q=pred.loc[mask]
        if len(q):rows.append({'regime':name,'n':len(q),'control_rmse':rmse(q.target,q.macro_control),
                               'augmented_rmse':rmse(q.target,q.augmented),
                               'gain_log_pp':rmse(q.target,q.macro_control)-rmse(q.target,q.augmented)})
    return pd.DataFrame(rows)


def plot_all(raw,panel,pred,scores,placebo,boot,weights,alt,abl,regime):
    plt.rcParams.update({'figure.figsize':(9,4.8),'font.size':10,'axes.grid':True,'grid.alpha':.22,'svg.hashsalt':'signals-to-alpha-poultry-20261028'})
    def save(name):
        plt.tight_layout();plt.savefig(FIGURES/(name+'.svg'),format='svg',bbox_inches='tight',metadata={'Date':None});plt.close()
    fig,ax=plt.subplots();ax.plot(raw.date,raw.broilers,label='Broilers');ax.plot(raw.date,raw.turkey,label='Turkey');ax.set_ylabel('Million lb / month');ax.set_title('01 | Historical poultry output');ax.legend();save('01_poultry_output')
    fig,ax=plt.subplots();ax.plot(raw.date,raw.beef,label='Beef');ax.plot(raw.date,raw.pork,label='Pork');ax.set_title('02 | Red meat supply history');ax.set_ylabel('Million lb / month');ax.legend();save('02_red_meat_output')
    fig,ax=plt.subplots();ax.plot(panel.date,panel.factor,label='Two-month stale protein divergence');ax.axhline(0,color='black',lw=.7);ax.set_title('03 | Fixed factor: tanh(red meat minus turkey / 20)');ax.legend();save('03_factor_history')
    fig,ax=plt.subplots();ax.scatter(panel.factor,panel.target,s=9,alpha=.3);ax.set_xlabel('Factor at formation');ax.set_ylabel('Future broiler YoY log-pp');ax.set_title('04 | Exploratory factor-target association');save('04_scatter')
    fig,ax=plt.subplots();ax.plot(pred.date,pred.target,label='Observed future YoY',lw=1.1);ax.plot(pred.date,pred.macro_control,label='Macro control',alpha=.8);ax.plot(pred.date,pred.augmented,label='Augmented',alpha=.8);ax.set_title('05 | Purged expanding-window OOS predictions');ax.legend();save('05_oos_predictions')
    fig,ax=plt.subplots();ax.barh(scores.model,scores.rmse_log_pp);ax.set_xlabel('RMSE, log-pp (lower better)');ax.set_title('06 | Competing OOS baselines');save('06_rmse_scorecard')
    fig,ax=plt.subplots();d=(pred.target-pred.macro_control)**2-(pred.target-pred.augmented)**2;ax.plot(pred.date,d.cumsum()/np.arange(1,len(d)+1));ax.axhline(0,color='black',lw=.8);ax.set_ylabel('Cumulative mean squared-loss gain');ax.set_title('07 | Time-varying paired forecast loss');save('07_loss_gain')
    fig,ax=plt.subplots();ax.hist(placebo,bins=35,alpha=.75);ax.axvline(rmse(pred.target,pred.macro_control)-rmse(pred.target,pred.augmented),color='red',label='Observed gain');ax.set_title('08 | 1,000 exploratory 12-month block reorders');ax.legend();save('08_placebo')
    fig,ax=plt.subplots();ax.hist(boot,bins=40,alpha=.8);ax.axvline(0,color='black',lw=.9);ax.set_title('09 | 2,000 paired moving-block bootstrap gains');save('09_bootstrap')
    fig,ax=plt.subplots();ax.scatter(weights.beef_weight,weights.gain_log_pp,s=8,alpha=.35);ax.axhline(0,color='black',lw=.9);ax.set_title('10 | 1,000 exposure weight perturbations');ax.set_xlabel('Beef weight (pork = 1 - beef)');ax.set_ylabel('RMSE gain');save('10_exposure_weights')
    fig,ax=plt.subplots();for_plot=alt.pivot(index='lag_months',columns='horizon_months',values='gain_log_pp');im=ax.imshow(for_plot.values,cmap='coolwarm',aspect='auto',vmin=-max(abs(for_plot.min().min()),abs(for_plot.max().max())),vmax=max(abs(for_plot.min().min()),abs(for_plot.max().max())));ax.set_xticks(range(len(for_plot.columns)),for_plot.columns);ax.set_yticks(range(len(for_plot.index)),for_plot.index);ax.set_xlabel('Forecast horizon (months)');ax.set_ylabel('Publication lag (months)');ax.set_title('11 | Lag and horizon sensitivity');fig.colorbar(im,ax=ax,label='RMSE gain');save('11_horizon_lag')
    fig,ax=plt.subplots();ax.bar(abl.case,abl.gain_log_pp);ax.axhline(0,color='black',lw=.9);ax.tick_params(axis='x',labelrotation=55);ax.set_title('12 | Component ablations');ax.set_ylabel('RMSE gain');save('12_ablation')
    fig,ax=plt.subplots();ax.bar(regime.regime,regime.gain_log_pp);ax.axhline(0,color='black',lw=.9);ax.set_title('13 | Structural regime sensitivity');ax.set_ylabel('RMSE gain');save('13_regime')


def run_all(draws=1000,bootstrap_draws=2000,weight_draws=1000):
    RESULTS.mkdir(exist_ok=True);FIGURES.mkdir(exist_ok=True)
    raw=load_raw();panel=make_panel(raw);pred=walkforward(panel)
    assert len(pred)>100 and pred.date.min()>=pd.Timestamp(OOS_START)
    assert (pred.max_training_label_available<=pred.date).all()
    scores=scorecard(pred)
    observed=rmse(pred.target,pred.macro_control)-rmse(pred.target,pred.augmented)
    boot=block_bootstrap_gain(pred,draws=bootstrap_draws)
    placebo,tail=permutation_test(panel,observed,draws=draws)
    weights=weight_sensitivity(raw,observed,draws=weight_draws)
    alt=alternative_checks(raw);abl=ablations(raw);regime=regime_checks(pred)
    raw_2023=raw.loc[raw.date.dt.year==2023,['broilers','turkey','beef','pork']].sum()
    raw_2019=raw.loc[raw.date.dt.year==2019,['broilers','turkey','beef','pork']].sum()
    corr=float(panel[['factor','target']].corr(method='spearman').iloc[0,1])
    metrics={
      'data_start':str(raw.date.min().date()),'data_end':str(raw.date.max().date()),'raw_n':len(raw),
      'broiler_n':int(raw.broilers.notna().sum()),'panel_n':len(panel),'oos_n':len(pred),
      'oos_start':str(pred.date.min().date()),'oos_end':str(pred.date.max().date()),
      'oos_min_train':int(pred.n_train.min()),'oos_max_train':int(pred.n_train.max()),
      'lag_months':LAG,'horizon_months':HORIZON,'purge_rule':'train target month + 2 months <= formation month',
      'observed_rmse_gain_log_pp':observed,'placebo_draws':draws,'placebo_exploratory_tail_fraction':tail,
      'bootstrap_draws':bootstrap_draws,'bootstrap_gain_ci_95':np.quantile(boot,[.025,.975]).tolist(),
      'weight_draws':weight_draws,'weight_positive_gain_fraction':float((weights.gain_log_pp>0).mean()),
      'factor_target_full_panel_spearman':corr,
      'broiler_production_2023_million_lb':float(raw_2023.broilers),
      'broiler_production_2019_million_lb':float(raw_2019.broilers),
      'broiler_production_2019_2023_growth_pct':float((raw_2023.broilers/raw_2019.broilers-1)*100),
      'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
      'equity_alpha_established':False,'pit_verified':False,'historical_vintage_available':False,
      'company_fundamentals_tested':False,'security_total_returns_tested':False,
      'status':'REPRODUCED RETROSPECTIVE POULTRY PRODUCTION MACRO PILOT - NOT PIT / NOT EQUITY ALPHA',
    }
    panel.to_csv(HERE/'data/derived_formation_panel.csv',index=False,float_format='%.10g')
    pred.to_csv(RESULTS/'oos_predictions.csv',index=False,float_format='%.10g')
    scores.to_csv(RESULTS/'baseline_scorecard.csv',index=False,float_format='%.10g')
    pd.DataFrame({'gain_log_pp':boot}).to_csv(RESULTS/'bootstrap_draws.csv',index=False)
    pd.DataFrame({'gain_log_pp':placebo}).to_csv(RESULTS/'placebo_draws.csv',index=False)
    weights.to_csv(RESULTS/'weight_perturbations.csv',index=False)
    alt.to_csv(RESULTS/'lag_horizon_checks.csv',index=False)
    abl.to_csv(RESULTS/'ablation_checks.csv',index=False)
    regime.to_csv(RESULTS/'regime_checks.csv',index=False)
    (RESULTS/'summary.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    plot_all(raw,panel,pred,scores,placebo,boot,weights,alt,abl,regime)
    print(json.dumps({k:metrics[k] for k in ['raw_n','panel_n','oos_n','observed_rmse_gain_log_pp','placebo_exploratory_tail_fraction','bootstrap_gain_ci_95','weight_positive_gain_fraction']},indent=2))
    print(scores.to_string(index=False))
    return metrics

if __name__=='__main__':run_all()
