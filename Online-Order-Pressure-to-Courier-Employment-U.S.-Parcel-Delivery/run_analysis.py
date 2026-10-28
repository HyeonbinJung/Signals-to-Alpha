from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis import prepare,walkforward,score,gain,placebo,paired_block_bootstrap,perturb,rank_ic
R=Path(__file__).resolve().parent
D=R/'data';O=R/'results';F=R/'figures'
for p in [D,O,F]:p.mkdir(exist_ok=True)
raw=pd.read_csv(D/'frozen_quarterly_courier_ecommerce_2026-10-26.csv')
d=prepare(raw);d.to_csv(D/'derived_formation_panel.csv',index=False)
o=walkforward(d);assert len(o)>45
o.to_csv(O/'oos_predictions.csv',index=False)
s=score(o);s.to_csv(O/'model_scorecard.csv',index=False)
p=placebo(d,o);p.to_csv(O/'block_permutation_1000.csv',index=False)
b=paired_block_bootstrap(o);b.to_csv(O/'block_bootstrap_2000.csv',index=False)
e=perturb(d);e.to_csv(O/'exposure_perturbation_1000.csv',index=False)
reg=[]
for name,mask in [('pre_2020',o.date<'2020-01-01'),('pandemic_2020_2021',(o.date>='2020-01-01')&(o.date<'2022-01-01')),('post_2021',o.date>='2022-01-01')]:
    z=o[mask]
    if len(z):reg.append({'period':name,'n':len(z),'gain_macro':gain(z),'gain_warehouse':gain(z,'warehouse_control')})
reg=pd.DataFrame(reg);reg.to_csv(O/'regimes.csv',index=False)
alt=[]
for h in [1,2,3,4]:
    z=walkforward(d,horizon=h)
    alt.append({'horizon_quarters':h,'n':len(z),'gain_macro':gain(z),'gain_warehouse':gain(z,'warehouse_control')})
pd.DataFrame(alt).to_csv(O/'horizon_sensitivity.csv',index=False)
abl=[]
for name in ['no_ecommerce','no_capacity']:
    z=walkforward(d,ablate=name)
    abl.append({'ablation':name,'n':len(z),'gain_macro':gain(z),'gain_warehouse':gain(z,'warehouse_control')})
pd.DataFrame(abl).to_csv(O/'ablations.csv',index=False)
loo=[]
for year in sorted(o.date.dt.year.unique()):
    z=o[o.date.dt.year!=year]
    loo.append({'excluded_year':int(year),'n':len(z),'gain_macro':gain(z),'gain_warehouse':gain(z,'warehouse_control')})
pd.DataFrame(loo).to_csv(O/'leave_one_year_out.csv',index=False)
metrics={'raw_rows':len(raw),'oos_origins':len(o),'oos_first':str(o.date.min().date()),'oos_last':str(o.date.max().date()),'gain_macro':gain(o),'gain_warehouse':gain(o,'warehouse_control'),
         'block_permutation_tail_macro':float((1+(p.gain_macro>=gain(o)).sum())/(len(p)+1)),
         'block_permutation_tail_warehouse':float((1+(p.gain_warehouse>=gain(o,'warehouse_control')).sum())/(len(p)+1)),
         'bootstrap_macro_95':list(np.quantile(b.gain_macro,[.025,.975])),
         'bootstrap_warehouse_95':list(np.quantile(b.gain_warehouse,[.025,.975])),
         'perturb_positive_share_macro':float((e.gain_macro>0).mean()),
         'perturb_positive_share_warehouse':float((e.gain_warehouse>0).mean()),
         'time_series_spearman_factor_vs_target':rank_ic(o,d.factor),
         'frozen_input_sha256':hashlib.sha256((D/'frozen_quarterly_courier_ecommerce_2026-10-26.csv').read_bytes()).hexdigest(),
         'pit_status':'NOT PIT: fixed revised snapshot with assumed one-quarter release buffer'}
(O/'summary.json').write_text(json.dumps(metrics,indent=2,default=float)+'\n')
plt.rcParams.update({'figure.figsize':(9,4),'font.size':10})
def fig(name,fn):
    plt.figure();fn();plt.tight_layout();plt.savefig(F/name,format='svg');plt.close()
fig('01_courier_warehouse_levels.svg',lambda:(plt.plot(d.date,d['CES4349200001'],label='Courier jobs'),plt.plot(d.date,d['CES4349300001'],label='Warehouse jobs'),plt.legend(),plt.title('Quarterly SA payrolls, thousands'),plt.ylabel('Thousands')))
fig('02_ecommerce_share.svg',lambda:(plt.plot(d.date,d.ECOMPCTSA),plt.title('E-commerce share of retail sales'),plt.ylabel('Percent')))
fig('03_factor_target.svg',lambda:(plt.scatter(d.factor,d.target,s=15,alpha=.6),plt.xlabel('Demand pressure factor (pp)'),plt.ylabel('Future courier YoY (log-pp)'),plt.title('Retrospective association; overlapping outcomes')))
fig('04_oos_predictions.svg',lambda:(plt.plot(o.date,o.actual,label='Actual'),plt.plot(o.date,o['macro'],label='Macro'),plt.plot(o.date,o.full,label='Factor + macro'),plt.legend(),plt.title('Purged expanding-window OOS')))
fig('05_model_scorecard.svg',lambda:(plt.bar(s.model,s.rmse),plt.xticks(rotation=30,ha='right'),plt.ylabel('RMSE (log-pp)'),plt.title('Identical OOS origins')))
fig('06_placebo.svg',lambda:(plt.hist(p.gain_macro,bins=35),plt.axvline(gain(o),color='red',ls='--'),plt.title('1000 block-aware factor-placebo gains'),plt.xlabel('Macro RMSE minus full RMSE')))
fig('07_bootstrap.svg',lambda:(plt.hist(b.gain_macro,bins=35),plt.axvline(0,color='red',ls='--'),plt.title('2000 paired 4-quarter block bootstrap gains')))
fig('08_perturbations.svg',lambda:(plt.scatter(e.warehouse_weight,e.gain_macro,s=5),plt.axhline(0,color='red',ls='--'),plt.title('1000 predeclared proxy-weight perturbations')))
fig('09_regimes.svg',lambda:(plt.bar(reg.period,reg.gain_macro),plt.xticks(rotation=25,ha='right'),plt.axhline(0,color='red'),plt.title('Regime-specific macro-relative gains')))
print(json.dumps(metrics,indent=2));print('\nSCORECARD\n',s.to_string(index=False));print('\nREGIMES\n',reg.to_string(index=False))
