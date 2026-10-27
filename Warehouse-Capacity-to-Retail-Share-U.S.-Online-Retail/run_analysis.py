"""Run all computations and save real diagnostic charts."""
from analysis import run, ROOT
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def charts(r,root=ROOT):
    figs=root/'figures';figs.mkdir(exist_ok=True)
    def save(name):
        plt.tight_layout();plt.savefig(figs/name,format='svg');plt.close()
    raw=r['raw'];panel=r['panel'];pred=r['pred']
    plt.figure(figsize=(9,4));plt.plot(raw.observation_date,raw.ECOMPCTSA,label='E-commerce share (percentage points)');plt.axvline(pd.Timestamp('2020-01-01'),ls='--',color='gray');plt.legend();plt.title('Frozen 2026-10-26 e-commerce retail share');save('01_retail_share.svg')
    plt.figure(figsize=(9,4));plt.plot(panel.observation_date,panel.factor,label='Lagged warehouse minus total payroll YoY (log pp)');plt.axhline(0,color='gray');plt.legend();plt.title('Predefined capacity signal');save('02_capacity_factor.svg')
    plt.figure(figsize=(9,4));plt.scatter(panel.factor,panel.target,s=14,alpha=.65);plt.xlabel('Warehouse relative hiring factor (log pp)');plt.ylabel('Next two-quarter retail share change (pp)');plt.title('Descriptive scatter (NOT OOS)');save('03_scatter.svg')
    plt.figure(figsize=(9,4));dates=pd.to_datetime(pred.date);plt.plot(dates,pred.actual,label='Observed');plt.plot(dates,pred.controls,label='Controls');plt.plot(dates,pred.augmented,label='Augmented');plt.legend();plt.title('Purged expanding-window OOS predictions');save('04_oos_predictions.svg')
    sc=r['scorecard'];plt.figure(figsize=(8,4));plt.bar(sc.model,sc.rmse_pp);plt.xticks(rotation=18);plt.ylabel('RMSE (percentage points)');plt.title('Same-origin model scorecard');save('05_scorecard.svg')
    plt.figure(figsize=(9,4));plt.hist(r['null'],bins=28,alpha=.8);plt.axvline(r['summary']['observed_delta_rmse_pp'],color='black',ls='--',label='Observed');plt.legend();plt.xlabel('Control RMSE minus augmented RMSE');plt.title('1,000-refit block-shuffle exploratory null');save('06_block_placebo.svg')
    plt.figure(figsize=(9,4));plt.hist(r['bootstrap'],bins=28);plt.axvline(0,color='black',ls='--');plt.title('2,000-draw paired circular-block bootstrap');plt.xlabel('Delta RMSE (pp)');save('07_bootstrap.svg')
    plt.figure(figsize=(9,4));plt.scatter(r['perturb'].warehouse_weight,r['perturb'].delta_rmse_pp,s=8,alpha=.45);plt.axhline(0,color='black',ls='--');plt.xlabel('Warehouse exposure weight');plt.ylabel('Delta RMSE (pp)');plt.title('1,000 ex-ante exposure mixtures');save('08_exposure.svg')
    plt.figure(figsize=(9,4));plt.bar(r['regimes'].regime,r['regimes'].delta_rmse_pp);plt.axhline(0,color='black');plt.xticks(rotation=15);plt.title('Regime sensitivity');plt.ylabel('Delta RMSE (pp)');save('09_regimes.svg')
    plt.figure(figsize=(9,4));plt.plot(r['loo'].excluded_year,r['loo'].delta_rmse_pp,marker='o');plt.axhline(0,color='black',ls='--');plt.title('Leave-one-OOS-year-out sensitivity');plt.ylabel('Delta RMSE (pp)');save('10_leave_one_year_out.svg')

if __name__=='__main__':
    r=run();charts(r)
    print('Saved',len(list((ROOT/'figures').glob('*.svg'))),'computed SVG diagnostics')
