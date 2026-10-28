"""U.S. beef processing: lagged poultry-versus-pork supply pressure and beef output.

Strict label-availability purge under an *assumed* two-month observation lag. Historical
first-release vintages are NOT available: this is a fixed-snapshot macro pilot only.
No corporate security return inference is permitted. The only data are frozen USDA-
origin monthly meat production redistributed in plotnine, plus separately transcribed
Tyson 2023 SEC filing segment fundamentals (descriptive; not a predictive panel).
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
RAW=HERE/'data/raw_plotnine_meat_2023_snapshot.csv'
RESULTS=HERE/'results';FIGURES=HERE/'figures'
LAG=2;HORIZON=6;OOS_START='2008-01-01';MIN_TRAIN=300;ALPHA=10.0;SEED=20261028
CONTROL=['beef_yoy_lag2','beef_yoy_lag8','beef_mom3_lag2','pork_yoy_lag2']
AR=CONTROL[:3]
MODELS=['historical_mean','persistence','momentum','ar_ridge','supply_control','factor_only','augmented']

def load_raw():
    df=pd.read_csv(RAW,parse_dates=['date']).sort_values('date').reset_index(drop=True)
    expected=['date','beef','veal','pork','lamb_and_mutton','broilers','other_chicken','turkey']
    assert df.columns.tolist()==expected, 'Unexpected raw data schema'
    assert len(df)==960 and df.date.min()==pd.Timestamp('1944-01-01') and df.date.max()==pd.Timestamp('2023-12-01')
    assert df.date.is_unique and df.date.diff().dropna().dt.days.between(28,31).all()
    assert (df[['beef','pork','broilers','turkey']].dropna()>0).all().all()
    assert df.broilers.notna().sum()==768 and df.turkey.notna().sum()==768
    return df

def make_panel(raw,horizon=HORIZON,lag=LAG,broiler_weight=.7,scale=20.):
    assert horizon>=1 and lag>=1 and 0<=broiler_weight<=1 and scale>0
    df=raw.copy()
    for c in ['beef','pork','broilers','turkey']:
        df[c+'_yoy']=100*np.log(df[c]/df[c].shift(12))
        df[c+'_mom3']=100*np.log(df[c]/df[c].shift(3))
    df['beef_yoy_lag2']=df.beef_yoy.shift(lag)
    df['beef_yoy_lag8']=df.beef_yoy.shift(lag+6)
    df['beef_mom3_lag2']=df.beef_mom3.shift(lag)
    df['pork_yoy_lag2']=df.pork_yoy.shift(lag)
    df['broiler_yoy_lag2']=df.broilers_yoy.shift(lag)
    df['turkey_yoy_lag2']=df.turkey_yoy.shift(lag)
    df['poultry_mix']=broiler_weight*df.broiler_yoy_lag2+(1-broiler_weight)*df.turkey_yoy_lag2
    df['factor_raw']=df.poultry_mix-df.pork_yoy_lag2
    df['factor']=np.tanh(df.factor_raw/scale)
    df['target']=df.beef_yoy.shift(-horizon)
    df['target_date']=df.date+pd.DateOffset(months=horizon)
    df['label_available']=df.target_date+pd.DateOffset(months=lag)
    keep=['date','target_date','label_available','target','factor','factor_raw','poultry_mix']+CONTROL+['broiler_yoy_lag2','turkey_yoy_lag2']
    panel=df[keep].dropna().reset_index(drop=True)
    assert (panel.label_available>panel.date).all()
    return panel

def ridge_forecast(train,row,features,alpha=ALPHA):
    if not features:return float(train.target.mean())
    x=train[features].to_numpy(float);y=train.target.to_numpy(float)
    mu=x.mean(axis=0);sd=x.std(axis=0);sd=np.where(sd<1e-10,1.,sd)
    z=(x-mu)/sd;z0=(row[features].to_numpy(float)-mu)/sd
    ym=y.mean();coef=np.linalg.solve(z.T@z+alpha*np.eye(z.shape[1]),z.T@(y-ym))
    return float(ym+z0@coef)

def walkforward(panel,oos_start=OOS_START,min_train=MIN_TRAIN,models=None):
    models=models or MODELS;out=[]
    for _,row in panel.iterrows():
        if row.date<pd.Timestamp(oos_start):continue
        train=panel.loc[(panel.label_available<=row.date)&(panel.date<row.date)]
        if len(train)<min_train:continue
        pred={'date':row.date,'target_date':row.target_date,'target':float(row.target),'factor':float(row.factor),
              'n_train':len(train),'max_training_target_date':train.target_date.max(),
              'max_training_label_available':train.label_available.max()}
        if 'historical_mean' in models:pred['historical_mean']=float(train.target.mean())
        if 'persistence' in models:pred['persistence']=float(row.beef_yoy_lag2)
        if 'momentum' in models:pred['momentum']=float(2*row.beef_yoy_lag2-row.beef_yoy_lag8)
        if 'ar_ridge' in models:pred['ar_ridge']=ridge_forecast(train,row,AR)
        if 'supply_control' in models:pred['supply_control']=ridge_forecast(train,row,CONTROL)
        if 'factor_only' in models:pred['factor_only']=ridge_forecast(train,row,['factor'])
        if 'augmented' in models:pred['augmented']=ridge_forecast(train,row,CONTROL+['factor'])
        out.append(pred)
    return pd.DataFrame(out)

def rmse(y,p):return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(p))**2)))

def scorecard(pred):
    return pd.DataFrame([{'model':name,'n_oos':len(pred),'rmse_log_pp':rmse(pred.target,pred[name]),
       'mae_log_pp':float(np.abs(pred.target-pred[name]).mean()),
       'bias_log_pp':float((pred[name]-pred.target).mean())} for name in MODELS]).sort_values('rmse_log_pp')

def block_reorder_factor(factor,rng,block=12):
    blocks=[np.arange(i,min(i+block,len(factor))) for i in range(0,len(factor),block)]
    return np.asarray(factor)[np.concatenate([blocks[k] for k in rng.permutation(len(blocks))])]

def _fast_augmented_forecasts(panel,factor_values=None):
    """Cumulative train-only standardized ridge, algebraically equivalent to ridge_forecast."""
    x0=panel[CONTROL].to_numpy(float)
    factor=np.asarray(panel.factor if factor_values is None else factor_values,dtype=float)
    x=np.column_stack((x0,factor));y=panel.target.to_numpy(float)
    dates=panel.date.to_numpy(dtype='datetime64[ns]')
    labels=panel.label_available.to_numpy(dtype='datetime64[ns]')
    origins=np.flatnonzero(dates>=np.datetime64(OOS_START))
    cutoffs=np.searchsorted(labels,dates[origins],side='right')
    mask=cutoffs>=MIN_TRAIN;origins=origins[mask];cutoffs=cutoffs[mask]
    sx=np.vstack([np.zeros(x.shape[1]),np.cumsum(x,axis=0)])
    sx2=np.vstack([np.zeros(x.shape[1]),np.cumsum(x*x,axis=0)])
    sxx=np.concatenate([np.zeros((1,x.shape[1],x.shape[1])),np.cumsum(x[:,:,None]*x[:,None,:],axis=0)])
    sxy=np.vstack([np.zeros(x.shape[1]),np.cumsum(x*y[:,None],axis=0)])
    sy=np.concatenate([[0.],np.cumsum(y)]);out=np.empty(len(origins));eye=np.eye(x.shape[1])
    for j,(i,k) in enumerate(zip(origins,cutoffs)):
        mu=sx[k]/k;sd=np.sqrt(np.maximum(0,sx2[k]/k-mu**2));sd=np.where(sd<1e-10,1.,sd)
        ym=sy[k]/k;gram=(sxx[k]-k*np.outer(mu,mu))/np.outer(sd,sd)
        rhs=(sxy[k]-k*mu*ym)/sd;beta=np.linalg.solve(gram+ALPHA*eye,rhs)
        out[j]=ym+((x[i]-mu)/sd)@beta
    return out

def block_bootstrap_gain(pred,draws=2000,block=12,seed=SEED+1):
    rng=np.random.default_rng(seed);n=len(pred);out=np.empty(draws)
    y=pred.target.to_numpy();a=pred.supply_control.to_numpy();b=pred.augmented.to_numpy()
    for k in range(draws):
        starts=rng.integers(0,n,size=int(np.ceil(n/block)))
        ix=np.concatenate([np.arange(s,s+block)%n for s in starts])[:n]
        out[k]=rmse(y[ix],a[ix])-rmse(y[ix],b[ix])
    return out

def permutation_test(panel,observed_gain,draws=1000,block=12,seed=SEED+2):
    rng=np.random.default_rng(seed);null=np.empty(draws)
    baseline=walkforward(panel,models=['supply_control'])
    baseline_rmse=rmse(baseline.target,baseline.supply_control)
    for k in range(draws):
        shuffled=block_reorder_factor(panel.factor.to_numpy(),rng,block)
        null[k]=baseline_rmse-rmse(baseline.target,_fast_augmented_forecasts(panel,shuffled))
    tail=(1+int((null>=observed_gain).sum()))/(draws+1)
    return null,tail

def weight_sensitivity(raw,draws=1000,seed=SEED+3):
    rng=np.random.default_rng(seed);w=rng.uniform(.1,.9,size=draws)
    panel=make_panel(raw);base=walkforward(panel,models=['supply_control'])
    base_rmse=rmse(base.target,base.supply_control)
    broiler=panel.broiler_yoy_lag2.to_numpy();turkey=panel.turkey_yoy_lag2.to_numpy();pork=panel.pork_yoy_lag2.to_numpy()
    gains=np.empty(draws)
    for k,wb in enumerate(w):
        fac=np.tanh((wb*broiler+(1-wb)*turkey-pork)/20.)
        gains[k]=base_rmse-rmse(base.target,_fast_augmented_forecasts(panel,fac))
    return pd.DataFrame({'broiler_weight':w,'turkey_weight':1-w,'gain_log_pp':gains})

def alternative_checks(raw):
    rows=[]
    for lag in [1,2,3,6]:
        for h in [1,3,6,12]:
            p=make_panel(raw,horizon=h,lag=lag)
            pr=walkforward(p,models=['supply_control','augmented'])
            rows.append({'lag_months':lag,'horizon_months':h,'n_oos':len(pr),
                'control_rmse':rmse(pr.target,pr.supply_control),
                'augmented_rmse':rmse(pr.target,pr.augmented),
                'gain_log_pp':rmse(pr.target,pr.supply_control)-rmse(pr.target,pr.augmented)})
    return pd.DataFrame(rows)

def ablations(raw):
    panel=make_panel(raw)
    b=panel.broiler_yoy_lag2.to_numpy();t=panel.turkey_yoy_lag2.to_numpy();p=panel.pork_yoy_lag2.to_numpy()
    cases={'primary_70_30_poultry_minus_pork':panel.factor.to_numpy(),
           'broiler_only_minus_pork':np.tanh((b-p)/20.),
           'turkey_only_minus_pork':np.tanh((t-p)/20.),
           'poultry_only_no_pork':np.tanh((.7*b+.3*t)/20.),
           'negative_pork_only':np.tanh(-p/20.),
           'linear_unbounded_factor':panel.factor_raw.to_numpy()/20.}
    rows=[]
    for name,fac in cases.items():
        x=panel.copy();x['factor']=fac;pr=walkforward(x,models=['supply_control','augmented'])
        rows.append({'case':name,'n_oos':len(pr),'gain_log_pp':rmse(pr.target,pr.supply_control)-rmse(pr.target,pr.augmented)})
    return pd.DataFrame(rows)

def regime_checks(pred):
    masks={'2008-2014':pred.date<'2015-01-01',
           '2015-2019':pred.date.between('2015-01-01','2019-12-31'),
           '2020-2021':pred.date.between('2020-01-01','2021-12-31'),
           '2022-2023':pred.date>='2022-01-01'}
    rows=[]
    for name,mask in masks.items():
        q=pred.loc[mask]
        if len(q):rows.append({'regime':name,'n':len(q),
            'control_rmse':rmse(q.target,q.supply_control),
            'augmented_rmse':rmse(q.target,q.augmented),
            'gain_log_pp':rmse(q.target,q.supply_control)-rmse(q.target,q.augmented)})
    return pd.DataFrame(rows)

def leave_one_year_out(pred):
    rows=[]
    for year in sorted(pred.date.dt.year.unique()):
        q=pred.loc[pred.date.dt.year!=year]
        rows.append({'excluded_oos_year':int(year),'n':len(q),
                     'gain_log_pp':rmse(q.target,q.supply_control)-rmse(q.target,q.augmented)})
    return pd.DataFrame(rows)

def plot_all(raw,panel,pred,scores,placebo,boot,weights,alt,abl,regime,year,firm):
    plt.rcParams.update({'figure.figsize':(9,4.8),'font.size':10,'axes.grid':True,'grid.alpha':.22,
       'svg.hashsalt':'signals-to-alpha-beef-20261028'})
    def save(name):
        plt.tight_layout();plt.savefig(FIGURES/(name+'.svg'),format='svg',bbox_inches='tight',metadata={'Date':None});plt.close()
    fig,ax=plt.subplots();ax.plot(raw.date,raw.beef,label='Beef');ax.plot(raw.date,raw.pork,label='Pork');ax.set_ylabel('Million lb per month');ax.set_title('01 | U.S. red meat processing output');ax.legend();save('01_red_meat_output')
    fig,ax=plt.subplots();ax.plot(raw.date,raw.broilers,label='Broilers');ax.plot(raw.date,raw.turkey,label='Turkey');ax.set_ylabel('Million lb per month');ax.set_title('02 | U.S. poultry production comparators');ax.legend();save('02_poultry_output')
    fig,ax=plt.subplots();ax.plot(panel.date,panel.factor);ax.axhline(0,color='black',lw=.8);ax.set_title('03 | Fixed poultry-minus-pork pressure factor');save('03_factor_history')
    fig,ax=plt.subplots();ax.scatter(panel.factor,panel.target,s=9,alpha=.3);ax.set_xlabel('Factor at formation');ax.set_ylabel('Future beef YoY growth (log pp)');ax.set_title('04 | Factor-target exploratory scatter');save('04_scatter')
    fig,ax=plt.subplots();ax.plot(pred.date,pred.target,label='Observed future beef YoY',lw=1.1);ax.plot(pred.date,pred.supply_control,label='Supply control',alpha=.8);ax.plot(pred.date,pred.augmented,label='Augmented',alpha=.8);ax.set_title('05 | Purged expanding-window OOS');ax.legend();save('05_oos_predictions')
    fig,ax=plt.subplots();ax.barh(scores.model,scores.rmse_log_pp);ax.set_xlabel('RMSE (log pp; lower better)');ax.set_title('06 | Competing OOS baselines');save('06_rmse_scorecard')
    fig,ax=plt.subplots();d=(pred.target-pred.supply_control)**2-(pred.target-pred.augmented)**2;ax.plot(pred.date,d.cumsum()/np.arange(1,len(d)+1));ax.axhline(0,color='black',lw=.8);ax.set_title('07 | Cumulative mean paired squared-loss difference');save('07_loss_gain')
    fig,ax=plt.subplots();ax.hist(placebo,bins=35,alpha=.75);ax.axvline(rmse(pred.target,pred.supply_control)-rmse(pred.target,pred.augmented),color='red',label='Observed gain');ax.set_title('08 | 1,000 exploratory 12-month block reorders');ax.legend();save('08_placebo')
    fig,ax=plt.subplots();ax.hist(boot,bins=40);ax.axvline(0,color='black',lw=.8);ax.set_title('09 | 2,000 paired block-bootstrap RMSE gains');save('09_bootstrap')
    fig,ax=plt.subplots();ax.scatter(weights.broiler_weight,weights.gain_log_pp,s=8,alpha=.3);ax.axhline(0,color='black',lw=.8);ax.set_xlabel('Broiler weight (turkey = 1-w)');ax.set_ylabel('RMSE gain');ax.set_title('10 | 1,000 input-weight perturbations');save('10_exposure_weights')
    fig,ax=plt.subplots();q=alt.pivot(index='lag_months',columns='horizon_months',values='gain_log_pp');mx=max(abs(q.values.min()),abs(q.values.max()));im=ax.imshow(q.values,cmap='coolwarm',aspect='auto',vmin=-mx,vmax=mx);ax.set_xticks(range(len(q.columns)),q.columns);ax.set_yticks(range(len(q.index)),q.index);ax.set_xlabel('Horizon (months)');ax.set_ylabel('Assumed release buffer (months)');ax.set_title('11 | Lag/horizon grid (post-hoc)');fig.colorbar(im,ax=ax);save('11_horizon_lag')
    fig,ax=plt.subplots();ax.bar(abl.case,abl.gain_log_pp);ax.axhline(0,color='black',lw=.8);ax.tick_params(axis='x',labelrotation=55);ax.set_title('12 | Component ablations');save('12_ablation')
    fig,ax=plt.subplots();ax.bar(regime.regime,regime.gain_log_pp);ax.axhline(0,color='black',lw=.8);ax.set_title('13 | Regime sensitivity');save('13_regime')
    fig,ax=plt.subplots();ax.bar(year.excluded_oos_year,year.gain_log_pp);ax.axhline(0,color='black',lw=.8);ax.set_title('14 | Leave-one-OOS-year-out sensitivity');save('14_leave_year_out')
    fig,ax=plt.subplots();beef=firm.loc[firm.segment=='Beef'];ax.plot(beef.fiscal_year,beef.sales_usd_millions,marker='o',label='Tyson Beef sales');ax.set_ylabel('USD million (FY ends September)');ax.set_title('15 | SEC FY2023 filing: 3-year descriptive segment sales');ax.legend();save('15_tyson_fundamentals')

def run_all(draws=1000,bootstrap_draws=2000,weight_draws=1000):
    RESULTS.mkdir(exist_ok=True);FIGURES.mkdir(exist_ok=True)
    raw=load_raw();panel=make_panel(raw);pred=walkforward(panel)
    assert len(pred)>100 and (pred.max_training_label_available<=pred.date).all()
    assert (pred.max_training_target_date<=pred.date).all()
    scores=scorecard(pred)
    gain=rmse(pred.target,pred.supply_control)-rmse(pred.target,pred.augmented)
    boot=block_bootstrap_gain(pred,draws=bootstrap_draws)
    placebo,tail=permutation_test(panel,gain,draws=draws)
    weights=weight_sensitivity(raw,draws=weight_draws)
    alt=alternative_checks(raw);abl=ablations(raw);regime=regime_checks(pred);year=leave_one_year_out(pred)
    firm=pd.read_csv(HERE/'data/tyson_fy2023_sec_fundamentals.csv')
    assert len(firm)==9 and set(firm.fiscal_year)=={2021,2022,2023}
    annual=raw.loc[raw.date.dt.year.isin([2019,2023])].groupby(raw.date.dt.year)['beef'].sum()
    metrics={'data_start':str(raw.date.min().date()),'data_end':str(raw.date.max().date()),
      'raw_n':len(raw),'beef_n':int(raw.beef.notna().sum()),'panel_n':len(panel),'oos_n':len(pred),
      'oos_start':str(pred.date.min().date()),'oos_end':str(pred.date.max().date()),
      'oos_min_train':int(pred.n_train.min()),'oos_max_train':int(pred.n_train.max()),
      'lag_months':LAG,'horizon_months':HORIZON,
      'purge_rule':'train target month + 2 months <= formation month',
      'observed_rmse_gain_log_pp':gain,'placebo_draws':draws,'placebo_exploratory_tail_fraction':tail,
      'bootstrap_draws':bootstrap_draws,'bootstrap_gain_ci_95':np.quantile(boot,[.025,.975]).tolist(),
      'weight_draws':weight_draws,'weight_positive_gain_fraction':float((weights.gain_log_pp>0).mean()),
      'factor_target_full_panel_spearman':float(panel[['factor','target']].corr(method='spearman').iloc[0,1]),
      'beef_production_2023_million_lb':float(annual.loc[2023]),
      'beef_production_2019_million_lb':float(annual.loc[2019]),
      'beef_production_2019_2023_growth_pct':float((annual.loc[2023]/annual.loc[2019]-1)*100),
      'tyson_beef_2023_sales_usd_millions':int(firm.query("segment=='Beef' and fiscal_year==2023").sales_usd_millions.iloc[0]),
      'tyson_beef_2023_operating_income_usd_millions':int(firm.query("segment=='Beef' and fiscal_year==2023").operating_income_usd_millions.iloc[0]),
      'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
      'equity_alpha_established':False,'pit_verified':False,'historical_vintage_available':False,
      'company_fundamentals_tested':False,'security_total_returns_tested':False,
      'status':'REPRODUCED RETROSPECTIVE BEEF PROCESSING MACRO PILOT - NOT PIT / NOT EQUITY ALPHA'}
    panel.to_csv(HERE/'data/derived_formation_panel.csv',index=False,float_format='%.10g')
    pred.to_csv(RESULTS/'oos_predictions.csv',index=False,float_format='%.10g')
    scores.to_csv(RESULTS/'baseline_scorecard.csv',index=False,float_format='%.10g')
    pd.DataFrame({'gain_log_pp':boot}).to_csv(RESULTS/'bootstrap_draws.csv',index=False)
    pd.DataFrame({'gain_log_pp':placebo}).to_csv(RESULTS/'placebo_draws.csv',index=False)
    weights.to_csv(RESULTS/'weight_perturbations.csv',index=False)
    alt.to_csv(RESULTS/'lag_horizon_checks.csv',index=False)
    abl.to_csv(RESULTS/'ablation_checks.csv',index=False)
    regime.to_csv(RESULTS/'regime_checks.csv',index=False)
    year.to_csv(RESULTS/'leave_one_year_out.csv',index=False)
    (RESULTS/'summary.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    plot_all(raw,panel,pred,scores,placebo,boot,weights,alt,abl,regime,year,firm)
    print(json.dumps({k:metrics[k] for k in ['raw_n','panel_n','oos_n','observed_rmse_gain_log_pp','placebo_exploratory_tail_fraction','bootstrap_gain_ci_95','weight_positive_gain_fraction']},indent=2))
    print(scores.to_string(index=False));return metrics

if __name__=='__main__':run_all()
