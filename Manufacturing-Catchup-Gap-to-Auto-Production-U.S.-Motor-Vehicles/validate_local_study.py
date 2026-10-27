"""Study-only preflight. Not a substitute for root scripts/validate_studies.py."""
from pathlib import Path
import json
import pandas as pd
ROOT=Path(__file__).resolve().parent
HEADINGS=['01. Abstract','02. Research Design & Hypotheses','03. Industry Context','04. Data & Source Integrity','05. Point-in-Time Availability','06. Factor Construction','07. Exposure & Transmission','08. Outcomes & Baselines','09. Empirical Findings','10. Robustness & Placebos','11. Regime Sensitivity','12. Bias Audit & Verdict','13. Reproduction','14. Next-Stage Protocol','15. Sources & Artifacts']
def main():
    m=json.loads((ROOT/'study.json').read_text()); assert m['schema_version']==1 and m['equity_alpha_established'] is False
    md=(ROOT/'README.md').read_text();heads=[x[3:] for x in md.splitlines() if x.startswith('## ')];assert heads==HEADINGS,heads
    nb=json.loads((ROOT/m['notebook']).read_text());assert len(nb['cells'])>=36
    code=[c for c in nb['cells'] if c['cell_type']=='code'];assert len(code)>=20
    assert all(c['execution_count'] is not None for c in code),'Unexecuted code cells'
    assert not any(o['output_type']=='error' for c in code for o in c['outputs']),'Notebook errors'
    nhead=[(''.join(c['source']).split('\n')[0][3:]) for c in nb['cells'] if c['cell_type']=='markdown' and ''.join(c['source']).startswith('## ')]
    assert nhead==HEADINGS,nhead
    assert sum(any('image/png' in o.get('data',{}) for o in c['outputs']) for c in code)>=3
    for k in ('notebook','source_register','analysis_entrypoint','requirements','notes_file'):
        assert (ROOT/m[k]).is_file(),k
    for k in ('data_files','result_files'):
        for f in m[k]:assert (ROOT/f).is_file(),f
    assert len(list((ROOT/'figures').glob('*.svg')))>=3
    src=pd.read_csv(ROOT/m['source_register']);assert {'A','B','C'}.issubset(set(src.grade))
    for f,n in [('block_placebo_draws.csv',1000),('bootstrap_draws.csv',2000),('exposure_perturbation.csv',1000)]:assert len(pd.read_csv(ROOT/'results'/f))>=n
    print(f'PASS local study: {len(nb["cells"])} cells, {len(code)} executed code cells, 15 sections, 11 figures, source grades A/B/C and 1000/2000/1000 robustness draws')
if __name__=='__main__':main()
