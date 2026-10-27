"""Execute and persist the U.S. basic chemicals macro-factor falsification."""
from pathlib import Path
import argparse,json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from chemicals_factor import *

ROOT=Path(__file__).resolve().parent

def run(draws=1000,boot_draws=2000,exposure_draws=1000):
    for p in ('data','results','figures'): (ROOT/p).mkdir(exist_ok=True)
    d=load_snapshot(ROOT/'data/frozen_chemicals_energy_2026-10-26.csv')
    panel=make_panel(d)
    panel.to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    oos=walk_forward(panel)
    oos.to_csv(ROOT/'results/oos_predictions.csv',index=False)
    scores=scorecard(oos)
    scores.to_csv(ROOT/'results/model_scorecard.csv',index=False)
    placebo_vals,tail,gain=placebo(panel,oos,draws=draws)
    pd.DataFrame({'gain_log_pp':placebo_vals}).to_csv(ROOT/'results/block_placebo.csv',index=False)
    boot=block_bootstrap(oos,draws=boot_draws)
    pd.DataFrame({'gain_log_pp':boot}).to_csv(ROOT/'results/block_bootstrap.csv',index=False)
    perturb=exposure_perturbation(panel,draws=exposure_draws)
    perturb.to_csv(ROOT/'results/exposure_sensitivity.csv',index=False)
    robust=[]
    for h in [3,6,12]:
        for lag in [2,4]:
            p=make_panel(d,horizon=h,feature_lag=lag)
            o=walk_forward(p,horizon=h,models={k:MODELS[k] for k in ['historical_mean','macro_controls','energy_gap_augmented']})
            robust.append({'horizon':h,'input_lag':lag,'n':len(o),'control_rmse':rmse(o.actual,o.macro_controls),'full_rmse':rmse(o.actual,o.energy_gap_augmented),'gain':rmse(o.actual,o.macro_controls)-rmse(o.actual,o.energy_gap_augmented)})
    robustness=pd.DataFrame(robust)
    robustness.to_csv(ROOT/'results/horizon_lag_sensitivity.csv',index=False)
    regime=[]
    for name,sel in [('pre_2020',oos.date<'2020-01-01'),('post_2021',oos.date>='2022-01-01'),('exclude_2020_2021',~oos.year.between(2020,2021)),('all',oos.year>0)]:
        s=oos.loc[sel]
        regime.append({'regime':name,'n':len(s),'control_rmse':rmse(s.actual,s.macro_controls),'full_rmse':rmse(s.actual,s.energy_gap_augmented),'gain':rmse(s.actual,s.macro_controls)-rmse(s.actual,s.energy_gap_augmented)})
    regimes=pd.DataFrame(regime);regimes.to_csv(ROOT/'results/regime_sensitivity.csv',index=False)
    years=[]
    for year in sorted(oos.year.unique()):
        s=oos[oos.year!=year]
        years.append({'excluded_year':year,'n':len(s),'gain':rmse(s.actual,s.macro_controls)-rmse(s.actual,s.energy_gap_augmented)})
    pd.DataFrame(years).to_csv(ROOT/'results/leave_one_year_out.csv',index=False)
    rel=walk_forward(make_panel(d),models={'historical_mean':[],'macro_controls':MODELS['macro_controls'],'energy_gap_augmented':MODELS['energy_gap_augmented']},target='relative_target')
    pd.DataFrame([{'model':k,'rmse_log_pp':rmse(rel.actual,rel[k]),'n':len(rel)} for k in ['historical_mean','macro_controls','energy_gap_augmented']]).to_csv(ROOT/'results/relative_outcome.csv',index=False)
    ablations=scores[scores.model.isin(['macro_controls','energy_gap_augmented','gas_only','oil_only','energy_gap_only'])]
    ablations.to_csv(ROOT/'results/ablations.csv',index=False)
    def savefig(name):
        plt.tight_layout();plt.savefig(ROOT/'figures'/name,dpi=120,bbox_inches='tight');plt.close()
    plt.figure(figsize=(9,4));plt.plot(d.DATE,d.CHEM,label='Basic chemicals IP');plt.plot(d.DATE,d.MANUF,label='Manufacturing IP');plt.xticks(range(0,len(d),24),d.DATE.iloc[::24],rotation=40);plt.ylabel('2017=100');plt.legend();plt.title('Real G.17 industrial production indices');savefig('01_industrial_output.png')
    plt.figure(figsize=(9,4));plt.plot(panel.date,panel.factor,label='WTI YoY − Henry Hub YoY (2m stale)');plt.axhline(0,color='black',lw=.8);plt.ylabel('log percentage points');plt.title('Predeclared relative energy-cost shock');plt.legend();savefig('02_energy_factor.png')
    plt.figure(figsize=(9,4));plt.plot(oos.date,oos.actual,label='Realized chemical YoY');plt.plot(oos.date,oos.macro_controls,label='Macro controls');plt.plot(oos.date,oos.energy_gap_augmented,label='Augmented',alpha=.75);plt.ylabel('log pp');plt.title('Purged expanding-window OOS forecasts');plt.legend();savefig('03_oos_forecast.png')
    plt.figure(figsize=(8,4));plt.bar(scores.model,scores.rmse_log_pp);plt.xticks(rotation=35,ha='right');plt.ylabel('RMSE, log pp');plt.title('OOS model comparison');savefig('04_model_rmse.png')
    plt.figure(figsize=(8,4));plt.hist(placebo_vals,bins=30);plt.axvline(gain,color='black',label='Actual gain');plt.xlabel('Control − augmented RMSE (log pp)');plt.title('Block-shuffled factor refits (exploratory)');plt.legend();savefig('05_block_placebo.png')
    plt.figure(figsize=(8,4));plt.hist(boot,bins=40);plt.axvline(0,color='black');plt.xlabel('Control − augmented RMSE (log pp)');plt.title('Paired circular-block bootstrap uncertainty');savefig('06_block_bootstrap.png')
    plt.figure(figsize=(8,4));plt.scatter(perturb.gas_weight,perturb.improvement,c=perturb.oil_weight,s=6);plt.axhline(0,color='black');plt.xlabel('Gas loading');plt.ylabel('OOS gain (log pp)');plt.title('Exposure loading sensitivity');savefig('07_exposure_sensitivity.png')
    plt.figure(figsize=(8,4));plt.plot(oos.date,(oos.actual-oos.macro_controls)**2-(oos.actual-oos.energy_gap_augmented)**2);plt.axhline(0,color='black');plt.ylabel('Squared loss difference');plt.title('Paired OOS loss differential by origin');savefig('08_loss_differential.png')
    summary={'study':'US_BASIC_CHEMICALS_ENERGY_GAP','data_start':str(d.DATE.iloc[0]),'data_end':str(d.DATE.iloc[-1]),'n_raw':len(d),'n_oos':len(oos),'start_oos':str(oos.date.iloc[0].date()),'end_oos':str(oos.date.iloc[-1].date()),'primary_gain_log_pp':gain,'bootstrap_95':[float(x) for x in np.quantile(boot,[.025,.975])],'block_shuffle_exploratory_tail':float(tail),'block_shuffle_n':draws,'bootstrap_n':boot_draws,'exposure_n':exposure_draws,'exposure_positive_fraction':float((perturb.improvement>0).mean()),'rank_ic_descriptive':block_ic(oos),'historical_vintage_verified':False,'equity_alpha_established':False}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));print(scores.to_string(index=False));print(regimes.to_string(index=False));return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--placebos',type=int,default=1000);p.add_argument('--bootstraps',type=int,default=2000);p.add_argument('--perturbations',type=int,default=1000)
    a=p.parse_args();run(a.placebos,a.bootstraps,a.perturbations)
