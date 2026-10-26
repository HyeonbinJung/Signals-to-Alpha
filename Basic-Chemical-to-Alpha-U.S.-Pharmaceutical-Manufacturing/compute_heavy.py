"""Run full 1,000-draw diagnostics in independent reproducible 250-draw chunks."""
from multiprocessing import Pool
import json, hashlib
import numpy as np
import pandas as pd
from run_analysis import (ROOT,RAW,read_data,make_panel,walk_forward,score,improvement,block_placebo,block_bootstrap,exposure_sensitivity,summarize_regimes,save_figures)

def work(arg):
    kind,seed,n=arg
    if kind=='placebo':
        raw=read_data(); panel=make_panel(raw);oos=walk_forward(panel)
        return block_placebo(panel,improvement(oos),draws=n,seed=seed)[0]
    return exposure_sensitivity(read_data(),draws=n,seed=seed)

if __name__=='__main__':
    raw=read_data(); panel=make_panel(raw);oos=walk_forward(panel)
    with Pool(processes=4) as pool:
        chunks=pool.map(work,[('placebo',20261026+i,250) for i in range(4)]+[('sensitivity',20262026+i,250) for i in range(4)])
    placebo=np.concatenate(chunks[:4]);sens=pd.concat(chunks[4:],ignore_index=True)
    boot=block_bootstrap(oos,draws=2000)
    metrics={'study':'Basic Chemical to Pharma Output, U.S. 2026-10-26',
             'source_snapshot':'FRED G.17 current revised data collected 2026-10-26; NOT archival publication vintages',
             'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
             'n_months':len(raw),'start':str(raw.index.min().date()),'end':str(raw.index.max().date()),
             'oos_n':len(oos),'oos_start':str(oos.index.min().date()),'oos_end':str(oos.index.max().date()),
             'horizon_months':6,'feature_lag_months':2,'label_purge_months':8,
             'metrics':score(oos),'rmse_improvement_macro_minus_full_pp':improvement(oos),
             'regimes':summarize_regimes(oos),'robustness':{}}
    for h in (3,9):
        x=walk_forward(make_panel(raw,horizon=h),horizon=h)
        metrics['robustness'][f'horizon_{h}m']={'n':len(x),'delta_rmse':improvement(x),'scores':score(x)}
    for label,params in [('lag_3m',{'release_lag':3}),('stale_chemical_12m',{'stale':12})]:
        x=walk_forward(make_panel(raw,**params),lag=params.get('release_lag',2))
        metrics['robustness'][label]={'n':len(x),'delta_rmse':improvement(x),'scores':score(x)}
    x=walk_forward(panel,train_window=72)
    metrics['robustness']['rolling_72m']={'n':len(x),'delta_rmse':improvement(x),'scores':score(x)}
    metrics['placebo']={'method':'Exploratory 12m block alignment shuffle, not exact null p-value',
                        'draws':len(placebo),'one_sided_tail_fraction':float((1+(placebo>=improvement(oos)).sum())/(len(placebo)+1)),
                        'mean_delta':float(placebo.mean())}
    metrics['bootstrap']={'draws':len(boot),'block_months':12,'ci95':list(map(float,np.quantile(boot,[.025,.975])))}
    metrics['exposure_sensitivity']={'draws':len(sens),'fraction_positive':float((sens.rmse_improvement_pp>0).mean()),
                                     'ci95':list(map(float,np.quantile(sens.rmse_improvement_pp,[.025,.975])))}
    oos.to_csv(ROOT/'results'/'oos_forecasts.csv')
    panel.to_csv(ROOT/'data'/'derived_panel.csv')
    pd.DataFrame({'delta_rmse':placebo}).to_csv(ROOT/'results'/'placebo_1000.csv',index=False)
    pd.DataFrame({'delta_rmse':boot}).to_csv(ROOT/'results'/'bootstrap_2000.csv',index=False)
    sens.to_csv(ROOT/'results'/'exposure_1000.csv',index=False)
    metrics['figures']=save_figures(raw,panel,oos,placebo,boot,sens)
    (ROOT/'results'/'metrics.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False))
    print(json.dumps({k:v for k,v in metrics.items() if k in ['n_months','oos_n','metrics','rmse_improvement_macro_minus_full_pp','placebo','bootstrap','exposure_sensitivity','regimes','robustness']},indent=2))
