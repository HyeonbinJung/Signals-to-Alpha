"""Retrospective digital-media relative-strength research; no investable alpha claims.
All prices are normalized Plotly demo *price* observations, not audited total returns.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

CORE = ('GOOG','AMZN','FB','NFLX')
CONTROL = ('AAPL','MSFT')
ALL = CORE + CONTROL
EXPOSURE = {'GOOG':0.95, 'AMZN':0.30, 'FB':1.00, 'NFLX':0.85}
HORIZON = 4
MOMENTUM = 8
RIDGE = 10.0
MIN_TRAIN_ORIGINS = 25


def load_prices(path: str | Path) -> pd.DataFrame:
    df=pd.read_csv(path,parse_dates=['date']).sort_values('date')
    assert df.date.is_unique and df.date.is_monotonic_increasing
    assert set(ALL).issubset(df.columns)
    assert np.isfinite(df[list(ALL)].to_numpy(float)).all()
    assert (df[list(ALL)]>0).all().all()
    assert (df.date.diff().dropna().dt.days.between(7,7)).all(), 'Weekly spacing changed'
    return df


def panel(prices:pd.DataFrame,horizon:int=4,lag:int=0,exposures:dict|None=None)->pd.DataFrame:
    """One formation per weekly close; y uses t+1 through t+h (not available at t)."""
    ex=exposures or EXPOSURE
    q=prices.reset_index(drop=True)
    lp=np.log(q[list(ALL)].to_numpy(float))
    r=np.diff(lp,axis=0,prepend=np.full((1,len(ALL)),np.nan))*100
    benchmark=lp[:,4:].mean(axis=1)
    bench_r=np.diff(benchmark,prepend=np.nan)*100
    rows=[]
    for t in range(MOMENTUM+lag,len(q)-horizon):
        bm8=100*(benchmark[t-lag]-benchmark[t-lag-MOMENTUM])
        bm4=100*(benchmark[t]-benchmark[t-4])
        bm1=100*(benchmark[t]-benchmark[t-1])
        bfuture=100*(benchmark[t+horizon]-benchmark[t])
        for j,firm in enumerate(CORE):
            x8=100*(lp[t-lag,j]-lp[t-lag-MOMENTUM,j])-bm8
            x4=100*(lp[t,j]-lp[t-4,j])-bm4
            x1=100*(lp[t,j]-lp[t-1,j])-bm1
            vol=float(np.std(r[t-3:t+1,j],ddof=1))
            # All four inputs are available at formation close t; no full-sample fit.
            rows.append({'t':t,'date':q.date.iloc[t], 'target_date':q.date.iloc[t+horizon],
                'firm':firm,'y':100*(lp[t+horizon,j]-lp[t,j])-bfuture,
                'lag4':x4,'lag1':x1,'vol4':vol,'bench8':bm8,
                'rel8':x8,'exposure':ex[firm],
                'factor':ex[firm]*np.tanh(x8/20.0),
                'lag4_y':x4,'benchmark_future':bfuture})
    return pd.DataFrame(rows)


def feature_matrix(df:pd.DataFrame,model:str='augmented')->np.ndarray:
    # Fixed security identity intercepts are controls, not forward-estimated exposures.
    dummies=np.column_stack([(df.firm.to_numpy()==f).astype(float) for f in CORE[1:]])
    if model=='mean':return np.empty((len(df),0))
    if model=='persistence':return df[['lag4_y']].to_numpy(float)
    if model=='momentum':return df[['rel8']].to_numpy(float)
    if model=='factor_only':return df[['factor']].to_numpy(float)
    features=['lag4','lag1','vol4','bench8']
    if model=='no_vol':features.remove('vol4')
    if model=='no_bench':features.remove('bench8')
    if model=='no_lag1':features.remove('lag1')
    if model=='augmented':features=features+['factor']
    if model not in ('control','augmented','no_vol','no_bench','no_lag1','no_dummies'):
        raise ValueError(model)
    X=df[features].to_numpy(float)
    return X if model=='no_dummies' else np.column_stack([X,dummies])


def ridge_fit_predict(X:np.ndarray,y:np.ndarray,Xnew:np.ndarray,alpha:float=RIDGE)->np.ndarray:
    """Train-only z-score with zero-variance safety, unpenalized intercept."""
    if X.shape[1]==0:return np.full(Xnew.shape[0],float(np.mean(y)))
    mu=X.mean(axis=0)
    sd=X.std(axis=0,ddof=0)
    sd=np.where(sd<1e-12,1,sd)
    Z=(X-mu)/sd
    Zn=(Xnew-mu)/sd
    ym=y.mean()
    coef=np.linalg.solve(Z.T@Z+alpha*np.eye(Z.shape[1]),Z.T@(y-ym))
    return ym+Zn@coef


def walk_forward(df:pd.DataFrame,models:tuple[str,...]=('mean','persistence','momentum','factor_only','control','augmented'),
                 min_train:int=MIN_TRAIN_ORIGINS,rolling:int|None=None,exclude:tuple[str,...]=())->pd.DataFrame:
    data=df.loc[~df.firm.isin(exclude)].copy().sort_values(['t','firm'])
    origins=sorted(data.t.unique())
    out=[]
    for t in origins:
        # Explicit release/target purge: training outcome ends no later than formation t.
        train=data.loc[data.t+int((data.target_date-data.date).dt.days.mode().iloc[0]/7) <= t] if False else None
        # All panel rows have same target horizon; infer integer target offset from first row's dates.
        h=int(round((data.target_date.iloc[0]-data.date.iloc[0]).days/7))
        train=data.loc[data.t+h<=t]
        if rolling is not None:train=train.loc[train.t>=t-h-rolling+1]
        if train.t.nunique()<min_train:continue
        test=data.loc[data.t==t]
        for model in models:
            if model=='persistence':pred=test.lag4_y.to_numpy(float) # transparent no-fit baseline
            elif model=='momentum':pred=test.rel8.to_numpy(float) # raw momentum, no fit
            else:
                X=feature_matrix(train,model);Xnew=feature_matrix(test,model)
                pred=ridge_fit_predict(X,train.y.to_numpy(float),Xnew)
            for row,yp in zip(test.itertuples(index=False),pred):
                out.append({'date':row.date,'target_date':row.target_date,'t':t,'firm':row.firm,
                            'model':model,'y':row.y,'prediction':float(yp),'error':row.y-float(yp),
                            'train_origins':train.t.nunique(),'train_rows':len(train),'horizon':h})
    return pd.DataFrame(out)


def scorecard(oos:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for m,g in oos.groupby('model'):
        y=g.y.to_numpy(float);p=g.prediction.to_numpy(float)
        rows.append({'model':m,'n_predictions':len(g),'n_origins':g.t.nunique(),
                     'rmse_pp':float(np.sqrt(np.mean((y-p)**2))),
                     'mae_pp':float(np.mean(np.abs(y-p))),
                     'direction_accuracy':float(np.mean(np.sign(y)==np.sign(p)))})
    return pd.DataFrame(rows).sort_values('rmse_pp')


def paired_improvement(oos:pd.DataFrame,a:str='control',b:str='augmented')->float:
    piv=oos.pivot_table(index=['t','firm'],columns='model',values=['y','prediction'])
    y=piv['y'][a].to_numpy();a_pred=piv['prediction'][a].to_numpy();b_pred=piv['prediction'][b].to_numpy()
    return float(np.sqrt(np.mean((y-a_pred)**2))-np.sqrt(np.mean((y-b_pred)**2)))


def rank_diagnostics(oos:pd.DataFrame,model:str='augmented')->pd.DataFrame:
    g=oos.loc[oos.model==model]
    out=[]
    for t,grp in g.groupby('t'):
        if len(grp)<3:continue
        rho=float(spearmanr(grp.prediction,grp.y).statistic)
        s=grp.sort_values('prediction')
        out.append({'t':t,'date':grp.date.iloc[0],'rank_ic':rho,
                    'spread_pp':float(s.y.iloc[-1]-s.y.iloc[0]),
                    'long':s.firm.iloc[-1],'short':s.firm.iloc[0]})
    return pd.DataFrame(out)


def block_shuffle_factor(df:pd.DataFrame,rng:np.random.Generator,block:int=4)->pd.DataFrame:
    """Within-firm non-overlapping contiguous feature blocks permuted in time.
    Not a valid exact permutation test under arbitrary nonstationarity.
    """
    d=df.copy()
    for firm,ind in d.groupby('firm',sort=False).groups.items():
        ids=np.array(sorted(ind))
        x=d.loc[ids,'factor'].to_numpy()
        chunks=[x[i:i+block] for i in range(0,len(x),block)]
        # equal-sized full blocks shuffled, remainder fixed to avoid length mismatch
        full=len(x)//block
        chunks0=np.array(chunks[:full]);order=rng.permutation(full)
        shuffled=chunks0[order].reshape(-1)
        if len(x)%block:shuffled=np.r_[shuffled,x[full*block:]]
        d.loc[ids,'factor']=shuffled
    return d


def placebo(df:pd.DataFrame,n:int=1000,seed:int=20261028)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    out=[]
    for k in range(n):
        d=block_shuffle_factor(df,rng)
        o=walk_forward(d,models=('control','augmented'))
        out.append({'draw':k,'rmse_improvement_pp':paired_improvement(o)})
    return pd.DataFrame(out)


def moving_block_bootstrap(oos:pd.DataFrame,n:int=2000,block:int=4,seed:int=20261029)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    p=oos.pivot_table(index=['t','firm'],columns='model',values=['y','prediction'])
    t=sorted(p.index.get_level_values(0).unique());A=[];B=[]
    for k in t:
        g=p.loc[k];y=g['y']['control'].to_numpy(float)
        A.append((y-g['prediction']['control'].to_numpy(float))**2)
        B.append((y-g['prediction']['augmented'].to_numpy(float))**2)
    A=np.array(A);B=np.array(B);N=len(t)
    out=[]
    for i in range(n):
        picks=[]
        while len(picks)<N:
            start=int(rng.integers(0,N))
            picks.extend([(start+j)%N for j in range(block)])
        ix=np.array(picks[:N]);out.append({'draw':i,'rmse_improvement_pp':float(np.sqrt(A[ix].mean())-np.sqrt(B[ix].mean()))})
    return pd.DataFrame(out)


def exposure_sensitivity(df:pd.DataFrame,n:int=1000,seed:int=20261030)->pd.DataFrame:
    rng=np.random.default_rng(seed);res=[]
    # Baseline is identical across draws. Vary analyst weights without re-optimizing.
    base_o=walk_forward(df,models=('control',))
    base_rmse=float(scorecard(base_o).rmse_pp.iloc[0])
    for i in range(n):
        weights={f:float(np.clip(EXPOSURE[f]+rng.normal(0,.18),.05,1.0)) for f in CORE}
        d=df.copy();d['factor']=d.apply(lambda row:weights[row.firm]*np.tanh(row.rel8/20),axis=1)
        aug=walk_forward(d,models=('augmented',))
        rmse=float(scorecard(aug).rmse_pp.iloc[0])
        res.append({'draw':i,'improvement_pp':base_rmse-rmse,**{f:weights[f] for f in CORE}})
    return pd.DataFrame(res)


def regime_table(oos:pd.DataFrame)->pd.DataFrame:
    a=oos[oos.model.isin(['control','augmented'])].copy()
    a['regime']=pd.cut(a.date,bins=[pd.Timestamp('2018-01-01'),pd.Timestamp('2019-01-01'),pd.Timestamp('2019-07-01'),pd.Timestamp('2020-01-01')],labels=['2018','2019H1','2019H2'],right=False)
    rows=[]
    for period,g in a.groupby('regime',observed=True):
        if g.empty:continue
        rows.append({'regime':str(period),'origins':g.t.nunique(),'predictions_per_model':len(g[g.model=='control']),
                     'rmse_improvement_pp':paired_improvement(g)})
    return pd.DataFrame(rows)


def compute_all(prices:pd.DataFrame,heavy:bool=True)->dict:
    df=panel(prices)
    oos=walk_forward(df)
    scores=scorecard(oos)
    ic=rank_diagnostics(oos)
    place=fast_placebo(df) if heavy else pd.DataFrame()
    boot=moving_block_bootstrap(oos) if heavy else pd.DataFrame()
    expo=fast_exposure_sensitivity(df) if heavy else pd.DataFrame()
    leave=[]
    for f in CORE:
        p=walk_forward(df,models=('control','augmented'),exclude=(f,))
        leave.append({'excluded':f,'n_predictions_per_model':len(p[p.model=='control']),'improvement_pp':paired_improvement(p)})
    alternatives=[]
    for h in (2,4,8):
        for lag in (0,1):
            d=panel(prices,horizon=h,lag=lag)
            o=walk_forward(d,models=('control','augmented'))
            alternatives.append({'horizon_weeks':h,'signal_lag_weeks':lag,'n_origins':o.t.nunique(),
                                 'improvement_pp':paired_improvement(o)})
    ablations=[]
    for model in ('no_vol','no_bench','no_lag1','no_dummies'):
        p=walk_forward(df,models=('control',model))
        ablations.append({'ablation':model,'n_origins':p.t.nunique(),
                          'rmse_improvement_vs_control_pp':paired_improvement(p,'control',model)})
    roll=walk_forward(df,models=('control','augmented'),rolling=40,min_train=20)
    summary={'n_raw_weeks':len(prices),'n_panel_rows':len(df),'n_oos_origins':oos.t.nunique(),
             'n_oos_predictions_per_model':len(oos[oos.model=='control']),
             'control_rmse_pp':float(scores.set_index('model').loc['control','rmse_pp']),
             'augmented_rmse_pp':float(scores.set_index('model').loc['augmented','rmse_pp']),
             'improvement_pp':paired_improvement(oos),
             'rank_ic_mean':float(ic.rank_ic.mean()),'rank_spread_mean_pp':float(ic.spread_pp.mean()),
             'rank_spread_net_20bps_roundtrip_pp':float(ic.spread_pp.mean()-0.20),
             'placebo_upper_tail_fraction':float((1+np.sum(place.rmse_improvement_pp>=paired_improvement(oos)))/(1+len(place))) if heavy else None,
             'bootstrap_ci_95_pp':[float(x) for x in np.quantile(boot.rmse_improvement_pp,[.025,.975])] if heavy else None,
             'exposure_positive_fraction':float((expo.improvement_pp>0).mean()) if heavy else None,
             'rolling_40wk_improvement_pp':paired_improvement(roll),
             'status':'REPRODUCED RETROSPECTIVE PRICE-RETURN PILOT — NOT PIT / NOT TOTAL RETURN / NOT INVESTABLE ALPHA',
             'publication_vintage':'UNKNOWN','total_return_adjustment':'UNKNOWN'}
    return dict(panel=df,oos=oos,scorecard=scores,ic=ic,placebo=place,bootstrap=boot,exposure=expo,
                leave_one_firm=pd.DataFrame(leave),alternatives=pd.DataFrame(alternatives),
                ablations=pd.DataFrame(ablations),regimes=regime_table(oos),rolling=roll,summary=summary)

class FastRefit:
    """Exact numpy equivalent of expanding OOS augmented regression, cached splits."""
    def __init__(self,df:pd.DataFrame,horizon:int=4,min_train:int=MIN_TRAIN_ORIGINS):
        self.df=df.sort_values(['t','firm']).reset_index(drop=True)
        self.y=self.df.y.to_numpy(float)
        self.Xbase=feature_matrix(self.df,'control')
        self.t=self.df.t.to_numpy(int)
        self.origins=[];self.splits=[]
        for t in sorted(self.df.t.unique()):
            tr=np.flatnonzero(self.t+horizon<=t)
            if np.unique(self.t[tr]).size<min_train:continue
            te=np.flatnonzero(self.t==t)
            self.origins.append(t);self.splits.append((tr,te))
    def augmented_predictions(self,factor:np.ndarray)->np.ndarray:
        X=np.column_stack((self.Xbase[:,:4],factor,self.Xbase[:,4:]))
        out=[]
        for tr,te in self.splits:
            out.extend(ridge_fit_predict(X[tr],self.y[tr],X[te]))
        return np.array(out)
    def actual_y(self)->np.ndarray:
        return np.concatenate([self.y[te] for tr,te in self.splits])
    def rmse(self,factor:np.ndarray)->float:
        return float(np.sqrt(np.mean((self.actual_y()-self.augmented_predictions(factor))**2)))


def fast_placebo(df:pd.DataFrame,n:int=1000,seed:int=20261028)->pd.DataFrame:
    rng=np.random.default_rng(seed);ref=FastRefit(df)
    base=walk_forward(df,models=('control',))
    base_rmse=float(scorecard(base).rmse_pp.iloc[0])
    x=ref.df.factor.to_numpy(float);out=[]
    for k in range(n):
        sh=x.copy()
        for f in CORE:
            ids=np.flatnonzero(ref.df.firm.to_numpy()==f)
            values=x[ids];block=4;full=len(values)//block
            sh[ids[:full*block]]=values[:full*block].reshape(full,block)[rng.permutation(full)].reshape(-1)
        out.append({'draw':k,'rmse_improvement_pp':base_rmse-ref.rmse(sh)})
    return pd.DataFrame(out)


def fast_exposure_sensitivity(df:pd.DataFrame,n:int=1000,seed:int=20261030)->pd.DataFrame:
    rng=np.random.default_rng(seed);ref=FastRefit(df)
    base=walk_forward(df,models=('control',))
    base_rmse=float(scorecard(base).rmse_pp.iloc[0]);f=ref.df.firm.to_numpy()
    rel=ref.df.rel8.to_numpy(float);out=[]
    for k in range(n):
        w={firm:float(np.clip(EXPOSURE[firm]+rng.normal(0,.18),.05,1.0)) for firm in CORE}
        factor=np.array([w[firm] for firm in f])*np.tanh(rel/20)
        out.append({'draw':k,'improvement_pp':base_rmse-ref.rmse(factor),**w})
    return pd.DataFrame(out)
