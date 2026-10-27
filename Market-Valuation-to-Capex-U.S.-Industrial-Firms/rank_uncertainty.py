"""Year-block uncertainty for firm-fundamental rank IC and residual spread."""
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent
r=pd.read_csv(ROOT/'results/fundamental_rank_diagnostics.csv')
years=np.sort(r.year.unique());n=len(years);rng=np.random.default_rng(20261027)
records=[]
for i in range(2000):
    sampled=[]
    while len(sampled)<n:
        start=int(rng.integers(0,n));sampled.extend([years[(start+j)%n] for j in range(2)])
    sub=pd.concat([r[r.year==y] for y in sampled[:n]],ignore_index=True)
    records.append({'iteration':i+1,'mean_fundamental_rank_ic':sub.fundamental_residual_rank_ic.mean(),
                    'mean_investment_residual_spread':sub.top3_minus_bottom3_realized_residual_log.mean()})
result=pd.DataFrame(records)
result.to_csv(ROOT/'results/fundamental_rank_yearblock_uncertainty.csv',index=False)
print(result[['mean_fundamental_rank_ic','mean_investment_residual_spread']].quantile([.025,.5,.975]).to_string())
