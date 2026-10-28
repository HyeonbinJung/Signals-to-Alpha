from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parent
p=ROOT/'research.ipynb'
nb=nbformat.read(p,as_version=4)
client=NotebookClient(nb,timeout=240,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}},allow_errors=False)
client.execute()
nbformat.write(nb,p)
code=[c for c in nb.cells if c.cell_type=='code']
print(f'EXECUTED {sum(c.execution_count is not None for c in code)}/{len(code)} code cells; {sum(len(c.outputs) for c in code)} saved output blocks; {sum(any(o.output_type=="display_data" and "image/png" in o.data for o in c.outputs) for c in code)} image-output cells')
