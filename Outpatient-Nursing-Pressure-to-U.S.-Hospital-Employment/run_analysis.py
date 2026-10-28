"""Frozen-snapshot U.S. hospital employment forecast falsification, no equity alpha claim.

All forecast transforms are deterministic and all Ridge centering/scaling is train-only.
Historical release vintages are unavailable: this is NOT a point-in-time backtest.
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

ROOT = Path(__file__).resolve().parent
RAW = ROOT/'data'/'raw_fred_ces_2010_2026_snapshot.csv'
EXPECTED_SHA = 'f1d5a8ff28a55f2d1798cbdb9cac239d46db6c006b0a9e1801abae1b3b1665f6'
ALPHA = 10.0
START_OOS = pd.Timestamp('2018-01-01')
SEED = 20261028


def load_raw():
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == EXPECTED_SHA, 'Source snapshot changed'
    d = pd.read_csv(RAW, parse_dates=['date']).sort_values('date').reset_index(drop=True)
    assert len(d)==201 and d['date'].iloc[0]==pd.Timestamp('2010-01-01')
    assert d['date'].iloc[-1]==pd.Timestamp('2026-09-01')
    assert d['date'].is_unique and not d.isna().any().any()
    assert d[['home','hospital','nursing','ambulatory','payroll']].gt(0).all().all()
    assert (d['ambulatory']-d['home']).gt(0).all()
    assert (d.date.diff().dropna().dt.days.between(28,31)).all()
    return d


def make_panel(d, horizon=6, lag=2, scale=5.0):
    """At t, use observations <=t-lag; target is YoY at t+horizon."""
    v = d.copy()
    v['outpatient_nonhome'] = v['ambulatory']-v['home']
    out=[]
    for t in range(lag+12, len(v)-horizon):
        row={'date':v.at[t,'date'], 't':t, 'target_mature_t':t+horizon+1}
        for col in ['home','hospital','nursing','ambulatory','outpatient_nonhome','payroll']:
            row['g_'+col] = 100*np.log(v.at[t-lag,col]/v.at[t-lag-12,col])
        row['hosp_momentum']=100*np.log(v.at[t-lag,'hospital']/v.at[t-lag-6,'hospital'])
        row['factor']=np.tanh((row['g_outpatient_nonhome']-row['g_nursing'])/scale)
        row['target']=100*np.log(v.at[t+horizon,'hospital']/v.at[t+horizon-12,'hospital'])
        out.append(row)
    p=pd.DataFrame(out)
    assert p.date.is_unique and p.target.notna().all()
    return p


def ridge_forecast(x, y, x_new, alpha=ALPHA):
    x=np.asarray(x,dtype=float); y=np.asarray(y,dtype=float); x_new=np.asarray(x_new,dtype=float)
    if x.ndim==1:x=x[:,None]
    if x_new.ndim==1:x_new=x_new[None,:]
    mu=x.mean(axis=0); sd=x.std(axis=0); sd=np.where(sd<1e-10,1.0,sd)
    z=(x-mu)/sd; zn=(x_new-mu)/sd
    ym=y.mean(); beta=np.linalg.solve(z.T@z+alpha*np.eye(x.shape[1]),z.T@(y-ym))
    return np.asarray(ym+zn@beta)

MODELS={
    'mean':[],
    'persistence':['g_hospital'],
    'momentum':['hosp_momentum'],
    'ar_ridge':['g_hospital','hosp_momentum'],
    'macro_controls':['g_hospital','g_payroll','g_nursing'],
    'full':['g_hospital','g_payroll','g_nursing','factor'],
    'factor_only':['factor'],
    'no_nursing':['g_hospital','g_payroll','factor'],
    'no_payroll':['g_hospital','g_nursing','factor'],
}

def walk_forward(panel, models=None, min_train=60, rolling=None):
    models=MODELS if models is None else models
    preds=[]
    for i,row in panel.iterrows():
        if row.date<START_OOS:continue
        tr=panel.loc[panel.target_mature_t<=row.t]
        if rolling is not None:tr=tr.tail(rolling)
        if len(tr)<min_train:continue
        out={'date':row.date,'t':int(row.t),'target':float(row.target),'train_n':len(tr)}
        for name,cols in models.items():
            out[name]=float(tr.target.mean() if not cols else ridge_forecast(tr[cols].to_numpy(),tr.target.to_numpy(),row[cols].to_numpy())[0])
        preds.append(out)
    r=pd.DataFrame(preds)
    assert not r.empty and r['date'].is_unique
    return r


def rmse(y, pred):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(pred))**2)))
def mae(y,pred):return float(np.mean(np.abs(np.asarray(y)-np.asarray(pred))))

def scorecard(o):
    return pd.DataFrame([{'model':m,'n':len(o),'rmse_log_pp':rmse(o.target,o[m]),'mae_log_pp':mae(o.target,o[m])} for m in MODELS])


def block_permute_factor(panel, rng, block=12):
    p=panel.copy(); a=p.factor.to_numpy(); blocks=[a[i:i+block] for i in range(0,len(a),block)]
    ix=rng.permutation(len(blocks)); p['factor']=np.concatenate([blocks[j] for j in ix]);return p


def fast_full_preds(panel, factors, o):
    # Same expanding, target-matured training origins as walk_forward; only numpy in 1000x refits.
    t=panel.t.to_numpy(); maturity=panel.target_mature_t.to_numpy(); y=panel.target.to_numpy()
    controls=panel[['g_hospital','g_payroll','g_nursing']].to_numpy()
    x=np.column_stack((controls,np.asarray(factors,dtype=float)))
    origin_rows=np.searchsorted(t,o.t.to_numpy())
    preds=np.empty(len(origin_rows))
    for k,i in enumerate(origin_rows):
        end=np.searchsorted(maturity,t[i],side='right')
        preds[k]=ridge_forecast(x[:end],y[:end],x[i])[0]
    return preds


def placebo_draws(panel, o, draws=1000, seed=SEED):
    rng=np.random.default_rng(seed); baseline=rmse(o.target,o.macro_controls)
    a=panel.factor.to_numpy();blocks=[a[i:i+12] for i in range(0,len(a),12)]
    gains=np.empty(draws)
    for i in range(draws):
        ix=rng.permutation(len(blocks)); f=np.concatenate([blocks[j] for j in ix])
        gains[i]=baseline-rmse(o.target,fast_full_preds(panel,f,o))
    return gains

def bootstrap_gains(o, draws=2000, block=12, seed=SEED+1):
    rng=np.random.default_rng(seed); n=len(o); err0=(o.target-o.macro_controls).to_numpy();err1=(o.target-o.full).to_numpy()
    out=np.empty(draws)
    for j in range(draws):
        starts=rng.integers(0,n-block+1,size=int(np.ceil(n/block)))
        idx=np.concatenate([np.arange(s,s+block) for s in starts])[:n]
        out[j]=np.sqrt(np.mean(err0[idx]**2))-np.sqrt(np.mean(err1[idx]**2))
    return out


def weight_sensitivity(panel, o, draws=1000, seed=SEED+2):
    rng=np.random.default_rng(seed); weights=rng.uniform(0.5,1.0,size=draws)
    base=rmse(o.target,o.macro_controls)
    result=[]
    for w in weights:
        f=np.tanh((w*panel.g_outpatient_nonhome.to_numpy()+(1-w)*panel.g_home.to_numpy()-panel.g_nursing.to_numpy())/5.0)
        result.append({'outpatient_weight':w,'rmse_gain_log_pp':base-rmse(o.target,fast_full_preds(panel,f,o))})
    return pd.DataFrame(result)

def robustness(raw, o):
    out=[]
    for h,l,rolling,label in [(3,2,None,'horizon_3m'),(9,2,None,'horizon_9m'),(6,3,None,'lag_3m'),(6,4,None,'lag_4m'),(6,2,84,'rolling_84m')]:
        p=make_panel(raw,horizon=h,lag=l)
        z=walk_forward(p,{'macro_controls':MODELS['macro_controls'],'full':MODELS['full']},rolling=rolling)
        out.append({'test':label,'n':len(z),'macro_rmse':rmse(z.target,z.macro_controls),'full_rmse':rmse(z.target,z.full),'gain':rmse(z.target,z.macro_controls)-rmse(z.target,z.full)})
    for label,mask in [('pre_2020',o.date<'2020-01-01'),('pandemic_2020_2021',o.date.between('2020-01-01','2021-12-31')),('post_2021',o.date>='2022-01-01'),('exclude_2020_2021',~o.date.between('2020-01-01','2021-12-31'))]:
        z=o.loc[mask];out.append({'test':label,'n':len(z),'macro_rmse':rmse(z.target,z.macro_controls),'full_rmse':rmse(z.target,z.full),'gain':rmse(z.target,z.macro_controls)-rmse(z.target,z.full)})
    return pd.DataFrame(out)


def leave_one_year(o):
    r=[]
    for year in sorted(o.date.dt.year.unique()):
        z=o.loc[o.date.dt.year!=year]
        r.append({'excluded_year':int(year),'n':len(z),'gain':rmse(z.target,z.macro_controls)-rmse(z.target,z.full)})
    return pd.DataFrame(r)


def effective_n(loss_diff,max_lag=12):
    a=np.asarray(loss_diff,dtype=float); n=len(a); a=a-a.mean();denom=np.dot(a,a)
    if denom<1e-15:return n
    rho=[np.dot(a[k:],a[:-k])/denom for k in range(1,min(max_lag,n-1)+1)]
    inflation=max(1.0,1+2*sum((1-k/n)*r for k,r in enumerate(rho,start=1)))
    return float(n/inflation)


def figsave(name):
    plt.tight_layout();plt.savefig(ROOT/'figures'/name,dpi=135,bbox_inches='tight');plt.close()


def make_figures(raw,p,o,sc,placebo,boot,weights,rob):
    plt.figure(figsize=(10,4));
    for c in ['hospital','ambulatory','home','nursing']:plt.plot(raw.date,raw[c]/raw[c].iloc[0]*100,label=c)
    plt.legend(ncol=4);plt.ylabel('Index (Jan 2010=100)');plt.title('01 | Sector employment levels — fixed 2026 snapshot');figsave('01_sector_levels.png')
    plt.figure(figsize=(10,4));
    for c in ['g_hospital','g_outpatient_nonhome','g_nursing']:plt.plot(p.date,p[c],label=c)
    plt.axhline(0,color='gray',lw=.7);plt.legend();plt.ylabel('YoY log growth (pp)');plt.title('02 | Available-at-formation growth rates');figsave('02_growth_rates.png')
    plt.figure(figsize=(10,4));plt.plot(p.date,p.factor,label='factor');plt.plot(p.date,p.target/10,label='target/10',alpha=.75);plt.legend();plt.title('03 | Factor and 6-month-ahead hospital employment growth');figsave('03_factor_target.png')
    plt.figure(figsize=(6,4));plt.scatter(p.factor,p.target,s=13,alpha=.55);plt.xlabel('Fixed factor');plt.ylabel('Future hospital YoY growth (log pp)');plt.title('04 | Unconditional association, not causality');figsave('04_scatter.png')
    plt.figure(figsize=(8,4));plt.bar(sc.model,sc.rmse_log_pp);plt.xticks(rotation=40,ha='right');plt.ylabel('OOS RMSE (log pp)');plt.title('05 | Matched-origin model scorecard');figsave('05_scorecard.png')
    plt.figure(figsize=(10,4));plt.plot(o.date,o.target,label='actual');plt.plot(o.date,o.macro_controls,label='controls');plt.plot(o.date,o.full,label='augmented',alpha=.7);plt.legend();plt.title('06 | Purged expanding-window OOS predictions');figsave('06_oos_forecasts.png')
    plt.figure(figsize=(10,3));d=(o.target-o.macro_controls)**2-(o.target-o.full)**2;plt.bar(o.date,d,width=18);plt.axhline(0,color='black',lw=.8);plt.title('07 | Paired squared-loss gain (positive favors factor)');figsave('07_paired_loss.png')
    obs=rmse(o.target,o.macro_controls)-rmse(o.target,o.full)
    plt.figure(figsize=(7,4));plt.hist(placebo,bins=40);plt.axvline(obs,color='red',lw=2,label='observed');plt.legend();plt.title('08 | 1,000 block-shuffle exploratory placebo gains');figsave('08_placebo.png')
    plt.figure(figsize=(7,4));plt.hist(boot,bins=40);plt.axvline(0,color='red',lw=2);plt.title('09 | 2,000 paired moving-block bootstrap gains');figsave('09_bootstrap.png')
    plt.figure(figsize=(7,4));plt.scatter(weights.outpatient_weight,weights.rmse_gain_log_pp,s=6,alpha=.4);plt.axhline(0,color='red');plt.xlabel('Outpatient-nonhome signal weight');plt.ylabel('RMSE gain');plt.title('10 | Exposure-weight perturbation (1,000)');figsave('10_weight_sensitivity.png')
    plt.figure(figsize=(9,4));plt.bar(rob.test,rob.gain);plt.axhline(0,color='black',lw=.8);plt.xticks(rotation=45,ha='right');plt.ylabel('Control − full RMSE');plt.title('11 | Horizon, lag, regime and rolling robustness');figsave('11_robustness.png')
    plt.figure(figsize=(10,3));plt.plot(o.date,(o.target-o.full).abs().rolling(12,min_periods=6).mean(),label='full rolling MAE');plt.plot(o.date,(o.target-o.macro_controls).abs().rolling(12,min_periods=6).mean(),label='control rolling MAE');plt.legend();plt.title('12 | 12-origin rolling absolute forecast error');figsave('12_rolling_errors.png')


def run(draws=1000,boot_draws=2000,weight_draws=1000,figures=True):
    raw=load_raw();p=make_panel(raw);o=walk_forward(p);sc=scorecard(o)
    placebo=placebo_draws(p,o,draws);boot=bootstrap_gains(o,boot_draws);weights=weight_sensitivity(p,o,weight_draws)
    rob=robustness(raw,o);loo=leave_one_year(o)
    gain=rmse(o.target,o.macro_controls)-rmse(o.target,o.full)
    # Time-series rank association is not equity cross-sectional IC.
    temporal_rank_corr=float(p[['factor','target']].corr(method='spearman').iloc[0,1])
    metrics={'status':'REPRODUCED RETROSPECTIVE HOSPITAL-EMPLOYMENT MACRO FALSIFICATION — NOT PIT / NOT EQUITY ALPHA',
        'raw_rows':len(raw),'panel_rows':len(p),'oos_origins':len(o),'first_oos':str(o.date.iloc[0].date()),'last_oos':str(o.date.iloc[-1].date()),
        'raw_sha256':EXPECTED_SHA,'lag_months':2,'horizon_months':6,'target_release_buffer_months':1,
        'macro_rmse':rmse(o.target,o.macro_controls),'full_rmse':rmse(o.target,o.full),'gain_log_pp':gain,
        'mean_rmse':rmse(o.target,o['mean']),'persistence_rmse':rmse(o.target,o.persistence),'ar_rmse':rmse(o.target,o.ar_ridge),
        'placebo_draws':len(placebo),'placebo_right_tail_fraction':float((1+(placebo>=gain).sum())/(len(placebo)+1)),
        'bootstrap_draws':len(boot),'bootstrap_gain_ci95':np.quantile(boot,[.025,.975]).tolist(),
        'weight_draws':len(weights),'weight_positive_fraction':float((weights.rmse_gain_log_pp>0).mean()),
        'effective_loss_n':effective_n((o.target-o.macro_controls)**2-(o.target-o.full)**2),
        'temporal_rank_corr_not_equity_ic':temporal_rank_corr,
        'historical_publication_vintages':'UNKNOWN — NOT PIT','security_total_returns':'NOT AVAILABLE','firm_level_OOS':'NOT AVAILABLE'}
    for name,obj in [('derived_formation_panel.csv',p)]:obj.to_csv(ROOT/'data'/name,index=False,float_format='%.12g')
    for name,obj in [('walk_forward_oos.csv',o),('scorecard.csv',sc),('robustness.csv',rob),('leave_one_year_out.csv',loo),('exposure_weight_draws.csv',weights)]:obj.to_csv(ROOT/'results'/name,index=False,float_format='%.12g')
    pd.DataFrame({'gain_log_pp':placebo}).to_csv(ROOT/'results'/'block_placebo_draws.csv',index=False)
    pd.DataFrame({'gain_log_pp':boot}).to_csv(ROOT/'results'/'bootstrap_draws.csv',index=False)
    (ROOT/'results'/'metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False)+'\n')
    if figures:make_figures(raw,p,o,sc,placebo,boot,weights,rob)
    return metrics

if __name__=='__main__':
    m=run();print(json.dumps(m,indent=2))
