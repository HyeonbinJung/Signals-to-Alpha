"""Frozen-vintage, retrospective IEA EV infrastructure lead-indicator study.

Research-only. A 2024 snapshot is NOT a historical point-in-time dataset.
No securities, P&L, or tradable alpha are evaluated.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'iea_ev_2024_selected.csv'
NUM_CONTROL = ['share_l1', 'delta_l1', 'year_trend']
CHARGING = ['fast_log_growth_l1', 'slow_log_growth_l1', 'fast_mix_l1']
ALPHA = 10.0  # ex ante fixed, no grid search
OOS_START = 2018


def read_data(path=DATA):
    d = pd.read_csv(path)
    req = {'country','year','ev_sales_share_pct','public_fast_points','public_slow_points'}
    assert req.issubset(d.columns), 'Missing columns'
    assert not d.duplicated(['country','year']).any(), 'Duplicate country-year'
    assert d.country.nunique() == 16, 'Frozen research universe changed'
    assert d[['ev_sales_share_pct','public_fast_points','public_slow_points']].notna().all().all()
    assert d.ev_sales_share_pct.between(0,100).all()
    assert (d[['public_fast_points','public_slow_points']]>=0).all().all()
    return d.sort_values(['country','year']).reset_index(drop=True)


def panel(data, horizon=1, stale=False):
    """At year t, only t-1 (and earlier) features; predict t annual sales-share change.

    horizon=2 tests a two-year outcome share(t+1)-share(t-1) with
    t-1 features. This is a different target and NOT comparable in level to h=1.
    """
    d = data.sort_values(['country','year']).copy()
    g = d.groupby('country',sort=False)
    for v in ['ev_sales_share_pct','public_fast_points','public_slow_points']:
        for lag in [1,2,3]:
            d[f'{v}_l{lag}'] = g[v].shift(lag)
    d['share_l1'] = d.ev_sales_share_pct_l1
    d['delta_l1'] = d.ev_sales_share_pct_l1-d.ev_sales_share_pct_l2
    d['year_trend'] = d.year-2011
    offset = 2 if stale else 1
    d['fast_log_growth_l1'] = np.log1p(d[f'public_fast_points_l{offset}'])-np.log1p(d[f'public_fast_points_l{offset+1}'])
    d['slow_log_growth_l1'] = np.log1p(d[f'public_slow_points_l{offset}'])-np.log1p(d[f'public_slow_points_l{offset+1}'])
    d['fast_mix_l1'] = d[f'public_fast_points_l{offset}']/(d[f'public_fast_points_l{offset}']+d[f'public_slow_points_l{offset}'])
    if horizon==1:
        d['target_pp'] = d.ev_sales_share_pct-d.ev_sales_share_pct_l1
    elif horizon==2:
        # 2-year cumulative target with features at t-1, target t+1, and
        # training embargo enforced by horizon in walk-forward.
        d['target_pp'] = g.ev_sales_share_pct.shift(-1)-d.ev_sales_share_pct_l1
    else:
        raise ValueError('horizon must be 1 or 2')
    cols=['share_l1','delta_l1','year_trend']+CHARGING+['target_pp']
    d=d.replace([np.inf,-np.inf],np.nan).dropna(subset=cols).copy()
    return d.sort_values(['year','country']).reset_index(drop=True)


def make_model(features):
    prep=ColumnTransformer([
        ('numeric',StandardScaler(),features),
        ('country',OneHotEncoder(handle_unknown='ignore',sparse_output=False),['country'])
    ],remainder='drop')
    return Pipeline([('preprocess',prep),('ridge',Ridge(alpha=ALPHA))])


def walk_forward(d,horizon=1,first=OOS_START):
    rows=[]
    for year in sorted(d.year.unique()):
        if year<first: continue
        # Label for train origin u is published after its target year.
        # h=1: u <= year-1; h=2: u <= year-2.
        train=d[d.year<=year-horizon]
        test=d[d.year==year]
        if len(train)<30 or test.empty: continue
        target=train.target_pp.to_numpy()
        glob=float(target.mean())
        bycountry=train.groupby('country').target_pp.mean()
        preds={'mean':np.repeat(glob,len(test)),
               'country_mean':test.country.map(bycountry).fillna(glob).to_numpy(),
               'momentum':test.delta_l1.to_numpy()}
        for name,features in {
            'controls':NUM_CONTROL,
            'full':NUM_CONTROL+CHARGING,
            'no_fast':NUM_CONTROL+CHARGING[1:],
            'no_slow':NUM_CONTROL+[CHARGING[0],CHARGING[2]],
            'no_mix':NUM_CONTROL+CHARGING[:2]
        }.items():
            model=make_model(features)
            model.fit(train[features+['country']],target)
            preds[name]=model.predict(test[features+['country']])
        for i,(_,r) in enumerate(test.iterrows()):
            item={'country':r.country,'year':int(year),'actual':float(r.target_pp),'charger_score':float(0.5*np.tanh(r.fast_log_growth_l1)+0.5*np.tanh(r.slow_log_growth_l1))}
            for k,v in preds.items():item[k]=float(v[i])
            rows.append(item)
    return pd.DataFrame(rows)


def metrics(oos,cols=('mean','country_mean','momentum','controls','full','no_fast','no_slow','no_mix')):
    out={}
    for name in cols:
        if name not in oos.columns:continue
        err=oos[name]-oos.actual
        out[name]={'n':int(len(err)),'rmse_pp':float(np.sqrt(np.mean(err**2))),
                   'mae_pp':float(np.mean(np.abs(err))),
                   'bias_pp':float(np.mean(err))}
    return out


def country_leaveout(oos):
    rows=[]
    for country in sorted(oos.country.unique()):
        z=oos[oos.country!=country]
        m=metrics(z,('controls','full'))
        rows.append({'removed':country,'n':len(z),'delta_rmse_control_minus_full':m['controls']['rmse_pp']-m['full']['rmse_pp']})
    return pd.DataFrame(rows)


def regime(oos):
    groups={'pre_covid_2018_2019':oos.year<=2019,
            'covid_2020_2021':oos.year.between(2020,2021),
            'post_2022_2023':oos.year>=2022,
            'without_Norway':oos.country!='Norway',
            'without_China':oos.country!='China',
            'without_Norway_China':~oos.country.isin(['Norway','China'])}
    return {k:{'n':int(v.sum()),'delta_rmse':metrics(oos[v],('controls','full'))['controls']['rmse_pp']-metrics(oos[v],('controls','full'))['full']['rmse_pp']} for k,v in groups.items() if v.sum()>0}


def per_year_rank_ic(oos):
    rows=[]
    for year,g in oos.groupby('year'):
        ic=float(spearmanr(g.charger_score,g.actual).statistic) if g.charger_score.nunique()>1 and g.actual.nunique()>1 else np.nan
        rows.append({'year':int(year),'n':len(g),'rank_ic':ic})
    return pd.DataFrame(rows)


def year_block_bootstrap(oos,draws=2000,seed=17):
    """Sample entire calendar-year clusters; only six OOS year clusters: exploratory."""
    rng=np.random.default_rng(seed);years=np.array(sorted(oos.year.unique()))
    blocks={y:oos[oos.year==y] for y in years}
    diffs=np.empty(draws)
    for b in range(draws):
        z=pd.concat([blocks[y] for y in rng.choice(years,size=len(years),replace=True)],ignore_index=True)
        m=metrics(z,('controls','full'))
        diffs[b]=m['controls']['rmse_pp']-m['full']['rmse_pp']
    return {'draws':draws,'ci_95_rmse_improvement_pp':list(map(float,np.quantile(diffs,[.025,.975]))),'prob_improvement_exploratory':float((diffs>0).mean())}


def weight_perturbation(oos,draws=1000,seed=17):
    rng=np.random.default_rng(seed)
    # OOS records are paired with original lagged charging components from panel,
    # and rank IC is descriptive only, not an investable return metric.
    d=panel(read_data())
    z=oos[['country','year','actual']].merge(d[['country','year','fast_log_growth_l1','slow_log_growth_l1']],on=['country','year'],validate='one_to_one')
    results=[]
    for w in rng.uniform(.2,.8,draws):
        z['score']=w*np.tanh(z.fast_log_growth_l1)+(1-w)*np.tanh(z.slow_log_growth_l1)
        ics=[spearmanr(g.score,g.actual).statistic for _,g in z.groupby('year') if g.score.nunique()>1]
        results.append(float(np.mean(ics)))
    return {'draws':draws,'weight_range':[.2,.8], 'mean_rank_ic_median':float(np.median(results)), 'mean_rank_ic_p05_p95':list(map(float,np.quantile(results,[.05,.95])))}


def placebo(oos,base_panel,draws=1000,seed=17):
    """Year-stratified charging-triplet shuffle, full ridge refit; exploratory only.

    Uses algebraically equivalent centered ridge closed form to avoid 6000 slow
    sklearn preprocessing fits. Train-only scalers and one-hot country controls.
    """
    rng=np.random.default_rng(seed)
    obs=metrics(oos,('controls','full'))
    observed=obs['controls']['rmse_pp']-obs['full']['rmse_pp']
    d=base_panel.reset_index(drop=True)
    charge=d[CHARGING].to_numpy(float)
    years=sorted(oos.year.unique())
    positions=[g.index.to_numpy() for _,g in d.groupby('year',sort=True)]
    countries=sorted(d.country.unique())
    dummies=pd.get_dummies(pd.Categorical(d.country,categories=countries)).to_numpy(float)
    ctrl=d[NUM_CONTROL].to_numpy(float)
    y=d.target_pp.to_numpy(float)
    blocks=[]
    for year in years:
        tr=np.where(d.year.to_numpy()<=year-1)[0]
        te=np.where(d.year.to_numpy()==year)[0]
        c_mu=ctrl[tr].mean(0);c_sd=ctrl[tr].std(0);c_sd[c_sd==0]=1
        h_mu=charge[tr].mean(0);h_sd=charge[tr].std(0);h_sd[h_sd==0]=1
        control_train=(ctrl[tr]-c_mu)/c_sd
        control_test=(ctrl[te]-c_mu)/c_sd
        fixed_train=np.column_stack([control_train,dummies[tr]])
        fixed_test=np.column_stack([control_test,dummies[te]])
        blocks.append((tr,te,fixed_train,fixed_test,h_mu,h_sd))
    def solve_one(arr):
        pred=[]
        for tr,te,fixed_train,fixed_test,h_mu,h_sd in blocks:
            X=np.column_stack([fixed_train[:,:3],(arr[tr]-h_mu)/h_sd,fixed_train[:,3:]])
            Z=np.column_stack([fixed_test[:,:3],(arr[te]-h_mu)/h_sd,fixed_test[:,3:]])
            mx=X.mean(0);my=y[tr].mean()
            centered=X-mx
            coef=np.linalg.solve(centered.T@centered+ALPHA*np.eye(X.shape[1]),centered.T@(y[tr]-my))
            pred.extend(zip(d.iloc[te].country,d.iloc[te].year,my+(Z-mx)@coef))
        pred=pd.DataFrame(pred,columns=['country','year','pred'])
        z=oos[['country','year','actual','controls']].merge(pred,on=['country','year'],validate='one_to_one')
        return float(np.sqrt(np.mean((z.controls-z.actual)**2))-np.sqrt(np.mean((z.pred-z.actual)**2)))
    # Verify algebraic equivalence of unpermuted ridge to sklearn baseline.
    reference=solve_one(charge)
    if abs(reference-observed)>1e-7:
        raise AssertionError(f'Fast placebo ridge solver diverges from sklearn: {reference} vs {observed}')
    results=np.empty(draws)
    for b in range(draws):
        shuffled=charge.copy()
        for ids in positions:
            shuffled[ids]=charge[rng.permutation(ids)]
        results[b]=solve_one(shuffled)
    return {'draws':draws,'observed_delta_rmse_pp':float(observed),
            'one_sided_p_exploratory':float((1+(results>=observed).sum())/(draws+1)),
            'null_q05_q50_q95':list(map(float,np.quantile(results,[.05,.5,.95]))),
            'method':'Within-year cross-country charging-feature triplet shuffle, full refit; not causal randomization',
            'null_distribution':list(map(float,results))}


def run(draws=1000,write=True):
    d=read_data();p=panel(d);oos=walk_forward(p)
    assert len(oos)>50, 'Insufficient out-of-sample data'
    m=metrics(oos)
    rank=per_year_rank_ic(oos)
    extra={
      'dataset':{'raw_rows_selected':len(d),'countries':int(d.country.nunique()),'min_year':int(d.year.min()),'max_year':int(d.year.max()),'feature_rows':len(p),'oos_n':len(oos),'oos_years':list(map(int,sorted(oos.year.unique())))},
      'metrics':m,
      'rmse_improvement_control_minus_full_pp':m['controls']['rmse_pp']-m['full']['rmse_pp'],
      'rank_ic':{'per_year':rank.to_dict(orient='records'),'mean':float(rank.rank_ic.mean())},
      'year_block_bootstrap':year_block_bootstrap(oos,draws=2000),
      'weight_perturbation':weight_perturbation(oos,draws=1000),
      'placebo':placebo(oos,p,draws=draws),
      'regimes':regime(oos),
      'stale_features':metrics(walk_forward(panel(d,stale=True)),('controls','full')),
      'horizon_two':metrics(walk_forward(panel(d,horizon=2),horizon=2),('controls','full')),
      'warnings':['2024 IEA snapshot used retrospectively for ALL earlier years; NOT vintage point-in-time',
                  'Country universe chosen for data availability; ex post selection risk',
                  'Six OOS years; overlapping shocks and common policies create cross-sectional dependence',
                  'Public charging counts endogenous to EV adoption; not a causal estimate',
                  'No company revenue, equity returns, delistings, transaction costs or investable alpha tested']}
    if write:
        res=ROOT/'results';res.mkdir(exist_ok=True)
        oos.to_csv(res/'walk_forward_oos.csv',index=False)
        p.to_csv(res/'feature_panel.csv',index=False)
        rank.to_csv(res/'year_rank_ic.csv',index=False)
        country_leaveout(oos).to_csv(res/'leave_one_country_out.csv',index=False)
        pd.DataFrame({'delta_rmse_control_minus_full_pp':extra['placebo']['null_distribution']}).to_csv(res/'placebo_null_distribution.csv',index=False)
        (res/'metrics.json').write_text(json.dumps({**extra,'placebo':{k:v for k,v in extra['placebo'].items() if k!='null_distribution'}},indent=2,ensure_ascii=False)+'\n')
    return extra,oos,p

if __name__=='__main__':
    summary,_,_=run()
    print(json.dumps({k:summary[k] for k in ['dataset','metrics','rmse_improvement_control_minus_full_pp','placebo','year_block_bootstrap']},indent=2))
