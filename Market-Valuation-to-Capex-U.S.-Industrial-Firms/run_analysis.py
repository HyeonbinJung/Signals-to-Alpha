"""Run all archived calculations from the frozen 11-firm panel."""
from pathlib import Path
from analysis import run
if __name__=='__main__':
    import json
    print(json.dumps(run(Path(__file__).resolve().parent,fast=False),indent=2))
