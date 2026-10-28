"""Independent subprocess for large Monte Carlo draws; prevents shared-process stalls."""
import sys
from pathlib import Path
from computer_factor import *
ROOT=Path(__file__).resolve().parent
raw=load_and_qa(ROOT/'data/frozen_g17_electronics_2026-10-19.csv')
p=make_panel(raw)
mode=sys.argv[1]
if mode=='placebo':
    o=oos(p); draws,pval=block_placebo(p,subset_gain(o),draws=1000)
    draws.to_csv(ROOT/'results/block_placebo_1000.csv',index=False)
elif mode=='bootstrap':
    o=oos(p);bootstrap_paired(o,draws=2000).to_csv(ROOT/'results/paired_block_bootstrap_2000.csv',index=False)
elif mode=='exposure':
    exposure_perturbation(raw,draws=1000).to_csv(ROOT/'results/exposure_perturbation_1000.csv',index=False)
else: raise ValueError(mode)
print('PASS',mode)
