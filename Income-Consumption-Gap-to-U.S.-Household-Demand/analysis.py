"""Historical household-demand lead-factor falsification; NO historical PIT guarantee."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'data'; RESULTS=ROOT/'results'; FIGURES=ROOT/'figures'
SEED=20261028
BASE_HORIZON=4
MIN_TRAIN=65

def load_raw():
    df=pd.read_csv(DATA/'macrodata_statsmodels_2009_snapshot.csv')
    assert len(df)==203 and df.date.iloc[0]=='1959Q1' and df.date.iloc[-1]=='2009Q3'
    assert df.date.is_unique and not df.isna().any().any()
    for k in ['realcons','realdpi','realgdp','realinv']:
        assert (df[k]>0).all()
    return df

def build_panel(raw,horizon=4,lag=1,income_weight=1.0,cons_weight=1.0):
    """At origin t, all regressors end at t-lag; target uses t..t+h."""
    x=raw.copy()
    for col in ['realcons','realdpi','realgdp','realinv']:
        x['g_'+col]=100*(np.log(x[col])-np.log(x[col].shift(4)))
    x['dpi_growth']=x.g_realdpi.shift(lag)
    x['cons_growth']=x.g_realcons.shift(lag)
    x['gdp_growth']=x.g_realgdp.shift(lag)
    x['inv_growth']=x.g_realinv.shift(lag)
    x['unemp_change']=(x.unemp-x.unemp.shift(4)).shift(lag)
    x['factor']=income_weight*x.dpi_growth-cons_weight*x.cons_growth
    x['target']=100*(np.log(x.realcons.shift(-horizon))-np.log(x.realcons))
    x['origin']=np.arange(len(x))
    cols=['date','origin','year','quarter','factor','target','dpi_growth','cons_growth','gdp_growth','inv_growth','unemp_change']
    out=x[cols].dropna().reset_index(drop=True)
    assert len(out)>100 and out.origin.is_monotonic_increasing
    return out

def ridge_prediction(X,y,xt,alpha=2.0):
    X=np.asarray(X,dtype=float);y=np.asarray(y,dtype=float);xt=np.asarray(xt,dtype=float)
    mu=X.mean(axis=0);sd=X.std(axis=0);sd[sd<1e-12]=1
    z=(X-mu)/sd;zt=(xt-mu)/sd
    yc=y.mean();a=z.T@z+alpha*np.eye(z.shape[1]);b=z.T@(y-yc)
    beta=np.linalg.solve(a,b)
    return float(yc+zt@beta)

MODEL_FEATURES={
 'historical_mean':[],
 'consumption_persistence':['cons_growth'],
 'income_gap_only':['factor'],
 'ar_ridge':['cons_growth','unemp_change'],
 'macro_controls':['cons_growth','gdp_growth','unemp_change','inv_growth'],
 'macro_plus_factor':['cons_growth','gdp_growth','unemp_change','inv_growth','factor'],
}

def walk_forward(panel,horizon=4,min_train=MIN_TRAIN,model_features=MODEL_FEATURES):
    """Target of training origin j is known by forecast origin t only if j+h<=t."""
    origins=panel.origin.to_numpy(dtype=int)
    targets=panel.target.to_numpy(dtype=float)
    columns={c:panel[c].to_numpy(dtype=float) for c in ['factor','cons_growth','gdp_growth','inv_growth','unemp_change']}
    mats={name:np.column_stack([columns[c] for c in cols]) for name,cols in model_features.items() if cols and name!='consumption_persistence'}
    rows=[]
    for i,t in enumerate(origins):
        end=int(np.searchsorted(origins,t-horizon,side='right'))
        if end<min_train:continue
        assert origins[end-1]+horizon<=t
        y=targets[:end]
        r={'date':str(panel.date.iloc[i]),'origin':int(t),'year':int(panel.year.iloc[i]),'target':float(targets[i]),'train_n':end,'train_last_origin':int(origins[end-1])}
        for name,cols in model_features.items():
            if name=='historical_mean':pred=float(y.mean())
            elif name=='consumption_persistence':pred=float(columns['cons_growth'][i])*horizon/4
            else:pred=ridge_prediction(mats[name][:end],y,mats[name][i])
            r[name]=pred
        rows.append(r)
    result=pd.DataFrame(rows)
    assert len(result)>60
    assert (result.train_last_origin+horizon<=result.origin).all()
    return result

def rmse(y,p):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(p))**2)))
def mae(y,p):return float(np.mean(np.abs(np.asarray(y)-np.asarray(p))))

def scorecard(pred):
    out=[]
    for name in MODEL_FEATURES:
        out.append({'model':name,'n_oos':len(pred),'rmse_log_pp':rmse(pred.target,pred[name]),'mae_log_pp':mae(pred.target,pred[name]),'mean_error':float(np.mean(pred[name]-pred.target))})
    return pd.DataFrame(out).sort_values('rmse_log_pp').reset_index(drop=True)

def block_shuffle(arr,rng,block=8):
    """Permute intact non-overlapping chronological blocks; exploratory null only."""
    a=np.asarray(arr);blocks=[a[i:i+block] for i in range(0,len(a),block)]
    order=rng.permutation(len(blocks))
    return np.concatenate([blocks[j] for j in order])

def placebo(panel,observed_gain,n=1000,horizon=BASE_HORIZON):
    rng=np.random.default_rng(SEED+1);gains=[]
    for i in range(n):
        z=panel.copy();z['factor']=block_shuffle(z.factor.to_numpy(),rng,8)
        q=walk_forward(z,horizon)
        gains.append(rmse(q.target,q.macro_controls)-rmse(q.target,q.macro_plus_factor))
    a=np.asarray(gains)
    return pd.DataFrame({'draw':np.arange(1,n+1),'null_gain_log_pp':a}),float((1+np.sum(a>=observed_gain))/(n+1))

def bootstrap(pred,n=2000,block=8):
    rng=np.random.default_rng(SEED+2);N=len(pred);gains=[]
    arr=pred[['target','macro_controls','macro_plus_factor','historical_mean','ar_ridge']].to_numpy()
    for _ in range(n):
        indices=[]
        while len(indices)<N:
            st=int(rng.integers(0,N));indices.extend([(st+k)%N for k in range(block)])
        x=arr[np.asarray(indices[:N])];gains.append(rmse(x[:,0],x[:,1])-rmse(x[:,0],x[:,2]))
    return pd.DataFrame({'draw':np.arange(1,n+1),'gain_log_pp':gains})

def exposure_sensitivity(raw,n=1000):
    rng=np.random.default_rng(SEED+3);rows=[]
    for i in range(n):
        w1,w2=rng.uniform(0.7,1.3,2)
        p=build_panel(raw,income_weight=w1,cons_weight=w2)
        q=walk_forward(p)
        gain=rmse(q.target,q.macro_controls)-rmse(q.target,q.macro_plus_factor)
        rows.append({'draw':i+1,'income_weight':w1,'cons_weight':w2,'gain_log_pp':gain})
    return pd.DataFrame(rows)

def diagnostics(raw,panel,pred,score,pl,bs,ex):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    FIGURES.mkdir(exist_ok=True)
    def fig(name):plt.tight_layout();plt.savefig(FIGURES/name,dpi=125);plt.close()
    plt.figure(figsize=(10,3));plt.plot(raw.date,raw.realcons,label='Real PCE');plt.plot(raw.date,raw.realdpi,label='Real DPI');plt.xticks(range(0,len(raw),20),raw.date.iloc[::20],rotation=45);plt.legend();plt.ylabel('Chained 2005 $bn (2009 snapshot)');plt.title('Historical income and consumption levels');fig('01_income_consumption_levels.png')
    plt.figure(figsize=(10,3));plt.plot(panel.date,panel.factor);plt.axhline(0,color='gray',lw=.8);plt.xticks(range(0,len(panel),18),panel.date.iloc[::18],rotation=45);plt.title('One-quarter-stale real-income minus consumption growth');plt.ylabel('log-pp YoY');fig('02_income_gap_factor.png')
    plt.figure(figsize=(5,4));plt.scatter(panel.factor,panel.target,s=10,alpha=.55);plt.xlabel('Formation factor (log-pp)');plt.ylabel('Next four-quarter real PCE growth (log-pp)');plt.title('Exploratory factor–target association');fig('03_factor_outcome_scatter.png')
    plt.figure(figsize=(9,4));plt.bar(score.model,score.rmse_log_pp);plt.xticks(rotation=35,ha='right');plt.ylabel('RMSE (log-pp)');plt.title('Purged expanding OOS model comparison');fig('04_oos_rmse.png')
    plt.figure(figsize=(10,3));plt.plot(pred.date,pred.target,label='Actual');plt.plot(pred.date,pred.macro_controls,label='Controls',alpha=.75);plt.plot(pred.date,pred.macro_plus_factor,label='Augmented',alpha=.75);plt.xticks(range(0,len(pred),12),pred.date.iloc[::12],rotation=45);plt.legend();plt.ylabel('4Q growth log-pp');plt.title('OOS predictions');fig('05_oos_forecasts.png')
    plt.figure(figsize=(10,3));d=(pred.target-pred.macro_controls)**2-(pred.target-pred.macro_plus_factor)**2;plt.plot(pred.date,np.cumsum(d));plt.axhline(0,color='gray',lw=.8);plt.xticks(range(0,len(pred),12),pred.date.iloc[::12],rotation=45);plt.ylabel('Cumulative squared-loss difference');plt.title('Positive = augmented better');fig('06_cumulative_loss.png')
    plt.figure(figsize=(6,3));plt.hist(pl.null_gain_log_pp,bins=40);plt.axvline(rmse(pred.target,pred.macro_controls)-rmse(pred.target,pred.macro_plus_factor),color='black',label='Observed');plt.legend();plt.title('1,000 block-reordered factor placebos');fig('07_block_placebo.png')
    plt.figure(figsize=(6,3));plt.hist(bs.gain_log_pp,bins=40);plt.axvline(0,color='black');plt.title('2,000 paired moving-block bootstrap gains');fig('08_bootstrap.png')
    plt.figure(figsize=(6,3));plt.scatter(ex.income_weight-ex.cons_weight,ex.gain_log_pp,s=4,alpha=.35);plt.axhline(0,color='black');plt.title('1,000 factor weight perturbations');plt.xlabel('Income weight minus consumption weight');fig('09_exposure_sensitivity.png')

def run():
    RESULTS.mkdir(exist_ok=True);raw=load_raw();p=build_panel(raw);pred=walk_forward(p);scores=scorecard(pred)
    observed=rmse(pred.target,pred.macro_controls)-rmse(pred.target,pred.macro_plus_factor)
    pl,tail=placebo(p,observed);bs=bootstrap(pred);ex=exposure_sensitivity(raw)
    horizons=[]
    for h in [1,2,4]:
        for lag in [1,2,3]:
            pp=build_panel(raw,h,lag);q=walk_forward(pp,h)
            horizons.append({'horizon_quarters':h,'publication_buffer_quarters':lag,'n':len(q),'control_rmse':rmse(q.target,q.macro_controls),'augmented_rmse':rmse(q.target,q.macro_plus_factor),'gain':rmse(q.target,q.macro_controls)-rmse(q.target,q.macro_plus_factor)})
    regimes=[]
    for name,sel in [('pre_1984',pred.year<1984),('1984_1999',(pred.year>=1984)&(pred.year<=1999)),('2000_2009',pred.year>=2000)]:
        q=pred[sel]
        if len(q)>0:regimes.append({'regime':name,'n':len(q),'gain':rmse(q.target,q.macro_controls)-rmse(q.target,q.macro_plus_factor)})
    leave=[]
    for dec in sorted((pred.year//10*10).unique()):
        q=pred[pred.year//10*10!=dec]
        leave.append({'excluded_decade':int(dec),'n':len(q),'gain':rmse(q.target,q.macro_controls)-rmse(q.target,q.macro_plus_factor)})
    ablations=[]
    for name,cols in [('without_income', ['cons_growth','gdp_growth','unemp_change','inv_growth']),('without_unemployment',['cons_growth','gdp_growth','inv_growth','factor']),('without_gdp',['cons_growth','unemp_change','inv_growth','factor']),('factor_only',['factor'])]:
        q=walk_forward(p,model_features={'historical_mean':[],'consumption_persistence':['cons_growth'],name:cols})
        ablations.append({'model':name,'rmse':rmse(q.target,q[name]),'n':len(q)})
    assoc=float(p[['factor','target']].corr().iloc[0,1]);ci=np.quantile(bs.gain_log_pp,[.025,.975])
    metrics={'status':'REPRODUCED RETROSPECTIVE CONSUMER-DEMAND MACRO PILOT — NOT PIT / NOT INDUSTRY-SPECIFIC / NOT EQUITY ALPHA',
        'observations':len(raw),'panel_n':len(p),'n_oos':len(pred),'horizon_quarters':4,'lag_quarters':1,
        'first_oos':str(pred.date.iloc[0]),'last_oos':str(pred.date.iloc[-1]),'factor_target_corr_in_sample':assoc,
        'control_rmse':rmse(pred.target,pred.macro_controls),'augmented_rmse':rmse(pred.target,pred.macro_plus_factor),
        'gain_log_pp':observed,'placebo_tail_fraction_exploratory':tail,'bootstrap_ci95':ci.tolist(),
        'exposure_gain_positive_fraction':float(np.mean(ex.gain_log_pp>0)),'n_placebo':len(pl),'n_bootstrap':len(bs),'n_exposure':len(ex),
        'source_snapshot_asof':'2009-12-15 (FRED/BLS accessed, NOT original release vintage)',
        'pit_verified':False,'company_fundamentals_tested':False,'security_total_returns_tested':False}
    for name,df in [('derived_formation_panel',p)]:df.to_csv(DATA/(name+'.csv'),index=False)
    for name,df in [('scorecard',scores),('walk_forward_oos',pred),('block_placebo_1000',pl),('paired_block_bootstrap_2000',bs),('exposure_perturbation_1000',ex),('horizon_lag_sensitivity',pd.DataFrame(horizons)),('regime_sensitivity',pd.DataFrame(regimes)),('leave_one_decade_out',pd.DataFrame(leave)),('ablations',pd.DataFrame(ablations))]:df.to_csv(RESULTS/(name+'.csv'),index=False)
    (RESULTS/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    diagnostics(raw,p,pred,scores,pl,bs,ex)
    print(json.dumps(metrics,indent=2));print(scores.to_string(index=False))
    return metrics

if __name__=='__main__':run()
