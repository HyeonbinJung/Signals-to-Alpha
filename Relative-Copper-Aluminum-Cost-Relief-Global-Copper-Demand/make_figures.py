"""Recreate ten empirical SVG diagnostics from frozen computed tables."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import BASE, read_raw

def main():
    f=BASE/'figures';f.mkdir(exist_ok=True)
    d=read_raw();p=pd.read_csv(BASE/'data/derived_formation_panel.csv')
    o=pd.read_csv(BASE/'results/oos_predictions.csv');s=pd.read_csv(BASE/'results/scorecard.csv')
    b=pd.read_csv(BASE/'results/block_bootstrap_2000.csv');q=pd.read_csv(BASE/'results/block_shuffle_1000.csv')
    e=pd.read_csv(BASE/'results/exposure_perturbations_1000.csv');l=pd.read_csv(BASE/'results/leave_one_year_out.csv')
    r=pd.read_csv(BASE/'results/robustness.csv');g=pd.read_csv(BASE/'results/regime_sensitivity.csv')
    def save(name,title,xlabel='',ylabel=''):
        plt.title(title);plt.xlabel(xlabel);plt.ylabel(ylabel);plt.grid(alpha=.2);plt.tight_layout()
        plt.savefig(f/name,format='svg');plt.close()
    plt.figure(figsize=(8,4));plt.plot(d.year,d.WORLDCONSUMPTION,marker='o',ms=3);save('01_copper_consumption.svg','World copper consumption (historical 1951–1975)','Year','1,000 metric tonnes')
    plt.figure(figsize=(8,4));plt.plot(d.year,d.COPPERPRICE/d.ALUMPRICE,marker='.');save('02_relative_metal_prices.svg','Copper / aluminum price ratio (historical)','Year','Unit ratio (dataset scales)')
    plt.figure(figsize=(8,4));plt.plot(p.formation_year,p.relative_cost_relief,label='Lagged relative cost relief');plt.plot(p.formation_year,p.y_growth,label='Next-year consumption growth');plt.legend();save('03_signal_target.svg','Lagged metal-price factor and demand growth','Formation year','100 × log change')
    plt.figure(figsize=(8,4));plt.plot(o.formation_year,o.actual,'k-o',label='Actual');plt.plot(o.formation_year,o.controls,'--',label='Controls');plt.plot(o.formation_year,o.full,'-.',label='Augmented');plt.legend();save('04_oos_predictions.svg','Purged expanding-window OOS forecasts','Formation year','Next-year demand growth (log-pp)')
    plt.figure(figsize=(8,4));plt.bar(s.model,s.rmse);plt.xticks(rotation=22);save('05_oos_scorecard.svg','Identical-origin forecast RMSE','Model','RMSE (log-pp)')
    plt.figure(figsize=(8,4));delta=(o.actual-o.controls)**2-(o.actual-o.full)**2;plt.bar(o.formation_year,delta);plt.axhline(0,color='k',lw=.8);save('06_paired_loss.svg','Per-origin squared-error gain: controls − full','Formation year','Squared log-pp')
    plt.figure(figsize=(8,4));plt.hist(q.rmse_gain,bins=40);plt.axvline(float(s.loc[s.model.eq('controls'),'rmse'].iloc[0]-s.loc[s.model.eq('full'),'rmse'].iloc[0]),color='red',label='Observed');plt.legend();save('07_block_shuffle.svg','1,000 exploratory block-reordered factor refits','Control − full RMSE','Draws')
    plt.figure(figsize=(8,4));plt.hist(b.rmse_gain,bins=40);plt.axvline(0,color='red');save('08_bootstrap.svg','2,000 paired circular-block bootstrap draws','Control − full RMSE','Draws')
    plt.figure(figsize=(8,4));plt.scatter(e.copper_weight,e.aluminum_weight,c=e.rmse_gain,s=7,rasterized=True);plt.colorbar(label='RMSE gain');save('09_exposure.svg','1,000 copper/aluminum weight perturbations','Copper weight','Aluminum weight')
    plt.figure(figsize=(8,4));plt.bar(g.regime,g.rmse_gain);plt.axhline(0,color='k',lw=.8);save('10_regimes.svg','Regime sensitivity (descriptive; tiny samples)','Regime','RMSE gain (log-pp)')
    return sorted(p.name for p in f.glob('*.svg'))
if __name__=='__main__':print('\n'.join(main()))
