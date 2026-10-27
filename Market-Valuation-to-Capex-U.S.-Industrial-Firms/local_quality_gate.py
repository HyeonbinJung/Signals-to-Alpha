"""Pre-publication check for this study; repo-wide validator runs in GitHub CI."""
from pathlib import Path
import json, re
import pandas as pd
R=Path(__file__).resolve().parent
m=json.loads((R/'study.json').read_text())
headings=['01. Abstract','02. Research Design & Hypotheses','03. Industry Context','04. Data & Source Integrity','05. Point-in-Time Availability','06. Factor Construction','07. Exposure & Transmission','08. Outcomes & Baselines','09. Empirical Findings','10. Robustness & Placebos','11. Regime Sensitivity','12. Bias Audit & Verdict','13. Reproduction','14. Next-Stage Protocol','15. Sources & Artifacts']
actual=[line[3:] for line in (R/'README.md').read_text().splitlines() if line.startswith('## ')]
assert actual==headings,(actual,headings)
nb=json.loads((R/m['notebook']).read_text())
nbhead=[line[3:] for c in nb['cells'] if c['cell_type']=='markdown' for line in ''.join(c['source']).splitlines() if line.startswith('## ')]
assert nbhead==headings,(nbhead,headings)
assert len(nb['cells'])>=36
codes=[c for c in nb['cells'] if c['cell_type']=='code']
assert all(c['execution_count'] is not None for c in codes)
assert not any(o.get('output_type')=='error' for c in codes for o in c.get('outputs',[]))
assert sum('image/png' in o.get('data',{}) for c in codes for o in c.get('outputs',[]))>=3
assert len(list((R/'figures').glob('*.svg')))>=3
assert m['equity_alpha_established'] is False and m['point_in_time_verified'] is False
for key in ['notebook','source_register','analysis_entrypoint','requirements','notes_file']:
    assert (R/m[key]).is_file(),key
for key in ['data_files','result_files']:
    for p in m[key]:assert (R/p).is_file(),p
sources=pd.read_csv(R/'data/source_register.csv')
assert len(sources)>=5 and sources.url.str.startswith('http').all()
assert sources.publication_date.notna().all() and sources.pit_status.notna().all()
for f,n in [('block_shuffle_placebo.csv',1000),('bootstrap_year_blocks.csv',2000),('exposure_perturbations.csv',1000)]:
    assert len(pd.read_csv(R/'results'/f))==n
print('PASS local quality gate:',len(nb['cells']),'notebook cells;',len(codes),'executed code cells;',len(list((R/'figures').glob('*.svg'))),'SVG figures; 15 canonical chapters; source/manifest/results present')
