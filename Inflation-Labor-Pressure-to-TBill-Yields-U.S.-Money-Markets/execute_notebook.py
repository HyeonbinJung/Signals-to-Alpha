"""Run every notebook cell and persist computed outputs in the research notebook."""
import json,sys,time,traceback
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parent
path=ROOT/'research.ipynb'
nb=nbformat.read(path,as_version=4)
started=time.time()
try:
    nb=NotebookClient(nb,timeout=900,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    errs=[(i,o.get('ename')) for i,c in enumerate(nb.cells) if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
    if errs:raise RuntimeError(f'Error outputs: {errs}')
    nbformat.write(nb,path)
    counts={'cells':len(nb.cells),'code_cells':sum(c.cell_type=='code' for c in nb.cells),
            'executed_code_cells':sum(c.cell_type=='code' and c.execution_count is not None for c in nb.cells),
            'image_outputs':sum(('image/png' in o.get('data',{}) or 'image/svg+xml' in o.get('data',{})) for c in nb.cells for o in c.get('outputs',[])),
            'error_outputs':len(errs),'elapsed_seconds':round(time.time()-started,2),'status':'PASS'}
    (ROOT/'logs'/'notebook_execution.json').write_text(json.dumps(counts,indent=2))
    print(json.dumps(counts,indent=2))
except Exception:
    (ROOT/'logs'/'notebook_execution_error.log').write_text(traceback.format_exc())
    traceback.print_exc();sys.exit(1)
