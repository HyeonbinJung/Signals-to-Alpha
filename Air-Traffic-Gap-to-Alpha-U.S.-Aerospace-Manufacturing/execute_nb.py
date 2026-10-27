from pathlib import Path
import nbformat,time,traceback
from nbclient import NotebookClient
p=Path(__file__).resolve().parent
nb=nbformat.read(p/'research.ipynb',as_version=4)
log=(p/'results/notebook_execution.log').open('w')
def report(event,cell=None,cell_index=None,**kwargs):
 s=f'{time.strftime("%H:%M:%S")} {event} {cell_index} {str(cell.source)[:50]!r}' if cell is not None else f'{time.strftime("%H:%M:%S")} {event}'
 print(s,flush=True);log.write(s+'\n');log.flush()
client=NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(p)}},on_cell_start=lambda **kw:report('start',**kw),on_cell_complete=lambda **kw:report('complete',**kw),on_cell_error=lambda **kw:report('error',**kw))
try:
 client.execute();nbformat.write(nb,p/'research.ipynb');report('SAVED');log.close()
except Exception:
 traceback.print_exc();nbformat.write(nb,p/'research_partial.ipynb');log.close();raise
