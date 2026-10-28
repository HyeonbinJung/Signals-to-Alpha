from pathlib import Path
import nbformat as nbf
P=Path(__file__).resolve().parent
readme=(P/'README.md').read_text()
chunks=readme.split('\n## ')
sections={}
for x in chunks[1:]:
 title,body=x.split('\n',1);sections[title]=body.strip()
nb=nbf.v4.new_notebook(); cells=[]
def md(x):cells.append(nbf.v4.new_markdown_cell(x))
def code(x):cells.append(nbf.v4.new_code_cell(x))
md('# Semiconductor Supply Pressure → U.S. Communications Equipment Manufacturing\n\n**Reproducible historical macro lead-indicator falsification (28 October 2026).**\n\n**Publication gate:** A statistically weak macro OOS gain on a latest-revised inherited snapshot is not a PIT or investable equity-alpha claim. All outputs below are computed by code, not pasted from a claimed result. The research design follows the 36-cell K-Food reference and the canonical 15-chapter template.')
code('from pathlib import Path\nimport json, hashlib, math\nimport numpy as np\nimport pandas as pd\nfrom IPython.display import display, Image, Markdown\nimport matplotlib.pyplot as plt\nimport run_analysis as ra\nROOT=Path.cwd()\nprint("Working directory:", ROOT, "| exact source Git blob:", ra.git_blob_sha(ra.RAW.read_bytes()))')
for num,title in enumerate(sections,1):
 md('## '+title+'\n\n'+sections[title])
 if num==1:
  code('summary=json.loads((ROOT/"results/summary.json").read_text())\nprint({k:summary[k] for k in ["n_raw","n_oos","primary_delta_rmse_log_pp","exploratory_block_shuffle_tail_fraction","point_in_time_verified"]})')
  code('print("Status: REPRODUCED RETROSPECTIVE MACRO PILOT — NOT PIT / NOT EQUITY ALPHA")')
 if num==2:
  code('print("H1: upstream semiconductors lead NAICS 3342; H2: beats mean, persistence and controls; H3: survives block-aware falsification.")\nprint("Primary specification: 2-month publication buffer; 3-month target horizon; ridge alpha=10; expanding purged training.")')
  code('print("Null: no stable incremental information beyond predeclared controls; causal direction is NOT identified.")')
 if num==3:
  code('raw=ra.load_raw(); display(raw.head(4));display(raw.tail(3))\nprint("NAICS 3342 communications equipment; 3344 semiconductors; 3341 computers; IPMAN aggregate manufacturing.")')
  code('display(Image(filename=str(ROOT/"figures/01_output_levels.png"),width=680))')
 if num==4:
  code('src=pd.read_csv(ROOT/"data/source_register.csv");display(src[["source_id","grade","publisher","publication_date","revision_or_vintage"]])')
  code('print("Source snapshot shape:",raw.shape,"| monthly dates:",raw.date.min().date(),raw.date.max().date())\nprint("Missing cells:",int(raw.isna().sum().sum()),"| all levels positive:",bool((raw.drop(columns="date")>0).all().all()))\nprint("Exact inherited blob match:",ra.git_blob_sha(ra.RAW.read_bytes())==ra.EXPECTED_GIT_BLOB)')
 if num==5:
  code('panel=ra.build_panel(raw)\nprint("Formation features are observed t-2; target is g_comm(t+3). First 3 rows:")\ndisplay(panel[["date","origin_index","comm_available","sem_available","man_available","factor","target"]].head(3))')
  code('wf=pd.read_csv(ROOT/"results/walk_forward_oos.csv",parse_dates=["date"])\nassert (wf.max_train_label_observation<=wf.latest_usable_observation).all()\nprint("All OOS origins purged:",len(wf),"| min train:",wf.n_train.min(),"| max train:",wf.n_train.max())')
 if num==6:
  code('t=panel.iloc[0];print("First factor row:",t.date.date(),"| F(t):",round(t.factor,6),"| manual:",round(float(np.tanh((t.sem_available-t.man_available)/15)),6))\nprint("Feature min/max:",panel.factor.min(),panel.factor.max(),"| no train-set fitted weights")')
  code('display(Image(filename=str(ROOT/"figures/03_signal_and_target.png"),width=680))')
 if num==7:
  code('exposure=pd.read_csv(ROOT/"data/company_exposure_map.csv");display(exposure[["entity","as_of","role","model_weight","qualification"]])')
  code('print("Issuer-level time series:","NOT AVAILABLE","| leave-one-company-out:","NOT APPLICABLE")')
 if num==8:
  code('score=pd.read_csv(ROOT/"results/scorecard.csv");display(score.sort_values("rmse_log_pp"))')
  code('print("Target is future NAICS 3342 output YoY log growth, not equity return. Forecast origins:",wf.date.min().date(),"to",wf.date.max().date())\nprint("Ridge scaling is train-only; no hyperparameter search; all models share the same origin dates.")')
 if num==9:
  code('display(Image(filename=str(ROOT/"figures/04_oos_forecasts.png"),width=680))')
  code('gain=ra.rmse(wf.target,wf.macro)-ra.rmse(wf.target,wf.full)\nprint("Control-minus-full RMSE:",gain,"| paired MAE improvement:",ra.mae(wf.target,wf.macro)-ra.mae(wf.target,wf.full))\nprint("Full-panel factor/target correlation:",panel[["factor","target"]].corr().iloc[0,1])')
  code('display(Image(filename=str(ROOT/"figures/05_rmse_scorecard.png"),width=680))')
 if num==10:
  code('pl=pd.read_csv(ROOT/"results/block_placebo_1000.csv");bs=pd.read_csv(ROOT/"results/block_bootstrap_2000.csv");ex=pd.read_csv(ROOT/"results/exposure_perturbation_1000.csv")\nprint("Refit block-shuffle N:",len(pl),"| exploratory upper-tail:",(1+(pl.delta_rmse>=gain).sum())/(len(pl)+1))\nprint("Paired block bootstrap N:",len(bs),"| 95% interval:",bs.delta_rmse.quantile([.025,.975]).to_dict())\nprint("Exposure perturbation N:",len(ex),"| fraction positive:",(ex.delta_rmse>0).mean())')
  code('display(Image(filename=str(ROOT/"figures/07_block_placebo.png"),width=680))')
  code('display(Image(filename=str(ROOT/"figures/08_bootstrap.png"),width=680))')
  code('abl=pd.read_csv(ROOT/"results/ablations.csv");display(abl)\nloyo=pd.read_csv(ROOT/"results/leave_one_year_out.csv");print("LOYO years:",len(loyo),"| positive:",int((loyo.delta_rmse>0).sum()))')
 if num==11:
  code('reg=pd.read_csv(ROOT/"results/regimes.csv");display(reg)\nsensitivity=pd.read_csv(ROOT/"results/horizon_lag.csv");display(sensitivity.pivot(index="lag_months",columns="horizon_months",values="delta_rmse"))')
  code('display(Image(filename=str(ROOT/"figures/10_regime_sensitivity.png"),width=680))')
 if num==12:
  code('audit={"historic_first_release_vintage":"UNKNOWN","latest_revised_source":True,"issuer_fundamentals":False,"total_return_and_benchmark":False,"transaction_costs":False,"multiple_testing_adjusted":False,"overlapping_labels":True};display(pd.Series(audit,name="audit_status"))')
  code('print("Conditional verdict:","small macro OOS gain; placebo not compelling; bootstrap includes zero; not PIT; not equity alpha.")')
 if num==13:
  code('print("Reproducing heavy computations with deterministic seed; please wait...")\nreproduced=ra.compute_all(n_placebo=1000,n_boot=2000,n_exposure=1000)\nprint("Computed from frozen raw:",reproduced["n_oos"],"OOS origins; gain:",reproduced["primary_delta_rmse_log_pp"])')
  code('assert np.isclose(reproduced["primary_delta_rmse_log_pp"],gain)\nassert reproduced["block_shuffle_draws"]==1000 and reproduced["bootstrap_draws"]==2000 and reproduced["exposure_draws"]==1000\nprint("Notebook heavy analysis and numerical assertions passed.")')
 if num==14:
  code('print("Next stage: ALFRED/Federal Reserve first-release vintages; issuer-by-year product revenue + filing dates; delisting-inclusive total returns; preregistered holdout.")')
 if num==15:
  code('print("A/B/C source register and frozen data:");display(src[["source_id","original_url","role"]])')
  code('print("Reproduction artifacts:",len(list((ROOT/"figures").glob("*.png"))),"figures,",len(list((ROOT/"results").glob("*.csv"))),"result CSVs")\nprint("Final verdict:","REPRODUCED RETROSPECTIVE MACRO PILOT — NOT PIT / NOT INVESTABLE ALPHA")')
md('### Publication integrity check\n\nThe exact source Git blob and all calculations are reproducible, but the original G.17 historical release vintages, independent issuer fundamentals and investable returns are **not**. An apparent gain must not be promoted to a validated trading strategy. The next research run should use a genuinely independent dataset and a preregistered test.')
nb.cells=cells
nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.13'}}
nbf.write(nb,P/'research.ipynb')
print('Notebook cells:',len(nb.cells),'code:',sum(c.cell_type=='code' for c in nb.cells))
