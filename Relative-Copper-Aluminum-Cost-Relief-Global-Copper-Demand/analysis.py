"""Fixed-rule retrospective world copper-demand forecasting; 1951–1975 Gill panel.
No publication vintages or security returns are represented. Every transform is explicit.
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
RAW = BASE/'data/copper_statsmodels_0_14_6_frozen.csv'
CONTROLS = ['lag_demand_growth','lag_income_growth','lag_inventory_change']
SEED=20261027

def read_raw():
    df=pd.read_csv(RAW)
    required=['year','WORLDCONSUMPTION','COPPERPRICE','INCOMEINDEX','ALUMPRICE','INVENTORYINDEX','TIME']
    assert list(df.columns)==required
    assert len(df)==25 and df.year.tolist()==list(range(1951,1976))
    assert df[required[1:]].notna().all().all()
    assert (df[['WORLDCONSUMPTION','COPPERPRICE','INCOMEINDEX','ALUMPRICE','INVENTORYINDEX']]>0).all().all()
    assert np.allclose(df.TIME,df.year-1950)
    return df

def make_panel(raw, horizon=1, lag=1, wc=1.,wa=1.):
    """At formation year t use only values through t-lag. Outcome is C(t+h)/C(t).
    This is not a PIT claim because historical release dates are unknown.
    """
    d=raw.copy().set_index('year')
    out=[]
    for t in range(int(d.index.min())+lag+1,int(d.index.max())-horizon+1):
        past=t-lag; old=past-1
        if old not in d.index or (t+horizon) not in d.index:continue
        z=lambda name,yr:float(d.at[yr,name])
        dg=lambda name:100*np.log(z(name,past)/z(name,old))
        r={
          'formation_year':t,'target_year':t+horizon,'horizon':horizon,'lag':lag,
          'y_growth':100*np.log(z('WORLDCONSUMPTION',t+horizon)/z('WORLDCONSUMPTION',t)),
          'lag_demand_growth':dg('WORLDCONSUMPTION'),
          'lag_income_growth':dg('INCOMEINDEX'),
          'lag_inventory_change':100*(z('INVENTORYINDEX',past)-z('INVENTORYINDEX',old)),
          'lag_copper_price_growth':dg('COPPERPRICE'),
          'lag_aluminum_price_growth':dg('ALUMPRICE'),
        }
        r['relative_cost_relief']=-wc*r['lag_copper_price_growth']+wa*r['lag_aluminum_price_growth']
        r['observed_through']=past
        out.append(r)
    return pd.DataFrame(out)

def ridge_forecast(train,test,features,alpha=8.0):
    """Training-only standardization and fixed closed-form ridge with unpenalized intercept."""
    X=train[features].to_numpy(dtype=float)
    y=train.y_growth.to_numpy(dtype=float)
    xt=test[features].to_numpy(dtype=float)
    return float(_ridge_numpy(X,y,xt,alpha)[0])

def _ridge_numpy(X,y,xt,alpha=8.0):
    mu=X.mean(axis=0);sd=X.std(axis=0);sd=np.where(sd>1e-12,sd,1.0)
    A=(X-mu)/sd;T=(xt-mu)/sd
    ym=y.mean();coef=np.linalg.solve(A.T@A+alpha*np.eye(A.shape[1]),A.T@(y-ym))
    return ym+T@coef

def walk_forward(panel,first=1965,horizon=1):
    """Train labels only if target year <= origin-1 (conservative extra annual buffer)."""
    years=panel.formation_year.to_numpy(dtype=int)
    targetyears=panel.target_year.to_numpy(dtype=int)
    y=panel.y_growth.to_numpy(dtype=float)
    Xc=panel[CONTROLS].to_numpy(dtype=float)
    Xf=panel[CONTROLS+['relative_cost_relief']].to_numpy(dtype=float)
    Xs=panel[['relative_cost_relief']].to_numpy(dtype=float)
    persistence=panel.lag_demand_growth.to_numpy(dtype=float)
    through=panel.observed_through.to_numpy(dtype=int)
    records=[]
    for i,t in enumerate(years):
        if t<first:continue
        idx=np.flatnonzero((targetyears<=t-1)&(years<t))
        if len(idx)<8:continue
        p={
          'mean':float(y[idx].mean()),
          'persistence':float(persistence[i]),
          'controls':float(_ridge_numpy(Xc[idx],y[idx],Xc[i:i+1])[0]),
          'full':float(_ridge_numpy(Xf[idx],y[idx],Xf[i:i+1])[0]),
          'factor_only':float(_ridge_numpy(Xs[idx],y[idx],Xs[i:i+1])[0]),
        }
        records.append({'formation_year':int(t),'target_year':int(targetyears[i]),
                        'observed_through':int(through[i]),'last_train_target_year':int(targetyears[idx].max()),
                        'n_train':len(idx),'actual':float(y[i]),**p})
    return pd.DataFrame(records)

def score(oos):
    return pd.DataFrame([{'model':c,'n_oos':len(oos),'rmse':float(np.sqrt(np.mean((oos.actual-oos[c])**2))),
                           'mae':float(np.mean(abs(oos.actual-oos[c]))),
                           'mean_error':float(np.mean(oos[c]-oos.actual))}
                          for c in ['mean','persistence','controls','full','factor_only']])

def improvement(oos):
    return float(np.sqrt(np.mean((oos.actual-oos.controls)**2)) - np.sqrt(np.mean((oos.actual-oos.full)**2)))

def block_bootstrap(oos,draws=2000,block=3,seed=SEED):
    rng=np.random.default_rng(seed);n=len(oos)
    errs_c=(oos.actual.to_numpy()-oos.controls.to_numpy())**2
    errs_f=(oos.actual.to_numpy()-oos.full.to_numpy())**2
    rows=[]
    for i in range(draws):
        idx=[]
        while len(idx)<n:
            s=int(rng.integers(0,n));idx.extend((s+np.arange(block))%n)
        idx=np.array(idx[:n],dtype=int)
        rows.append({'draw':i+1,'rmse_gain':float(np.sqrt(np.mean(errs_c[idx]))-np.sqrt(np.mean(errs_f[idx])))})
    return pd.DataFrame(rows)

def _gain_for_signal(panel,signal,baseline_oos):
    """Refit augmented ridge at each original expanding origin; controls cached."""
    years=panel.formation_year.to_numpy(dtype=int)
    targets=panel.target_year.to_numpy(dtype=int)
    y=panel.y_growth.to_numpy(dtype=float)
    X=np.column_stack((panel[CONTROLS].to_numpy(dtype=float),signal))
    pred=[]
    for t in baseline_oos.formation_year.to_numpy(dtype=int):
        i=np.flatnonzero(years==t)[0]
        train=np.flatnonzero((targets<=t-1)&(years<t))
        pred.append(float(_ridge_numpy(X[train],y[train],X[i:i+1])[0]))
    truth=baseline_oos.actual.to_numpy(dtype=float)
    controls=baseline_oos.controls.to_numpy(dtype=float)
    return float(np.sqrt(np.mean((truth-controls)**2))-np.sqrt(np.mean((truth-np.asarray(pred))**2)))

def block_shuffle_placebo(panel,observed,draws=1000,block=3,seed=SEED):
    """Exploratory block reorder of signal; not an exact exchangeability test."""
    rng=np.random.default_rng(seed);vals=panel.relative_cost_relief.to_numpy()
    blocks=[vals[i:i+block] for i in range(0,len(vals),block)]
    base_oos=walk_forward(panel)
    rows=[]
    for i in range(draws):
        order=rng.permutation(len(blocks));shuffled=np.concatenate([blocks[j] for j in order])
        rows.append({'draw':i+1,'rmse_gain':_gain_for_signal(panel,shuffled,base_oos)})
    return pd.DataFrame(rows)

def exposure_sensitivity(raw,draws=1000,seed=SEED):
    rng=np.random.default_rng(seed);rows=[]
    base=make_panel(raw);oos=walk_forward(base)
    cu=base.lag_copper_price_growth.to_numpy();al=base.lag_aluminum_price_growth.to_numpy()
    for i in range(draws):
        wc=float(rng.uniform(.75,1.25));wa=float(rng.uniform(.75,1.25))
        signal=-wc*cu+wa*al
        rows.append({'draw':i+1,'copper_weight':wc,'aluminum_weight':wa,
                     'rmse_gain':_gain_for_signal(base,signal,oos)})
    return pd.DataFrame(rows)

def leave_one_year_out(oos):
    return pd.DataFrame([{'excluded_year':int(y),'n_oos':len(oos)-1,'rmse_gain':improvement(oos[oos.formation_year!=y])}
                         for y in oos.formation_year])

def scenario(raw,horizon=1,lag=1,first=1965,drop_years=(),features=None):
    panel=make_panel(raw,horizon=horizon,lag=lag)
    if drop_years:
        # Removes origins; training also excludes these years to avoid reusing shock labels.
        panel=panel[~panel.formation_year.isin(drop_years)].reset_index(drop=True)
    if features is None:
        o=walk_forward(panel,first=first,horizon=horizon)
    else:
        # A predeclared ablation with identical origins and conservative purge.
        rows=[]
        for _,r in panel[panel.formation_year>=first].iterrows():
            t=int(r.formation_year);train=panel[panel.target_year<=t-1]
            if len(train)<8:continue
            test=panel[panel.formation_year==t]
            rows.append({'formation_year':t,'actual':r.y_growth,'controls':ridge_forecast(train,test,features),
                         'full':ridge_forecast(train,test,features+['relative_cost_relief'])})
        o=pd.DataFrame(rows)
    return {'horizon':horizon,'lag':lag,'first':first,'n_oos':len(o),'rmse_gain':improvement(o) if len(o) else np.nan,
            'rmse_controls':float(np.sqrt(np.mean((o.actual-o.controls)**2))) if len(o) else np.nan,
            'rmse_full':float(np.sqrt(np.mean((o.actual-o.full)**2))) if len(o) else np.nan}

def run_all():
    raw=read_raw();panel=make_panel(raw);oos=walk_forward(panel)
    assert len(oos)>=8 and (oos.last_train_target_year<=oos.formation_year-1).all()
    (BASE/'results').mkdir(exist_ok=True);(BASE/'data').mkdir(exist_ok=True)
    panel.to_csv(BASE/'data/derived_formation_panel.csv',index=False)
    oos.to_csv(BASE/'results/oos_predictions.csv',index=False)
    sc=score(oos);sc.to_csv(BASE/'results/scorecard.csv',index=False)
    boot=block_bootstrap(oos);boot.to_csv(BASE/'results/block_bootstrap_2000.csv',index=False)
    placebo=block_shuffle_placebo(panel,improvement(oos));placebo.to_csv(BASE/'results/block_shuffle_1000.csv',index=False)
    expo=exposure_sensitivity(raw);expo.to_csv(BASE/'results/exposure_perturbations_1000.csv',index=False)
    loo=leave_one_year_out(oos);loo.to_csv(BASE/'results/leave_one_year_out.csv',index=False)
    cases=[('primary',scenario(raw)),('h2',scenario(raw,horizon=2)),('h3',scenario(raw,horizon=3)),
           ('lag2',scenario(raw,lag=2)),('lag3',scenario(raw,lag=3)),
           ('no_inventory',scenario(raw,features=['lag_demand_growth','lag_income_growth'])),
           ('no_income',scenario(raw,features=['lag_demand_growth','lag_inventory_change'])),
           ('exclude_1973_1974',scenario(raw,drop_years=(1973,1974)))]
    robustness=pd.DataFrame([{'scenario':name,**x} for name,x in cases]);robustness.to_csv(BASE/'results/robustness.csv',index=False)
    regimes=[]
    for name,subset in [('1965-1969',oos[oos.formation_year<=1969]),('1970-1974',oos[oos.formation_year>=1970]),('exclude_1973_1974',oos[~oos.formation_year.isin([1973,1974])])]:
        regimes.append({'regime':name,'n_oos':len(subset),'rmse_gain':improvement(subset)})
    regimes=pd.DataFrame(regimes);regimes.to_csv(BASE/'results/regime_sensitivity.csv',index=False)
    obs=improvement(oos)
    summary={'data_years':[int(raw.year.min()),int(raw.year.max())],'n_raw':len(raw),'n_formation':len(panel),
             'n_oos':len(oos),'oos_years':[int(oos.formation_year.min()),int(oos.formation_year.max())],
             'rmse_gain_controls_minus_full':obs,
             'block_shuffle_tail_fraction_exploratory':float((1+(placebo.rmse_gain>=obs).sum())/(len(placebo)+1)),
             'bootstrap_95pct_percentiles':np.quantile(boot.rmse_gain,[.025,.975]).tolist(),
             'exposure_positive_fraction':float((expo.rmse_gain>0).mean()),
             'not_pit':True,'firm_fundamentals_tested':False,'equity_returns_tested':False,
             'model_alpha':8.0,'lag_years':1,'label_release_buffer_years':1,'permutation_draws':1000,'bootstrap_draws':2000}
    import json
    (BASE/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return raw,panel,oos,sc,boot,placebo,expo,loo,robustness,regimes,summary

if __name__=='__main__':
    import json
    out=run_all();print(json.dumps(out[-1],indent=2))
