"""Generate the 15-section, independently readable research notebook; execute separately."""
from pathlib import Path
import nbformat as nbf
ROOT=Path(__file__).resolve().parent
nb=nbf.v4.new_notebook()
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}}
c=[]
def md(x):c.append(nbf.v4.new_markdown_cell(x))
def code(x):c.append(nbf.v4.new_code_cell(x))
md('''# Air-Traffic Demand Gap → U.S. Aerospace Manufacturing

**Independent research notebook | 2026-10-26 fixed snapshot | REPRODUCED MACRO PILOT / NOT PIT / NOT EQUITY ALPHA**

This study tests whether U.S. airline passenger-mile growth anticipates aerospace manufacturing output. It follows the 15-section canonical research structure and the K-Food v3 logic: falsifiable hypotheses, dated source register, fixed factor, purged expanding-window OOS, block-aware falsification, limitations and verdict. **All quantitative claims below come from code outputs; this is not a securities trading backtest.**''')
md('''## 01. Abstract

**Question:** Does lagged air revenue passenger-mile growth, relative to manufacturing momentum, improve six-month-ahead U.S. aerospace production forecasts beyond persistence and macro baselines? The primary target is the G.17 NAICS 3364 industrial-production YoY log change at t+6. The study uses 201 aerospace/manufacturing monthly observations and 150 airline observations; no individual firm returns are included.''')
code('''from pathlib import Path
import sys, json, hashlib, numpy as np, pandas as pd, matplotlib.pyplot as plt
from IPython.display import display, Markdown, Image
import io
def showfig():
    buf=io.BytesIO()
    plt.gcf().savefig(buf,format='png',dpi=110,bbox_inches='tight')
    display(Image(data=buf.getvalue()))
    plt.close()
ROOT=Path.cwd()
assert (ROOT/'run_analysis.py').exists(), 'Run notebook from the study directory'
sys.path.insert(0,str(ROOT))
import run_analysis as ra
pd.set_option('display.max_columns',30)
print('Study root:',ROOT)
print('Predeclared six-month horizon:',ra.HORIZON,'| airline delay:',ra.AIR_LAG,'| G.17 delay:',ra.IP_LAG)''')
code('''raw=ra.load_data()
print('Raw rows:',len(raw),'| airline non-null:',raw.AIRRPMTSID11.notna().sum())
display(raw.head(3),raw.tail(3))''')
md('''The principal failure standard is **not** whether an in-sample coefficient is positive: the air-gap challenger must improve the macro baseline and historical mean on the same purged OOS origins.''')
md('''## 02. Research Design & Hypotheses

**H1:** airline gap improves macro-control RMSE. **H2:** the gain survives exclusion of 2020–21 and alternative horizons. **H3:** the gain survives 1,000 block-shuffle placebos and ±20% formula perturbations. The counterthesis is that flight utilization drives engine aftermarket while aircraft production depends on multi-year order books, defense procurement and supply-chain bottlenecks.''')
code('''design=pd.DataFrame({'test':['H1: incremental OOS','H2: regimes/horizons','H3: block placebo / weights'], 'success_rule':['macro RMSE − full RMSE > 0 and full < historical mean','positive in 2020–21 exclusion and 3m/12m horizons','not explained by block shuffle and robust weight signs']})
display(design)''')
md('''## 03. Industry Context

The [Aerospace Industries Association 2026 Facts & Figures](https://www.aia-aerospace.org/news/2026-aia-facts-figures-u-s-aerospace-defense-industry-leads-the-world-with-1-trillion-in-sale/) reports **$988.6B** of 2025 U.S. aerospace-and-defense sales and **$506B** of direct output. These are broad A&D totals, **not** the NAICS 3364 index level. Commercial aviation and defense procurement have different demand cycles, while a 2017=100 industrial production index is not a revenue series.''')
code('''context=pd.DataFrame({'mechanism':['airline traffic → fleet replacement','flight utilization → maintenance','defense procurement → factory output','OEM capacity/supply-chain → factory output'], 'predicted_relation':['potentially positive but slow','positive aftermarket, weaker G.17 link','can overwhelm civilian signal','can sever demand-output link'], 'measured_here':['air passenger miles only','not directly','not directly','not directly']})
display(context)''')
md('''## 04. Data & Source Integrity

**Source grades:** A = original federal FRED table directly inspected; B = official federal series reused from previously frozen and manually transcribed repository studies; C = industry association context. `data/source_register.csv` records exact URLs, publisher, release date, coverage, units and revisions. All 201 aerospace monthly observations were parsed from the FRED table; independent checks of 2010-01, 2020-04 and 2026-09 are included. Historical row-by-row comparison of reused inputs remains pending.''')
code('''sources=pd.read_csv(ROOT/'data/source_register.csv')
display(sources[['source_id','grade','series_or_document','release_or_publication_date','observation_period','revision_vintage']])''')
code('''print('Raw SHA-256:',hashlib.sha256((ROOT/'data/frozen_observations_2026-10-26.csv').read_bytes()).hexdigest())
assert len(raw)==201 and raw.date.is_unique
assert np.isclose(raw.loc[raw.date.eq('2010-01-01'),'aerospace_ip'].iloc[0],84.8531)
assert np.isclose(raw.loc[raw.date.eq('2020-04-01'),'aerospace_ip'].iloc[0],54.3996)
assert np.isclose(raw.loc[raw.date.eq('2026-09-01'),'aerospace_ip'].iloc[0],99.2876)
print('Three independently viewed FRED aerospace spot checks: PASS')''')
code('''print('Missing by column:')
display(raw.isna().sum().to_frame('missing_rows'))
print('Airline observed window:',raw.loc[raw.AIRRPMTSID11.notna(),'date'].min().date(),raw.loc[raw.AIRRPMTSID11.notna(),'date'].max().date())''')
md('''## 05. Point-in-Time Availability

At formation t, airline signal ends at **t−4 months**, G.17 controls at **t−2 months**; a training label from formation s is allowed only if **s+6+1≤t**. These are modeling buffers, **not** historical release-vintage verification. Latest-revised G.17 and BTS values may differ from original releases; exact historical timestamps and revisions are UNKNOWN.''')
code('''d=ra.panel()
display(d[['date','origin_month','aero_mom','mfg_mom','air_mom','air_gap','target']].head(5))
print('Complete formation rows:',len(d),'| first/last:',d.date.min().date(),d.date.max().date())''')
code('''o=ra.forecast(d)
first=o.iloc[0]; train=d[d.origin_month+ra.HORIZON+ra.TARGET_RELEASE_BUFFER<=first.origin_month]
print('First OOS formation:',first.date,'| training labels available:',len(train),'| last admitted training origin:',train.date.max().date())
assert len(train)==first.n_train
assert (train.origin_month+7<=first.origin_month).all()
print('Target-release purge: PASS')''')
md('''## 06. Factor Construction

For series X define `g^X_t=100·ln(X_t/X_(t−12))`. Use `a_t=g^AIR_(t−4)`, `m_t=g^MFG_(t−2)`, `p_t=g^AERO_(t−2)` and fixed `F_t=30·tanh((a_t−m_t)/30)`. Target `y_t=g^AERO_(t+6)`. The scale 30 and Ridge penalty α=10 are fixed; only training-window feature means and standard deviations are fitted.''')
code('''sample=d.iloc[10]
recomputed=30*np.tanh((sample.air_mom-sample.mfg_mom)/30)
print('Sample origin:',sample.date.date(),'| factor saved:',round(sample.air_gap,6),'| independently recomputed:',round(recomputed,6))
assert np.isclose(sample.air_gap,recomputed)''')
code('''fig,ax=plt.subplots(figsize=(9,3.1));ax.plot(d.date,d.air_mom,label='Air YoY at t−4');ax.plot(d.date,d.mfg_mom,label='Mfg YoY at t−2');ax.axhline(0,color='gray',lw=.6);ax.set_ylabel('YoY log growth, pp');ax.set_title('Observed formation-date inputs');ax.legend();showfig()''')
code('''fig,ax=plt.subplots(figsize=(9,3));ax.plot(d.date,d.air_gap,label='Fixed tanh gap');ax.axhline(0,color='gray',lw=.6);ax.set_ylabel('Bounded factor, pp');ax.set_title('Candidate factor (no full-sample standardization)');ax.legend();showfig()''')
md('''## 07. Exposure & Transmission

Dated company exposure is **qualitative**. Boeing commercial aircraft, GE Aerospace propulsion/aftermarket, and RTX Collins/Pratt & Whitney/defense have distinct revenue channels. There is no justified monthly company exposure matrix or historical constituent universe. **Leave-one-company-out is inapplicable**; it is not replaced with fabricated firm data.''')
code('''exposure=pd.read_csv(ROOT/'data/company_exposure_map.csv')
display(exposure[['company','exposure_type','qualitative_direction','as_of','weight']])''')
md('''Aerospace output is a U.S. industry aggregate, not a value-weighted portfolio of those three companies. The ±20% robustness test changes the *economic formula weights*, not security holdings.''')
md('''## 08. Outcomes & Baselines

**Common origins:** historical target mean; direct lagged aerospace YoY persistence; two-control Ridge (`p_t,m_t`); full Ridge (`p_t,m_t,F_t`); air-only; no-manufacturing ablation. Each model uses the same target, purge and origins. Corporate fundamentals and total-return/benchmark-adjusted equity returns are **NOT TESTED**; return IC/spread is **N/A**, not zero.''')
code('''print('OOS observations:',len(o),'| date range:',o.date.min(),o.date.max(),'| training sample range:',o.n_train.min(),o.n_train.max())
display(o.head(3),o.tail(3))''')
code('''sc=ra.scorecard(o)
display(sc.round(3))
assert (sc.n==len(o)).all()''')
code('''fig,ax=plt.subplots(figsize=(9,3.5));ax.plot(o.date,o.actual,label='Actual');ax.plot(o.date,o.macro,label='Macro control');ax.plot(o.date,o.full,label='With air gap');ax.legend();ax.set_title('Purged expanding-window OOS predictions');ax.set_ylabel('Six-month-ahead aerospace YoY, pp');plt.xticks(rotation=30);showfig()''')
md('''## 09. Empirical Findings

The predeclared improvement is `RMSE(macro) − RMSE(full)`. **Positive is improvement, negative is deterioration.** Pearson forecast/outcome correlation is secondary and cannot substitute for calibrated prediction loss.''')
code('''delta=ra.rmse(o.actual,o.macro)-ra.rmse(o.actual,o.full)
print(f'Macro-minus-full RMSE: {delta:.3f} pp; mean-minus-full: {ra.rmse(o.actual,o["mean"])-ra.rmse(o.actual,o.full):.3f} pp')
print('Hypothesis H1 supported?',delta>0 and ra.rmse(o.actual,o.full)<ra.rmse(o.actual,o['mean']))''')
code('''fig,ax=plt.subplots(figsize=(8,3));ax.bar(sc.model,sc.rmse_pp);ax.set_ylabel('RMSE, pp');ax.set_title('Historical mean vs persistence vs multivariate models');plt.xticks(rotation=20);showfig()''')
code('''loss=(o.actual-o.macro)**2-(o.actual-o.full)**2
fig,ax=plt.subplots(figsize=(9,3));ax.plot(o.date,loss.cumsum());ax.axhline(0,color='black',lw=.8);ax.set_ylabel('Cumulative macro loss − full loss');ax.set_title('Paired squared-loss differential');plt.xticks(rotation=30);showfig()''')
md('''The factor can correlate with the direction of production changes while still **increasing squared forecast error** during regime changes. The scorecard and cumulative-loss plot, rather than a selected positive coefficient, determine the verdict.''')
md('''## 10. Robustness & Placebos

Block shuffling preserves within-12-month order while reassigning the factor's annual blocks; each of **1,000** draws refits the expanding-window model. This is a **heuristic placebo**, not an exact p-value because temporal regimes and overlapping targets violate exchangeability. Paired circular-block bootstrap (**2,000** draws) quantifies forecast-loss sensitivity. Economic formula weights vary independently ±20% in **1,000** refits.''')
code('''# Full 1,000/2,000/1,000 draw analyses are generated by run_analysis.py before publication.
# This notebook verifies saved draw counts and independently recomputes all OOS forecasts.
metrics=json.loads((ROOT/'results/metrics.json').read_text())
assert metrics['n_oos']==len(o)
assert metrics['block_placebo_draws']==1000 and metrics['bootstrap_draws']==2000 and metrics['exposure_draws']==1000
saved=pd.read_csv(ROOT/'results/walk_forward_oos.csv')
assert np.allclose(saved[['macro','full']],o[['macro','full']])
print('Saved heavy falsifications + independent OOS reproduction: PASS')''')
code('''p=pd.read_csv(ROOT/'results/block_placebo_1000.csv')
print('Exploratory shuffled-tail fraction:',round((p.delta_rmse_pp>=delta).mean(),3))
fig,ax=plt.subplots(figsize=(8,3));ax.hist(p.delta_rmse_pp,bins=35);ax.axvline(delta,color='black',lw=2,label='Observed');ax.set_xlabel('Macro − full RMSE, pp');ax.legend();ax.set_title('12-month block-order shuffle, 1,000 refits');showfig()''')
code('''b=pd.read_csv(ROOT/'results/bootstrap_2000.csv');ci=np.quantile(b.delta_macro_full,[.025,.975])
print('Bootstrap 95% interval:',ci.round(3),'| 2,000 paired circular 12-month blocks')
fig,ax=plt.subplots(figsize=(8,3));ax.hist(b.delta_macro_full,bins=40);ax.axvline(0,color='black');ax.set_title('Bootstrap paired RMSE improvement');showfig()''')
code('''pert=pd.read_csv(ROOT/'results/exposure_1000.csv')
print('Fraction of perturbations with positive gain:',round((pert.delta_macro_full>0).mean(),3))
fig,ax=plt.subplots(figsize=(8,3));ax.scatter(pert.w_air,pert.delta_macro_full,s=7,alpha=.4);ax.axhline(0,color='black');ax.set_xlabel('Air coefficient');ax.set_ylabel('Macro − full RMSE, pp');ax.set_title('1,000 economic-exposure perturbations');showfig()''')
code('''print('Ablation scorecard:')
display(sc[sc.model.isin(['macro','full','air_only','no_mfg'])].round(3))''')
md('''## 11. Regime Sensitivity

Change forecast horizon to 3 or 12 months, airline delay to 6 months, or G.17 delay to 3 months. Separately **score** the unchanged OOS predictions excluding 2020–21, rather than retraining a post-hoc model. A pre-2020 slice with only two origins is too small for inference.''')
code('''rob=pd.read_csv(ROOT/'results/robustness.csv')
display(rob.round(3))''')
code('''fig,ax=plt.subplots(figsize=(9,4));ax.barh(rob.test,rob.macro_minus_full_rmse_pp);ax.axvline(0,color='black',lw=.8);ax.set_title('Horizon, delay and regime sensitivity');ax.set_xlabel('Macro − full RMSE, pp');showfig()''')
code('''loo=pd.read_csv(ROOT/'results/leave_one_year_out.csv')
display(loo.round(3))
print('Leave-one-year-out gain positive in',int((loo.delta_macro_full>0).sum()),'of',len(loo),'exclusions')''')
md('''## 12. Bias Audit & Verdict

**PIT:** all three series are revised snapshots; initial release vintages UNKNOWN. **Selection:** this industry was chosen after several negative industry pilots, so across-study multiple testing is material. **Regime:** 2020 and post-pandemic production constraints are not stable. **Survivorship:** national index composition/revisions, not a historical company universe. **Causality:** no aircraft order backlog, exports, defense controls or fleet data. **Costs:** no stock returns, transactions, capacity or slippage; no trading claim. **Verdict: NEGATIVE REPRODUCED MACRO PILOT; NOT PIT; NOT EQUITY ALPHA.**''')
code('''verdict={'H1_incremental_rmse_positive':bool(delta>0),'H2_exclude_pandemic_positive':bool(rob.loc[rob.test.eq('exclude-2020-2021'),'macro_minus_full_rmse_pp'].iloc[0]>0),'H3_exposure_majority_positive':bool((pert.delta_macro_full>0).mean()>.5),'historical_PIT_verified':False,'equity_alpha_established':False}
display(pd.DataFrame([verdict]).T.rename(columns={0:'result'}))''')
md('''## 13. Reproduction

From a clean checkout install `requirements.txt`, run `python run_analysis.py`, then `python -m pytest tests -q`, and execute this notebook with nbconvert/nbclient. All plots and tables above are computed from the frozen input, and results have fixed seeds. Root `scripts/validate_studies.py` is a **structural** gate, not proof of real-time vintage validity.''')
code('''import subprocess
p_test=subprocess.run([sys.executable,'-m','pytest','tests','-q'],cwd=ROOT,capture_output=True,text=True)
print(p_test.stdout)
assert p_test.returncode==0,p_test.stderr''')
code('''print('Published results:')
for name in ['metrics.json','scorecard.csv','walk_forward_oos.csv','block_placebo_1000.csv','bootstrap_2000.csv','exposure_1000.csv','robustness.csv']:
 pth=ROOT/'results'/name
 print(name,pth.stat().st_size,'bytes')
assert len(list((ROOT/'figures').glob('*.png')))>=3''')
md('''## 14. Next-Stage Protocol

Acquire actual ALFRED G.17 historical vintages and BTS initial-release files; re-audit all 201 aerospace and reused manufacturing/air rows; timestamp each observation as available. Add FAA deliveries, order backlogs, defense contracts and supply-chain lead times. Only then construct historical firm-segment revenue exposure panels, independent earnings outcomes, dividend-adjusted total returns, transaction costs and an untouched holdout.''')
code('''next_steps=pd.DataFrame({'priority':[1,2,3,4],'data':['G.17/BTS first-release vintages','FAA orders, fleet and deliveries','Dated BA/GE/RTX segment fundamentals','Adjusted returns + benchmark + costs'],'current_status':['UNKNOWN','NOT COLLECTED','NOT COLLECTED','NOT COLLECTED']})
display(next_steps)''')
md('''## 15. Sources & Artifacts

Primary source: [Federal Reserve aerospace G.17](https://fred.stlouisfed.org/data/IPG3364S) (updated 2026-10-16). Controls: [G.17 manufacturing](https://fred.stlouisfed.org/data/IPMAN) (2026-10-16) and [BTS air passenger miles](https://fred.stlouisfed.org/data/AIRRPMTSID11) (2026-10-01). Company mapping: [Boeing](https://investors.boeing.com/investors/news/press-release-details/2026/Boeing-Reports-Fourth-Quarter-Results/default.aspx), [GE Aerospace](https://www.geaerospace.com/news/articles/smooth-takeoff-ge-aerospace-releases-first-annual-report-standalone-company), [RTX](https://www.rtx.com/news/news-center/2026/01/27/rtx-reports-2025-results-and-announces-2026-outlook-). Full source register, frozen data, analysis, tests, results and computed figures accompany this notebook.''')
code('''summary={'observations':len(raw),'oos_origins':len(o),'rmse_mean_pp':round(ra.rmse(o.actual,o['mean']),3),'rmse_macro_pp':round(ra.rmse(o.actual,o.macro),3),'rmse_full_pp':round(ra.rmse(o.actual,o.full),3),'macro_minus_full_pp':round(delta,3),'bootstrap_ci_pp':ci.round(3).tolist(),'vintage':'latest revised, NOT PIT','verdict':'FAILED incremental macro prediction'}
display(pd.DataFrame([summary]).T.rename(columns={0:'value'}))''')
nb.cells=c
nbf.validate(nb)
nbf.write(nb,ROOT/'research.ipynb')
print('Created',len(c),'cells:',sum(x.cell_type=='code' for x in c),'code and',sum(x.cell_type=='markdown' for x in c),'markdown')
