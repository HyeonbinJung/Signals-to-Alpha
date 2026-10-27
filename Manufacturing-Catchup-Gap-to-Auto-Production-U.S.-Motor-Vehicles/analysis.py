"""Retrospective U.S. auto manufacturing lead-factor falsification.
All transformations and training are computed at origin; the G.17 2026-10-16
fixed snapshot is NOT an archival point-in-time release history.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'
RESULTS=ROOT/'results'
FIGURES=ROOT/'figures'
SEED=20261027
COLS=['auto_yoy_lag','manufacturing_yoy_lag','auto_mom_lag']

def load_raw():
    df=pd.read_csv(DATA/'frozen_auto_manufacturing_2026-10-27.csv',parse_dates=['date']).sort_values('date')
    assert df.date.is_unique and len(df)==201 and df.date.min()==pd.Timestamp('2010-01-01')
    assert df.date.max()==pd.Timestamp('2026-09-01') and df[['auto_ip','manufacturing_ip']].gt(0).all().all()
    assert df.date.diff().dropna().eq(pd.Timedelta(days=30)).mean()<0.5 # calendar month, not 30d
    return df

def make_panel(raw=None,horizon=3,lag=2,scale=10.0,weight=1.0):
    if raw is None:raw=load_raw()
    a=raw.copy().set_index('date')
    for c in ['auto_ip','manufacturing_ip']:
        a[c+'_yoy']=100*(np.log(a[c])-np.log(a[c].shift(12)))
        a[c+'_mom']=100*(np.log(a[c])-np.log(a[c].shift(3)))
    # At formation date t, only observations dated <= t-lag can enter features.
    a['auto_yoy_lag']=a.auto_ip_yoy.shift(lag)
    a['manufacturing_yoy_lag']=a.manufacturing_ip_yoy.shift(lag)
    a['auto_mom_lag']=a.auto_ip_mom.shift(lag)
    a['manufacturing_mom_lag']=a.manufacturing_ip_mom.shift(lag)
    a['gap']=weight*(a.manufacturing_mom_lag-a.auto_mom_lag)+(1-weight)*(a.manufacturing_yoy_lag-a.auto_yoy_lag)
    a['factor']=np.tanh(a.gap/scale)
    # Outcome is future YoY level growth at t+h, not change from t to t+h.
    a['target']=a.auto_ip_yoy.shift(-horizon)
    a['origin']=a.index
    a['target_month']=a.index+pd.DateOffset(months=horizon)
    panel=a.reset_index(drop=True).dropna(subset=COLS+['factor','target']).reset_index(drop=True)
    return panel

def ridge_predict(X,y,x,alpha=12.0):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float);x=np.asarray(x,dtype=float)
    if len(X)==0:return float('nan')
    mu=X.mean(0);sd=X.std(0);sd=np.where(sd<1e-8,1,sd)
    z=(X-mu)/sd; xx=(x-mu)/sd
    ym=y.mean()
    coef=np.linalg.solve(z.T@z+alpha*np.eye(X.shape[1]),z.T@(y-ym))
    return float(ym+xx@coef)

def oos(panel, horizon=3, lag=2, min_train=60, factor_col='factor', extra_cols=None, label='base', minimal=False):
    """Vectorized pre-slicing; exact monthly target availability purge."""
    controls=COLS if extra_cols is None else list(extra_cols)
    origins=panel.origin.to_numpy(dtype='datetime64[ns]')
    targets=panel.target_month.to_numpy(dtype='datetime64[ns]')
    y=panel.target.to_numpy(dtype=float)
    cols=list(dict.fromkeys(controls+[factor_col,'auto_yoy_lag']))
    arr={c:panel[c].to_numpy(dtype=float) for c in cols}
    rows=[]
    for i in range(len(panel)):
        # Only training targets observed by t-lag are eligible.
        cutoff=panel.origin.iloc[i]-pd.DateOffset(months=lag)
        j=int(np.searchsorted(targets,np.datetime64(cutoff),side='right'))
        j=min(j,i)
        if j<min_train:continue
        yt=y[:j]
        def pred(cs):
            x=np.column_stack([arr[c][:j] for c in cs]); xx=np.array([arr[c][i] for c in cs])
            return ridge_predict(x,yt,xx)
        preds={'macro_control':pred(controls),'augmented':pred(controls+[factor_col])}
        if not minimal:
            preds.update({'mean':float(yt.mean()),'persistence':pred(['auto_yoy_lag']), 'factor_only':pred([factor_col])})
        rows.append({'origin':panel.origin.iloc[i],'target_month':panel.target_month.iloc[i],
                     'actual':y[i],'n_train':j,**preds})
    return pd.DataFrame(rows)

def score(pred):
    if len(pred)==0:return pd.DataFrame()
    return pd.DataFrame([{'model':c,'n':len(pred),'rmse':float(np.sqrt(np.mean((pred.actual-pred[c])**2))),
                         'mae':float(np.mean(abs(pred.actual-pred[c]))),
                         'rank_ic':float(spearmanr(pred.actual,pred[c]).statistic)}
                         for c in ['mean','persistence','macro_control','factor_only','augmented']])

def improvement(pred, challenger='augmented', baseline='macro_control'):
    return float(np.sqrt(np.mean((pred.actual-pred[baseline])**2))-np.sqrt(np.mean((pred.actual-pred[challenger])**2)))

def block_bootstrap(pred, reps=2000, block=12, seed=SEED):
    rng=np.random.default_rng(seed);n=len(pred); vals=np.empty(reps)
    a=pred.actual.to_numpy();b=pred.macro_control.to_numpy();c=pred.augmented.to_numpy()
    for k in range(reps):
        ids=[]
        while len(ids)<n:
            start=int(rng.integers(0,n))
            ids.extend([(start+j)%n for j in range(block)])
        ix=np.array(ids[:n])
        vals[k]=np.sqrt(np.mean((a[ix]-b[ix])**2))-np.sqrt(np.mean((a[ix]-c[ix])**2))
    return vals

def block_permutation(panel, observed, reps=1000, block=12, horizon=3, lag=2, seed=SEED):
    rng=np.random.default_rng(seed);n=len(panel)
    blocks=[np.arange(i,min(i+block,n)) for i in range(0,n,block)]
    vals=np.empty(reps);factor=panel.factor.to_numpy()
    for k in range(reps):
        # Reorder intact time blocks, retaining within-block serial dependence.
        order=rng.permutation(len(blocks))
        shuffled=np.concatenate([factor[blocks[j]] for j in order])
        p=panel.copy();p['factor']=shuffled
        q=oos(p,horizon=horizon,lag=lag,minimal=True)
        vals[k]=improvement(q)
    # One-sided randomization tail for incremental improvement, descriptive only.
    return vals,float((1+np.sum(vals>=observed))/(reps+1))

def factor_sensitivity(raw, reps=1000, seed=SEED):
    rng=np.random.default_rng(seed)
    vals=[]
    for k in range(reps):
        scale=float(rng.uniform(5,20));weight=float(rng.uniform(.6,1.0))
        p=make_panel(raw,scale=scale,weight=weight)
        q=oos(p,minimal=True)
        vals.append({'iteration':k+1,'scale':scale,'weight':weight,'rmse_improvement':improvement(q)})
    return pd.DataFrame(vals)

def regime_scores(pred):
    out=[]
    groups={
      'pre_2020':pred[pred.origin<'2020-01-01'],
      'pandemic_2020_2021':pred[(pred.origin>='2020-01-01')&(pred.origin<'2022-01-01')],
      'post_2022':pred[pred.origin>='2022-01-01'],
      'excluding_2020_2021':pred[(pred.origin<'2020-01-01')|(pred.origin>='2022-01-01')],
    }
    for name,df in groups.items():
        if len(df)<5:continue
        out.append({'regime':name,'n':len(df),'improvement':improvement(df),'rmse_control':float(np.sqrt(np.mean((df.actual-df.macro_control)**2))), 'rmse_full':float(np.sqrt(np.mean((df.actual-df.augmented)**2)))})
    return pd.DataFrame(out)

def run(quick=False):
    RESULTS.mkdir(exist_ok=True);FIGURES.mkdir(exist_ok=True)
    raw=load_raw();panel=make_panel(raw);pred=oos(panel)
    assert len(pred)>60
    panel.to_csv(DATA/'derived_formation_panel.csv',index=False)
    pred.to_csv(RESULTS/'oos_predictions.csv',index=False)
    s=score(pred);s.to_csv(RESULTS/'oos_scorecard.csv',index=False)
    obs=improvement(pred)
    boot=block_bootstrap(pred,reps=2000 if not quick else 40)
    pd.DataFrame({'draw':np.arange(len(boot))+1,'rmse_improvement':boot}).to_csv(RESULTS/'bootstrap_draws.csv',index=False)
    perm,pval=block_permutation(panel,obs,reps=1000 if not quick else 30)
    pd.DataFrame({'draw':np.arange(len(perm))+1,'rmse_improvement':perm}).to_csv(RESULTS/'block_placebo_draws.csv',index=False)
    sens=factor_sensitivity(raw,reps=1000 if not quick else 30)
    sens.to_csv(RESULTS/'exposure_perturbation.csv',index=False)
    regimes=regime_scores(pred);regimes.to_csv(RESULTS/'regime_scores.csv',index=False)
    loo=[]
    for yr in sorted(pred.origin.dt.year.unique()):
        q=pred[pred.origin.dt.year!=yr]
        loo.append({'excluded_year':int(yr),'n':len(q),'improvement':improvement(q)})
    pd.DataFrame(loo).to_csv(RESULTS/'leave_one_year_out.csv',index=False)
    alt=[]
    for h in [1,3,6,12]:
        for lag in [1,2,3,4]:
            q=oos(make_panel(raw,horizon=h,lag=lag),horizon=h,lag=lag)
            alt.append({'horizon':h,'lag':lag,'n':len(q),'improvement':improvement(q),'rmse_mean':score(q).query("model=='mean'").rmse.iloc[0]})
    pd.DataFrame(alt).to_csv(RESULTS/'horizon_lag_sensitivity.csv',index=False)
    ablations=[]
    for name,cols in [('no_auto_momentum',['auto_yoy_lag','manufacturing_yoy_lag']),('no_manufacturing_yoy',['auto_yoy_lag','auto_mom_lag']),('auto_yoy_only',['auto_yoy_lag'])]:
        q=oos(panel,extra_cols=cols)
        ablations.append({'ablation':name,'n':len(q),'rmse_control':score(q).query("model=='macro_control'").rmse.iloc[0], 'rmse_full':score(q).query("model=='augmented'").rmse.iloc[0], 'improvement':improvement(q)})
    pd.DataFrame(ablations).to_csv(RESULTS/'ablations.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'figure.dpi':120})
    def save(name):plt.tight_layout();plt.savefig(FIGURES/(name+'.svg'));plt.close()
    plt.figure(figsize=(10,4));plt.plot(raw.date,raw.auto_ip,label='Motor vehicles & parts');plt.plot(raw.date,raw.manufacturing_ip,label='Manufacturing');plt.legend();plt.ylabel('Index (2017=100)');plt.title('Frozen revised industrial production levels');save('01_industry_levels')
    plt.figure(figsize=(10,4));plt.plot(panel.origin,panel.auto_yoy_lag,label='Auto YoY (lagged)',alpha=.7);plt.plot(panel.origin,panel.manufacturing_yoy_lag,label='Manufacturing YoY (lagged)',alpha=.7);plt.legend();plt.ylabel('Log-pp');plt.title('Lagged industry vs macro growth');save('02_growth_divergence')
    plt.figure(figsize=(10,4));plt.plot(panel.origin,panel.factor);plt.axhline(0,color='gray',lw=.8);plt.title('Predefined nonlinear manufacturing–auto momentum gap');plt.ylabel('tanh(gap / 10)');save('03_factor')
    plt.figure(figsize=(10,4));plt.plot(pred.origin,pred.actual,label='Actual 3m-ahead YoY');plt.plot(pred.origin,pred.augmented,label='Augmented OOS forecast',alpha=.8);plt.legend();plt.title('Purged expanding-window forecasts');plt.ylabel('Log-pp');save('04_oos_predictions')
    plt.figure(figsize=(7,4));plt.bar(s.model,s.rmse);plt.xticks(rotation=25,ha='right');plt.ylabel('RMSE, log-pp');plt.title('Same-origin baseline scorecard');save('05_scorecard')
    plt.figure(figsize=(9,4));plt.plot(pred.origin,(pred.actual-pred.macro_control)**2-(pred.actual-pred.augmented)**2);plt.axhline(0,color='gray',lw=.8);plt.ylabel('Squared-loss improvement');plt.title('Paired loss difference over time');save('06_paired_loss')
    plt.figure(figsize=(7,4));plt.hist(boot,bins=35);plt.axvline(obs,color='black',label='Observed');plt.legend();plt.title('Moving-block bootstrap: RMSE improvement');save('07_bootstrap')
    plt.figure(figsize=(7,4));plt.hist(perm,bins=35);plt.axvline(obs,color='black',label='Observed');plt.legend();plt.title('12-month block reorder placebo (exploratory)');save('08_placebo')
    plt.figure(figsize=(8,4));plt.scatter(sens.scale,sens.rmse_improvement,s=8,alpha=.3);plt.axhline(0,color='gray');plt.title('1,000 scale / 3m-vs-12m mixture perturbations');plt.xlabel('Factor tanh scale');plt.ylabel('RMSE improvement');save('09_exposure_sensitivity')
    plt.figure(figsize=(8,4));plt.bar(regimes.regime,regimes.improvement);plt.xticks(rotation=20,ha='right');plt.axhline(0,color='gray');plt.ylabel('RMSE improvement');plt.title('Regime instability');save('10_regime')
    plt.figure(figsize=(8,4));plt.bar(pd.DataFrame(loo).excluded_year.astype(str),pd.DataFrame(loo).improvement);plt.xticks(rotation=90);plt.axhline(0,color='gray');plt.title('Leave-one-calendar-year-out OOS score');save('11_loyo')
    summary={'raw_months':len(raw),'formation_rows':len(panel),'oos_origins':len(pred),'first_origin':str(pred.origin.min().date()),'last_origin':str(pred.origin.max().date()),'rmse_improvement':obs,'bootstrap_95':[float(x) for x in np.quantile(boot,[.025,.975])],'placebo_tail_fraction':pval,'placebo_draws':len(perm),'bootstrap_draws':len(boot),'sensitivity_draws':len(sens),'sensitivity_positive_fraction':float((sens.rmse_improvement>0).mean()),'point_in_time':False,'equity_alpha_established':False}
    import json
    (RESULTS/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(s.to_string(index=False));print(json.dumps(summary,indent=2));print(regimes.to_string(index=False));return summary
if __name__=='__main__':run()
