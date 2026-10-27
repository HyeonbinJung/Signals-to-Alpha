"""Recompute all tables and real figures from the frozen source CSVs."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from analysis import *

ROOT=Path(__file__).resolve().parent

def main():
    for d in ('data','results','figures'): (ROOT/d).mkdir(exist_ok=True)
    raw=load_frozen(ROOT)
    panel=build_panel(raw)
    panel.to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    oos=walk_forward(panel)
    assert len(oos)>50 and oos.n_train.min()>=MIN_TRAIN
    assert all(oos.formation_date>=oos.target_date-pd.DateOffset(months=HORIZON))
    oos.to_csv(ROOT/'results/oos_predictions.csv',index=False)
    scores=scorecard(oos);scores.to_csv(ROOT/'results/scorecard.csv',index=False)
    obs=rmse_gain(oos)
    p=placebo(panel,obs);p.to_csv(ROOT/'results/block_placebo_1000.csv',index=False)
    b=circular_bootstrap(oos);b.to_csv(ROOT/'results/block_bootstrap_2000.csv',index=False)
    e=exposure_sensitivity(panel);e.to_csv(ROOT/'results/exposure_sensitivity_1000.csv',index=False)
    l=leave_year_out(oos);l.to_csv(ROOT/'results/leave_one_year_out.csv',index=False)
    r=regime_sensitivity(oos);r.to_csv(ROOT/'results/regime_sensitivity.csv',index=False)
    h=alternative_horizons(raw);h.to_csv(ROOT/'results/horizon_lag_sensitivity.csv',index=False)
    a=ablations(panel);a.to_csv(ROOT/'results/ablations.csv',index=False)
    fig,ax=plt.subplots(figsize=(9,3.4));ax.plot(raw.date,raw.AIRRPMTSID11/1e6,label='Air RPM (billion miles)');ax.set_title('Airline activity, frozen revised snapshot');ax.set_ylabel('Billion passenger miles');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/01_airline_activity.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,3.4));ax.plot(panel.date,panel.oil_relief,label='Oil-cost relief score');ax.plot(panel.date,panel.target_air_yoy,label='Future airline RPM YoY',alpha=.7);ax.set_title('Signal and outcome: not a PIT chart');ax.set_ylabel('Log percentage points');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/02_signal_target.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,3.4));ax.plot(oos.target_date,oos.actual,label='Observed');ax.plot(oos.target_date,oos.macro_control,label='Control',alpha=.75);ax.plot(oos.target_date,oos.oil_augmented,label='Oil augmented',alpha=.75);ax.set_title('Purged expanding-window OOS forecasts');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/03_oos_predictions.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.4));ax.bar(scores.model,scores.rmse);ax.set_ylabel('RMSE (log-pp)');ax.tick_params(axis='x',labelrotation=20);ax.set_title('Forecast baselines vs challenger');fig.tight_layout();fig.savefig(ROOT/'figures/04_scorecard.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4));ax.hist(p.gain_rmse,bins=35,alpha=.8);ax.axvline(obs,linestyle='--',label='Observed gain');ax.set_title('1,000 exploratory year-block shuffle refits');ax.set_xlabel('Control minus augmented RMSE');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/05_placebo.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4));ax.hist(b.gain_rmse,bins=40,alpha=.8);ax.axvline(0,linestyle='--');ax.set_title('2,000 paired 12-month circular-block bootstrap draws');ax.set_xlabel('Control minus augmented RMSE');fig.tight_layout();fig.savefig(ROOT/'figures/06_bootstrap.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4));ax.scatter(e.w_yoy,e.gain_rmse,s=5,alpha=.25);ax.axhline(0,linestyle='--');ax.set_title('Oil-horizon blend perturbations (1,000 refits)');ax.set_xlabel('Annual oil-change weight');ax.set_ylabel('RMSE improvement');fig.tight_layout();fig.savefig(ROOT/'figures/07_exposure.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4));ax.plot(l.excluded_formation_year,l.gain_rmse,marker='o');ax.axhline(0,linestyle='--');ax.set_title('Leave-one-formation-year-out sensitivity');ax.set_ylabel('RMSE improvement');fig.tight_layout();fig.savefig(ROOT/'figures/08_leave_year.svg');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,3.4));ax.barh(r.regime,r.gain_rmse);ax.axvline(0,linestyle='--');ax.set_title('Regime sensitivity, same OOS forecasts');ax.set_xlabel('RMSE improvement');fig.tight_layout();fig.savefig(ROOT/'figures/09_regimes.svg');plt.close(fig)
    print('OOS',len(oos),'train min',oos.n_train.min(),'last formation',oos.formation_date.iloc[-1])
    print(scores.to_string(index=False));print('RMSE gain',obs)
    print('block placebo exploratory tail fraction',float(np.mean(p.gain_rmse>=obs)))
    print('paired block bootstrap CI',np.quantile(b.gain_rmse,[.025,.975]).tolist())
    print('exposure improvement fraction',float(np.mean(e.gain_rmse>0)))
    print('regimes\n',r.to_string(index=False))
    print('horizons\n',h.to_string(index=False))
    print('ablations\n',a.to_string(index=False))

if __name__=='__main__':main()
