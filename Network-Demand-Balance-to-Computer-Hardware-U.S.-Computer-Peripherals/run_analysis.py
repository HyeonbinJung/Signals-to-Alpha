"""Deterministic, no-network research reproduction; see README for scope."""
from __future__ import annotations
import hashlib, json, os, sys, time, subprocess
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from computer_factor import (load_and_qa,make_panel,oos,rmse,mae,scorecard,subset_gain,
                             block_placebo,bootstrap_paired,exposure_perturbation,FEATURES)

ROOT=Path(__file__).resolve().parent
RAW=ROOT/'data/frozen_g17_electronics_2026-10-19.csv'
RES=ROOT/'results';FIG=ROOT/'figures'
RES.mkdir(exist_ok=True);FIG.mkdir(exist_ok=True)


def saveplot(name, fn):
    fig,ax=plt.subplots(figsize=(10.2,5.0),layout='constrained')
    fn(ax)
    ax.grid(alpha=.2)
    fig.savefig(FIG/name,dpi=130)
    plt.close(fig)


def run():
    t0=time.time(); raw=load_and_qa(RAW)
    panel=make_panel(raw)
    panel.to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    o=oos(panel); assert len(o)>=80
    assert (o['target_month']>o['date']).all()
    assert (o['latest_input_month']<o['date']).all()
    assert (o['n_train']>=48).all()
    sc=scorecard(o); gain=subset_gain(o)
    o.to_csv(RES/'walk_forward_oos.csv',index=False)
    sc.to_csv(RES/'scorecard.csv',index=False)
    # Each Monte Carlo batch runs in a separate fresh Python process.
    reuse_draws='--reuse-draws' in sys.argv
    for mode,filename in [('exposure','exposure_perturbation_1000.csv'),('placebo','block_placebo_1000.csv'),('bootstrap','paired_block_bootstrap_2000.csv')]:
        print('START '+mode,flush=True)
        if not reuse_draws or not (RES/filename).exists():
            subprocess.run([sys.executable,str(ROOT/'compute_draws.py'),mode],cwd=ROOT,check=True,
                           env={**os.environ,'OPENBLAS_NUM_THREADS':'1'})
    null=pd.read_csv(RES/'block_placebo_1000.csv')
    p_tail=float((1+(null.null_delta_rmse_log_pp>=gain).sum())/(len(null)+1))
    boot=pd.read_csv(RES/'paired_block_bootstrap_2000.csv')
    exposure=pd.read_csv(RES/'exposure_perturbation_1000.csv')
    # Alternative horizon and publication buffer: not apples-to-apples sample sizes.
    print('START horizon',flush=True);horizon=[]
    for h in [1,3,6,12]:
        for buffer in [1,2,3,4]:
            pp=make_panel(raw,h=h,buffer=buffer)
            oo=oos(pp,h=h,buffer=buffer)
            if len(oo)<40: continue
            horizon.append({'horizon_months':h,'release_buffer_months':buffer,'n':len(oo),
                            'mean_rmse':rmse(oo.y,oo.historical_mean),
                            'control_rmse':rmse(oo.y,oo.macro_control),
                            'full_rmse':rmse(oo.y,oo.full_network_balance),
                            'delta_rmse':subset_gain(oo)})
    pd.DataFrame(horizon).to_csv(RES/'horizon_lag_robustness.csv',index=False)
    print('START regimes',flush=True);regimes=[]
    for name,mask in [('pre_2020',o.date<'2020-01-01'),('pandemic_2020_2021',(o.date>='2020-01-01')&(o.date<'2022-01-01')),
                      ('post_2021',o.date>='2022-01-01')]:
        x=o.loc[mask]
        regimes.append({'regime':name,'n':len(x),'control_rmse':rmse(x.y,x.macro_control),
                        'full_rmse':rmse(x.y,x.full_network_balance),'delta_rmse':subset_gain(x)})
    pd.DataFrame(regimes).to_csv(RES/'regime_sensitivity.csv',index=False)
    loo=[]
    for year in sorted(o.date.dt.year.unique()):
        x=o.loc[o.date.dt.year!=year]
        loo.append({'excluded_year':int(year),'n':len(x),'delta_rmse':subset_gain(x)})
    pd.DataFrame(loo).to_csv(RES/'leave_one_year_out.csv',index=False)
    ablation=[]
    abls={
        'no_chip_control':['computer_stale','computer_momentum','manufacturing_stale','factor'],
        'no_manufacturing_control':['computer_stale','computer_momentum','chip_stale','factor'],
        'network_level_only':['computer_stale','computer_momentum','manufacturing_stale','chip_stale','network_stale'],
        'base_full':FEATURES['full_network_balance'],
    }
    for name,cols in abls.items():
        oo=oos(panel,feature_sets={'ablation':cols})
        ablation.append({'model':name,'n':len(oo),'rmse':rmse(oo.y,oo.ablation)})
    pd.DataFrame(ablation).to_csv(RES/'ablations.csv',index=False)
    p_valid=panel.dropna(subset=['factor','target'])
    corr=float(p_valid['factor'].corr(p_valid['target']))
    rho=float(spearmanr(p_valid['factor'],p_valid['target']).statistic)
    boot_ci=np.quantile(boot.delta_rmse_log_pp,[.025,.975])
    metric={
        'status':'REPRODUCED RETROSPECTIVE MACRO FALSIFICATION — NOT PIT, NOT EQUITY ALPHA',
        'research_date':'2026-10-28','industry':'US computer and peripheral equipment manufacturing NAICS 3341',
        'data_n':len(raw),'raw_start':str(raw.date.min().date()),'raw_end':str(raw.date.max().date()),
        'oos_n':len(o),'oos_start':str(o.date.min().date()),'oos_end':str(o.date.max().date()),
        'target_horizon_months':3,'publication_buffer_months':2,'training_min':48,
        'target_units':'100 x log(IPG3341S[t+3] / IPG3341S[t-9]) (log percentage points)',
        'factor_formula':'g_IPG3342S[t-2] - g_IPG3344S[t-2], g_s=100log(IP_s/IP_s[-12])',
        'mean_rmse':rmse(o.y,o.historical_mean),'persistence_rmse':rmse(o.y,o.persistence),
        'momentum_rmse':rmse(o.y,o.momentum),'ar_rmse':rmse(o.y,o.ar_ridge),
        'macro_rmse':rmse(o.y,o.macro_control),'full_rmse':rmse(o.y,o.full_network_balance),
        'delta_rmse':gain,'factor_only_rmse':rmse(o.y,o.network_factor_only),
        'macro_mae':mae(o.y,o.macro_control),'full_mae':mae(o.y,o.full_network_balance),
        'association_pearson':corr,'association_spearman':rho,'association_n':len(p_valid),
        'block_placebo_draws':len(null),'block_placebo_tail_fraction_exploratory':p_tail,
        'block_bootstrap_draws':len(boot),'bootstrap_ci_95_delta_rmse':boot_ci.tolist(),
        'exposure_draws':len(exposure),'exposure_fraction_positive':float((exposure.delta_rmse_log_pp>0).mean()),
        'exposure_ci_95':np.quantile(exposure.delta_rmse_log_pp,[.025,.975]).tolist(),
        'source_vintage_pit_verified':False,'company_fundamentals_tested':False,
        'equity_total_returns_tested':False,'source_inherited_from':'Semiconductor-Device-Gap-to-Alpha-U.S.-Chip-Manufacturing',
        'raw_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),
        'limitations':['No original release-vintage panel','Overlapping YoY labels; paired block bootstrap only exploratory',
                       'Only 2011-2026 fixed revised monthly sample','No corporate fundamentals or securities returns',
                       'Source inherited from previous repository research, not independently recollected'],
    }
    (RES/'metrics.json').write_text(json.dumps(metric,indent=2,ensure_ascii=False)+'\n')
    # 10 nonredundant computed diagnostic charts.
    print('START figures',flush=True);saveplot('01_computer_network_chip_indices.png',lambda ax:(raw.set_index('date')[['IPG3341S','IPG3342S','IPG3344S']].plot(ax=ax),ax.set_title('Industrial production indices: computer / network / electronic components'),ax.set_ylabel('2017=100')))
    saveplot('02_yoy_sector_growth.png',lambda ax:(panel.set_index('date')[['computer_yoy','network_yoy','chip_yoy']].plot(ax=ax),ax.set_title('12-month log growth: three electronics industries'),ax.set_ylabel('log-pp')))
    saveplot('03_factor_vs_future_growth.png',lambda ax:(ax.plot(p_valid.date,p_valid.factor,label='network minus chip signal'),ax.plot(p_valid.date,p_valid.target,label='computer growth t+3',alpha=.65),ax.legend(),ax.set_title('Retrospective factor and 3m-ahead computer production YoY')))
    saveplot('04_signal_scatter.png',lambda ax:(ax.scatter(p_valid.factor,p_valid.target,alpha=.35,s=15),ax.set_xlabel('network-chip growth gap (log-pp)'),ax.set_ylabel('computer YoY at t+3 (log-pp)'),ax.set_title(f'Unconditional association, Pearson r={corr:.3f} (not OOS)')))
    saveplot('05_oos_forecast_paths.png',lambda ax:(ax.plot(o.date,o.y,label='realized'),ax.plot(o.date,o.macro_control,label='macro control'),ax.plot(o.date,o.full_network_balance,label='augmented',alpha=.8),ax.legend(),ax.set_title('Purged expanding-window OOS forecasts')))
    saveplot('06_baseline_scorecard.png',lambda ax:(ax.barh(sc.model,sc.rmse_log_pp),ax.set_xlabel('RMSE (log-pp; lower better)'),ax.set_title('Same-origin OOS baseline comparison')))
    loss=(o.y-o.macro_control)**2-(o.y-o.full_network_balance)**2
    saveplot('07_cumulative_loss_differential.png',lambda ax:(ax.plot(o.date,np.cumsum(loss)),ax.axhline(0,color='gray',ls='--'),ax.set_title('Cumulative paired squared-error advantage of factor'),ax.set_ylabel('control squared error - augmented squared error')))
    saveplot('08_block_placebo.png',lambda ax:(ax.hist(null.null_delta_rmse_log_pp,bins=35,alpha=.8),ax.axvline(gain,color='red',label='observed'),ax.legend(),ax.set_title('1,000 12-month block-reordered factor refits (exploratory)')))
    saveplot('09_bootstrap_uncertainty.png',lambda ax:(ax.hist(boot.delta_rmse_log_pp,bins=40,alpha=.8),ax.axvline(0,color='black',ls='--'),ax.axvline(gain,color='red'),ax.set_title('2,000 moving-block paired OOS RMSE differences')))
    saveplot('10_exposure_sensitivity.png',lambda ax:(ax.scatter(exposure.chip_subtraction_weight,exposure.delta_rmse_log_pp,alpha=.35,s=12),ax.axhline(0,color='black',ls='--'),ax.set_xlabel('chip subtraction weight'),ax.set_ylabel('control - full RMSE (log-pp)'),ax.set_title('1,000 refitted factor-weight perturbations')))
    saveplot('11_regime_sensitivity.png',lambda ax:(ax.bar([r['regime'] for r in regimes],[r['delta_rmse'] for r in regimes]),ax.axhline(0,color='black',ls='--'),ax.set_title('Out-of-sample regime dependence'),ax.set_ylabel('RMSE improvement (log-pp)')))
    # Clean logs are created only after successful completion.
    (RES/'analysis_execution.log').write_text(f'PASS run_analysis.py; reuse_draws={reuse_draws}; raw_n={len(raw)}; oos_n={len(o)}; placebo=1000; bootstrap=2000; perturbations=1000; elapsed_seconds={time.time()-t0:.2f}\n')
    print(json.dumps({'oos_n':len(o),'delta_rmse':gain,'mean':metric['mean_rmse'],
                      'control':metric['macro_rmse'],'full':metric['full_rmse'],
                      'placebo_tail':p_tail,'bootstrap_ci':boot_ci.tolist(),
                      'exposure_fraction_positive':metric['exposure_fraction_positive']},indent=2))
    return metric

if __name__=='__main__':run()
