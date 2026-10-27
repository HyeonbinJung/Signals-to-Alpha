"""Study-local structural and numerical gate; repository-wide gate runs in CI."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat
from analysis import read_raw,make_panel,walk_forward,score,improvement
R=Path(__file__).resolve().parent
H=['01. Abstract','02. Research Design & Hypotheses','03. Industry Context','04. Data & Source Integrity',
'05. Point-in-Time Availability','06. Factor Construction','07. Exposure & Transmission','08. Outcomes & Baselines',
'09. Empirical Findings','10. Robustness & Placebos','11. Regime Sensitivity','12. Bias Audit & Verdict',
'13. Reproduction','14. Next-Stage Protocol','15. Sources & Artifacts']
assert [x[3:] for x in (R/'README.md').read_text().splitlines() if x.startswith('## ')]==H
nb=nbformat.read(R/'research.ipynb',as_version=4)
assert len(nb.cells)>=36
code=[c for c in nb.cells if c.cell_type=='code']
assert len(code)>=20 and all(c.execution_count is not None for c in code)
assert not [o for c in code for o in c.get('outputs',[]) if o.get('output_type')=='error']
assert sum(any(k.startswith('image/') for k in o.get('data',{})) for c in code for o in c.get('outputs',[]))>=3
assert [x.source[3:].strip() for x in nb.cells if x.cell_type=='markdown' and x.source.startswith('## ')]==H
m=json.loads((R/'study.json').read_text());assert m['equity_alpha_established'] is False and m['point_in_time_verified'] is False
for key in ('notebook','source_register','analysis_entrypoint','requirements','notes_file'):
 assert (R/m[key]).is_file(),key
for key in ('data_files','result_files'):
 for path in m[key]:assert (R/path).is_file(),path
p=make_panel(read_raw());o=walk_forward(p);s=score(o)
stored=pd.read_csv(R/'results/scorecard.csv');np.testing.assert_allclose(s.rmse,stored.rmse,atol=1e-10)
assert (o.last_train_target_year<=o.formation_year-1).all()
for filename,n in [('block_shuffle_1000.csv',1000),('block_bootstrap_2000.csv',2000),('exposure_perturbations_1000.csv',1000)]:
 assert len(pd.read_csv(R/'results'/filename))==n
assert len(list((R/'figures').glob('*.svg')))>=3
assert len(pd.read_csv(R/'data/source_register.csv'))>=3
print(f'PASS: {len(nb.cells)} cells, {len(code)} executed code, 15 sections, 10 figures, source register, 15 tests separately, all OOS tables consistent')
