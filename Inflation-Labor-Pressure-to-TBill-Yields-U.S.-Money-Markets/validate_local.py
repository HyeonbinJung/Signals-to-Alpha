"""Study-specific publication checks; not a substitute for repository-wide validator."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parent
HEADINGS=["01. Abstract","02. Research Design & Hypotheses","03. Industry Context","04. Data & Source Integrity","05. Point-in-Time Availability","06. Factor Construction","07. Exposure & Transmission","08. Outcomes & Baselines","09. Empirical Findings","10. Robustness & Placebos","11. Regime Sensitivity","12. Bias Audit & Verdict","13. Reproduction","14. Next-Stage Protocol","15. Sources & Artifacts"]
m=json.loads((R/'study.json').read_text());nb=json.loads((R/m['notebook']).read_text());readme=(R/'README.md').read_text()
assert [x[3:] for x in readme.splitlines() if x.startswith('## ')]==HEADINGS
assert all((R/x).is_file() for x in m['data_files']+m['result_files'])
assert all((R/m[k]).is_file() for k in ['notebook','source_register','analysis_entrypoint','requirements','notes_file'])
assert m['equity_alpha_established'] is False and m['source_vintage_pit_verified'] is False
assert nb['nbformat']==4 and len(nb['cells'])>=36
assert sum(c['cell_type']=='code' for c in nb['cells'])>=20
assert sum(c['cell_type']=='code' and c.get('execution_count') is not None for c in nb['cells'])==sum(c['cell_type']=='code' for c in nb['cells'])
assert not any(o.get('output_type')=='error' for c in nb['cells'] for o in c.get('outputs',[]))
assert sum('image/png' in o.get('data',{}) for c in nb['cells'] for o in c.get('outputs',[]))>=3
assert all(any(h in ''.join(c.get('source',[])) for c in nb['cells'] if c['cell_type']=='markdown') for h in HEADINGS)
assert len(list((R/'figures').glob('*.png')))>=3
print('PASS: 15 sections, all referenced files, executed notebook, >=3 stored plots, no error outputs')
