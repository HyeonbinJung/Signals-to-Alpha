from pathlib import Path
import json,nbformat,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parent
headings=['01. Abstract','02. Research Design & Hypotheses','03. Industry Context','04. Data & Source Integrity','05. Point-in-Time Availability','06. Factor Construction','07. Exposure & Transmission','08. Outcomes & Baselines','09. Empirical Findings','10. Robustness & Placebos','11. Regime Sensitivity','12. Bias Audit & Verdict','13. Reproduction','14. Next-Stage Protocol','15. Sources & Artifacts']
readme=(ROOT/'README.md').read_text()
assert [line[3:] for line in readme.splitlines() if line.startswith('## ')]==headings
manifest=json.loads((ROOT/'study.json').read_text())
assert manifest['schema_version']==1 and manifest['equity_alpha_established'] is False
for field in ('notebook','source_register','analysis_entrypoint','requirements','notes_file'):
 assert (ROOT/manifest[field]).is_file(),field
for field in ('data_files','result_files'):
 for name in manifest[field]:assert (ROOT/name).is_file(),name
nb=nbformat.read(ROOT/'research.ipynb',as_version=4)
assert len(nb.cells)>=40
assert [c.source.splitlines()[0][3:] for c in nb.cells if c.cell_type=='markdown' and c.source.startswith('## ')]==headings
code=[c for c in nb.cells if c.cell_type=='code']
assert all(c.execution_count is not None for c in code)
assert not any(o.output_type=='error' for c in code for o in c.outputs)
images=sum(any(o.output_type=='display_data' and 'image/png' in o.data for o in c.outputs) for c in code)
assert images>=3
assert len(list((ROOT/'figures').glob('*.png')))>=3
s=json.loads((ROOT/'results'/'summary.json').read_text())
assert s['n_oos_origins']==65 and s['n_oos_predictions_per_model']==260
assert s['publication_vintage']=='UNKNOWN' and s['total_return_adjustment']=='UNKNOWN'
print('PASS: exact 15-section README/notebook,',len(nb.cells),'cells,',len(code),'executed,',images,'image cells; all study.json paths valid')
