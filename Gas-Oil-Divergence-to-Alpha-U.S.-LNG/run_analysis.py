"""Frozen EIA monthly natural gas/oil relative-price factor; not investable P&L."""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
FEATURES = ["gas_mom3","gas_mom12","wti_mom3","wti_mom12","oil_gas_spread"]
MODELS = {"mean":[],"control":FEATURES[:4],"full":FEATURES,
          "spread_only":FEATURES[4:],"gas_only":FEATURES[:2],
          "gas_spread":FEATURES[:2]+FEATURES[4:]}

def load_data():
    df=pd.read_csv(ROOT/"data/henry_hub_wti_monthly.csv",parse_dates=["date"])
    assert list(df.columns)==["date","henry_hub_usd_mmbtu","wti_usd_barrel"]
    assert df.date.is_unique and not df.isna().any().any()
    assert (df.iloc[:,1:]>0).all().all()
    assert list(df.date.dt.to_period("M"))==list(pd.period_range(df.date.iloc[0],df.date.iloc[-1],freq="M"))
    return df

def make_panel(df,h=3,spread_lag=0):
    if h<1 or spread_lag<0: raise ValueError("invalid horizon or lag")
    g=df.henry_hub_usd_mmbtu.to_numpy(float)
    w=df.wti_usd_barrel.to_numpy(float)
    rows=[]
    for t in range(13+spread_lag,len(df)-h):
        k=t-1
        ks=t-1-spread_lag
        x=[100*np.log(g[k]/g[k-3]),100*np.log(g[k]/g[k-12]),
           100*np.log(w[k]/w[k-3]),100*np.log(w[k]/w[k-12]),
           np.log(w[ks]/(6*g[ks]))]
        rows.append([t,df.date.iloc[t].strftime("%Y-%m"),100*np.log(g[t+h]/g[t-1]),*x])
    return pd.DataFrame(rows,columns=["t","date","y"]+FEATURES)

def ridge_predict(train,test,cols,alpha=10):
    y=train.y.to_numpy(float)
    ym=float(y.mean())
    if not cols: return ym
    X=train[cols].to_numpy(float)
    x=test[cols].to_numpy(dtype=float)
    mu=X.mean(axis=0)
    sd=np.sqrt(((X-mu)**2).mean(axis=0))
    sd[sd==0]=1
    Z=(X-mu)/sd
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(len(cols)),Z.T@(y-ym))
    return float(ym+((x-mu)/sd)@beta)

def evaluate(df,h=3,spread_lag=0,min_train=96):
    panel=make_panel(df,h,spread_lag)
    out=[]
    for _,test in panel.iterrows():
        # Label purge: training outcomes must END no later than t-1.
        train=panel.loc[panel.t+h<=test.t-1]
        if len(train)<min_train: continue
        rec={"t":int(test.t),"date":test.date,"y":float(test.y),"n_train":len(train)}
        for name,cols in MODELS.items():
            rec[name]=ridge_predict(train,test,cols)
        out.append(rec)
    return pd.DataFrame(out)

def score(pred):
    if pred.empty: return {}
    out={"n":len(pred),"start":pred.date.iloc[0],"end":pred.date.iloc[-1]}
    for name in MODELS:
        e=pred.y.to_numpy()-pred[name].to_numpy()
        out[name]={"rmse":float(np.sqrt(np.mean(e**2))),
                   "mae":float(np.mean(np.abs(e))),
                   "hit_rate":float(np.mean(np.sign(pred.y)==np.sign(pred[name])))}
    out["delta_rmse_control_minus_full"]=out["control"]["rmse"]-out["full"]["rmse"]
    return out

def block_ci(pred,replications=1000,block=12,seed=20261019):
    rng=np.random.default_rng(seed)
    n=len(pred)
    e0=(pred.y-pred.control).to_numpy()
    e1=(pred.y-pred.full).to_numpy()
    diffs=[]
    for _ in range(replications):
        ix=[]
        while len(ix)<n:
            j=int(rng.integers(0,n-block+1))
            ix.extend(range(j,j+block))
        ix=np.asarray(ix[:n])
        diffs.append(np.sqrt(np.mean(e0[ix]**2))-np.sqrt(np.mean(e1[ix]**2)))
    return [float(v) for v in np.quantile(diffs,[.025,.975])]

def run(write=False):
    df=load_data()
    p=evaluate(df,3)
    robustness={"h1":score(evaluate(df,1)),"h6":score(evaluate(df,6)),
                "pre2016":score(p[p.date<"2016-01"]),
                "since2016":score(p[p.date>="2016-01"]),
                "since2020":score(p[p.date>="2020-01"]),
                "excluding_2022":score(p[~p.date.str.startswith("2022-")])}
    placebo={f"spread_lag_{k}":score(evaluate(df,3,k)) for k in [12,24,36]}
    res={"research_date":"2026-10-19","data_months":len(df),
         "data_start":df.date.iloc[0].strftime("%Y-%m"),
         "data_end":df.date.iloc[-1].strftime("%Y-%m"),
         "target":"100*log(Gas[t+3]/Gas[t-1]); features through t-1",
         "primary":score(p),"robustness":robustness,
         "stale_spread_placebos":placebo,
         "bootstrap_95_ci_delta_rmse":block_ci(p),
         "historical_pit_vintages_verified":False,
         "equity_alpha_tested":False}
    if write:
        dest=ROOT/"results"
        dest.mkdir(exist_ok=True)
        p.drop(columns=["t"]).to_csv(dest/"oos_predictions.csv",index=False)
        (dest/"metrics.json").write_text(json.dumps(res,indent=2)+"\n")
    return res

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--write",action="store_true")
    print(json.dumps(run(write=parser.parse_args().write),indent=2))
