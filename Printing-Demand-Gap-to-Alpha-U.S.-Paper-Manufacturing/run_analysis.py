"""Run the paper-industry macro falsification and persist all computed artifacts."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from analysis import *


def main():
    (ROOT/'results').mkdir(exist_ok=True);(ROOT/'figures').mkdir(exist_ok=True)
    raw=load_data();panel=build_panel(raw);pred=walk_forward(panel)
    assert len(pred)>=60
    panel.to_csv(ROOT/'data/derived_formation_panel.csv',index=False)
    pred.to_csv(ROOT/'results/oos_predictions.csv',index=False)
    metrics=score(pred);metrics.to_csv(ROOT/'results/scorecard.csv',index=False)
    gain=rmse_improvement(pred)
    bs=block_bootstrap(pred);pd.DataFrame({'improvement_log_pp':bs}).to_csv(ROOT/'results/block_bootstrap_2000.csv',index=False)
    perm,tail=placebo(panel,gain);pd.DataFrame({'placebo_improvement_log_pp':perm}).to_csv(ROOT/'results/block_permutation_1000.csv',index=False)
    exp=exposure_perturbations(raw);exp.to_csv(ROOT/'results/exposure_perturbation_1000.csv',index=False)
    reg=regime_scores(pred);reg.to_csv(ROOT/'results/regimes.csv',index=False)
    loo=leave_one_year_out(pred);loo.to_csv(ROOT/'results/leave_one_year_out.csv',index=False)
    ranks,spread=rank_spread(pred);ranks.to_csv(ROOT/'results/factor_quintile_outcomes.csv')
    robustness=[]
    for h in [1,3,6,12]:
        for lag in [1,2,3]:
            pp=build_panel(raw,horizon=h,lag=lag);p=walk_forward(pp,horizon=h,lag=lag)
            robustness.append({'horizon':h,'lag':lag,'n':len(p),'control_minus_augmented_rmse':rmse_improvement(p),
                               'mean_rmse':score(p).set_index('model').loc['mean','rmse_log_pp']})
    pd.DataFrame(robustness).to_csv(ROOT/'results/horizon_lag_sensitivity.csv',index=False)
    summary={'n_raw':len(raw),'n_panel':len(panel),'n_oos':len(pred),'first_origin':str(pred.origin.min().date()),
             'last_origin':str(pred.origin.max().date()),'improvement_log_pp':gain,
             'block_bootstrap_ci_95':list(map(float,np.quantile(bs,[.025,.975]))),
             'block_permutation_exploratory_tail':tail,'perturbation_positive_share':float((exp.control_minus_augmented_rmse>0).mean()),
             'quintile_macro_growth_spread_log_pp':spread,
             'historical_vintages_verified':False,'equity_alpha_established':False}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    # Actual figures are computed from data; SVG chosen to keep GitHub transfer auditable and text-based.
    plt.rcParams.update({'figure.figsize':(8,4.2),'font.size':10})
    def save(name):
        plt.tight_layout();plt.savefig(ROOT/'figures'/name,format='svg');plt.close()
    raw.assign(paper_yoy=100*np.log(raw.paper_ip/raw.paper_ip.shift(12)),printing_yoy=100*np.log(raw.printing_ip/raw.printing_ip.shift(12))).set_index('date')[['paper_yoy','printing_yoy']].plot(title='Paper and printing industrial output YoY (revised snapshot)');plt.axhline(0,color='gray',lw=.7);save('01_industry_growth.svg')
    panel.plot(x='date',y=['factor','target'],title='Stale printing-demand gap vs future paper output');plt.axhline(0,color='gray',lw=.7);save('02_signal_target.svg')
    metrics.set_index('model').rmse_log_pp.plot(kind='bar',title='Purged expanding-window OOS RMSE');plt.ylabel('log percentage points');save('03_oos_scorecard.svg')
    pred.plot(x='origin',y=['actual','mean','macro_controls','augmented'],title='Realized vs OOS predictions');save('04_oos_predictions.svg')
    pred.assign(loss_diff=(pred.actual-pred.macro_controls)**2-(pred.actual-pred.augmented)**2).plot(x='origin',y='loss_diff',title='Paired squared-loss differential (positive favors factor)');plt.axhline(0,color='gray',lw=.7);save('05_loss_differences.svg')
    plt.hist(bs,bins=45);plt.axvline(0,color='black',ls='--');plt.title('2000 circular 12-month block-bootstrap RMSE gains');save('06_bootstrap.svg')
    plt.hist(perm,bins=45);plt.axvline(gain,color='black',ls='--',label='observed');plt.legend();plt.title('1000 block-shuffle placebo RMSE gains');save('07_block_placebo.svg')
    reg.plot(x='regime',y='gain_log_pp',kind='bar',legend=False,title='Control minus augmented RMSE by regime');plt.axhline(0,color='black');save('08_regimes.svg')
    loo.plot(x='excluded_year',y='gain_log_pp',kind='bar',legend=False,title='Leave-one-calendar-year-out gain');plt.axhline(0,color='black');save('09_leave_one_year.svg')
    ranks['mean'].plot(kind='bar',title='Future paper output growth by signal quintile (not returns)');plt.ylabel('log percentage points');save('10_factor_quintiles.svg')
    print(json.dumps(summary,indent=2));print(metrics.to_string(index=False))

if __name__=='__main__':main()
