"""Generate reproducible SVG figures from frozen data and computed tables."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype']='none'
plt.rcParams['svg.hashsalt']='signals-to-alpha-20261027'
import numpy as np
import pandas as pd
from analysis import load_raw,prepare
ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
raw=load_raw(ROOT);panel=prepare(raw)
p=pd.read_csv(ROOT/'results/oos_predictions.csv')
m=pd.read_csv(ROOT/'results/baseline_scorecard.csv')
boot=pd.read_csv(ROOT/'results/bootstrap_year_blocks.csv')
placebo=pd.read_csv(ROOT/'results/block_shuffle_placebo.csv')
pert=pd.read_csv(ROOT/'results/exposure_perturbations.csv')
loo=pd.read_csv(ROOT/'results/leave_one_company_out.csv')
rank=pd.read_csv(ROOT/'results/fundamental_rank_diagnostics.csv')
rob=pd.read_csv(ROOT/'results/robustness_scenarios.csv')

def save(name):
    plt.tight_layout();plt.savefig(FIG/name,format='svg',bbox_inches='tight');plt.close()

plt.figure(figsize=(10,5))
for f,g in raw.groupby('firm'):plt.plot(g.year,np.log(g.invest),label=f,alpha=.75)
plt.title('Real firm investment (log, 1947 dollars): 1935–1954');plt.xlabel('Year');plt.ylabel('Log gross investment');plt.legend(ncol=3,fontsize=7);save('01_historical_firm_investment.svg')

plt.figure(figsize=(8,5))
for group,g in panel.groupby('group'):plt.scatter(g.q_proxy,g.log_invest-g.log_invest_lag,label=group,alpha=.4,s=18)
plt.title('Lagged market-to-capital proxy vs subsequent investment change');plt.xlabel('log(value/capital) at t−1');plt.ylabel('log(invest t / invest t−1)');plt.legend(fontsize=7);save('02_q_proxy_scatter.svg')

plt.figure(figsize=(8,5))
plt.bar(m.model,m.rmse_log);plt.title('Purged expanding-window OOS RMSE, 110 firm-years');plt.ylabel('RMSE of log investment');plt.xticks(rotation=20);save('03_oos_baseline_scorecard.svg')

by=p.groupby('year').apply(lambda x:pd.Series({'control':np.sqrt(np.mean((x.control-x.truth)**2)), 'full':np.sqrt(np.mean((x.full-x.truth)**2))}),include_groups=False)
plt.figure(figsize=(9,5));plt.plot(by.index,by.control,marker='o',label='Controls');plt.plot(by.index,by.full,marker='o',label='Plus valuation factor');plt.title('Year-level OOS forecast errors (11 firms/year)');plt.ylabel('Log RMSE');plt.xlabel('Test year');plt.legend();save('04_yearly_oos_errors.svg')

p=p.sort_values(['year','firm']);diff=(p.control-p.truth)**2-(p.full-p.truth)**2
plt.figure(figsize=(9,4));plt.plot(np.arange(1,len(diff)+1),diff.cumsum());plt.axhline(0,linestyle='--',color='black');plt.title('Cumulative paired squared-error improvement');plt.xlabel('Firm-year predictions ordered by test year');plt.ylabel('Cumulative control MSE minus full MSE');save('05_cumulative_loss_difference.svg')

obs=float(np.sqrt(np.mean((p.control-p.truth)**2))-np.sqrt(np.mean((p.full-p.truth)**2)))
plt.figure(figsize=(8,4));plt.hist(boot.rmse_improvement,bins=45);plt.axvline(obs,linestyle='--',color='black',label='Observed');plt.title('2,000 paired two-year block-bootstrap RMSE gains');plt.xlabel('Control RMSE minus full RMSE');plt.legend();save('06_bootstrap_uncertainty.svg')

plt.figure(figsize=(8,4));plt.hist(placebo.rmse_improvement,bins=45);plt.axvline(obs,linestyle='--',color='black',label='Observed');plt.title('1,000 exploratory within-firm three-year block shuffles');plt.xlabel('Control RMSE minus shuffled-factor RMSE');plt.legend();save('07_block_placebo.svg')

plt.figure(figsize=(9,5));plt.barh(loo.excluded_firm,loo.rmse_improvement);plt.axvline(0,color='black',linestyle='--');plt.title('Leave-one-company-out OOS gain');plt.xlabel('Control RMSE minus full RMSE');save('08_leave_one_company_out.svg')

plt.figure(figsize=(8,4));plt.hist(pert.rmse_improvement,bins=40);plt.axvline(0,color='black',linestyle='--');plt.title('1,000 firm-specific ±20% factor-scaling perturbations');plt.xlabel('Control RMSE minus full RMSE');save('09_exposure_perturbation.svg')

plt.figure(figsize=(9,4));plt.bar(rank.year,rank.fundamental_residual_rank_ic);plt.axhline(0,color='black',linestyle='--');plt.title('Within-year rank IC of predicted vs realized investment residuals');plt.xlabel('Test year');plt.ylabel('Spearman rho (fundamentals, NOT equity)');save('10_fundamental_rank_ic.svg')
print('saved',len(list(FIG.glob('*.svg'))),'SVG figures')
