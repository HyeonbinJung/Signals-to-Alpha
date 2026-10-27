"""Frozen-snapshot airline fuel-cost leading-indicator falsification.

IMPORTANT: Conservative lags do not reconstruct historical publication vintages.
No securities data or investable alpha claims are made.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd

HORIZON = 3
RELEASE_LAG = 2
MIN_TRAIN = 36
ALPHA = 15.0
WEIGHT_YOY = 0.70
SEED = 20261027

@dataclass(frozen=True)
class StudyConfig:
    horizon: int = HORIZON
    release_lag: int = RELEASE_LAG
    min_train: int = MIN_TRAIN
    alpha: float = ALPHA
    weight_yoy: float = WEIGHT_YOY


def load_frozen(root: Path) -> pd.DataFrame:
    a = pd.read_csv(root / 'data/bts_bls_frozen_2026-10-26.csv', parse_dates=['date'])
    b = pd.read_csv(root / 'data/eia_energy_frozen_2026-10-08.csv')
    b['date'] = pd.to_datetime(b['DATE'] + '-01')
    a = a.merge(b[['date','wti_usd_barrel','henry_hub_usd_mmbtu']], on='date', how='left', validate='one_to_one')
    assert a.date.is_monotonic_increasing and a.date.is_unique
    assert len(a)==153 and a.date.iloc[0]==pd.Timestamp('2014-01-01')
    assert a['AIRRPMTSID11'].notna().sum()==150
    assert (a[['AIRRPMTSID11','CES7072100001','CES7072200001','wti_usd_barrel','henry_hub_usd_mmbtu']].dropna()>0).all().all()
    return a


def log_growth(series: pd.Series, months: int) -> pd.Series:
    x = series.astype(float)
    return 100 * np.log(x / x.shift(months))


def build_panel(raw: pd.DataFrame, config: StudyConfig = StudyConfig()) -> pd.DataFrame:
    t = raw.copy()
    l = config.release_lag
    h = config.horizon
    t['air_persistence'] = log_growth(t['AIRRPMTSID11'], 12).shift(l)
    t['lodging_yoy'] = log_growth(t['CES7072100001'], 12).shift(l)
    t['food_yoy'] = log_growth(t['CES7072200001'], 12).shift(l)
    t['wti_yoy'] = log_growth(t['wti_usd_barrel'], 12).shift(l)
    t['wti_3m'] = log_growth(t['wti_usd_barrel'], 3).shift(l)
    t['henry_yoy'] = log_growth(t['henry_hub_usd_mmbtu'], 12).shift(l)
    t['oil_relief'] = -(config.weight_yoy*t['wti_yoy'] + (1-config.weight_yoy)*t['wti_3m'])
    # Target is the annual log change at t+h, NOT future 3-month growth.
    t['target_air_yoy'] = log_growth(t['AIRRPMTSID11'],12).shift(-h)
    t['target_month'] = t['date'] + pd.DateOffset(months=h)
    t['available_month'] = t['target_month'] + pd.DateOffset(months=l)
    needed=['air_persistence','lodging_yoy','food_yoy','wti_yoy','wti_3m','oil_relief','target_air_yoy']
    return t.dropna(subset=needed).reset_index(drop=True)


def fit_predict_ridge(X: np.ndarray, y: np.ndarray, xt: np.ndarray, alpha: float=ALPHA) -> float:
    """Training-only centering/scaling; fixed Ridge alpha; no test-statistic leakage."""
    X=np.asarray(X,float); y=np.asarray(y,float); xt=np.asarray(xt,float)
    mu=X.mean(axis=0); scale=X.std(axis=0);scale[scale<1e-9]=1.0
    Z=np.clip((X-mu)/scale,-6,6); zt=np.clip((xt-mu)/scale,-6,6)
    Z=Z-Z.mean(axis=0)
    beta=np.linalg.solve(Z.T@Z+alpha*np.eye(Z.shape[1]),Z.T@(y-y.mean()))
    return float(y.mean()+((zt-((X-mu)/scale).clip(-6,6).mean(axis=0))@beta))


def walk_forward(panel: pd.DataFrame, config: StudyConfig=StudyConfig(), signal: np.ndarray|None=None, controls: tuple[str,...]=('air_persistence','lodging_yoy','food_yoy')) -> pd.DataFrame:
    """At formation t, use only training targets whose release t+h+lag <= t."""
    if signal is None: signal=panel.oil_relief.to_numpy(float)
    signal=np.asarray(signal,float)
    y=panel.target_air_yoy.to_numpy(float)
    dates=panel.date.to_numpy()
    available=panel.available_month.to_numpy()
    cx=panel[list(controls)].to_numpy(float)
    out=[]
    for i in range(len(panel)):
        train=np.flatnonzero(available[:i] <= dates[i])
        if len(train)<config.min_train: continue
        base=cx[train]; current=cx[i]
        pred_mean=float(y[train].mean())
        pred_persist=float(panel.air_persistence.iloc[i])
        pred_control=fit_predict_ridge(base,y[train],current,config.alpha)
        pred_full=fit_predict_ridge(np.column_stack((base,signal[train])),y[train],np.r_[current,signal[i]],config.alpha)
        pred_signal=fit_predict_ridge(signal[train,None],y[train],np.array([signal[i]]),config.alpha)
        out.append((panel.date.iloc[i],panel.target_month.iloc[i],len(train),y[i],pred_mean,pred_persist,pred_control,pred_full,pred_signal))
    return pd.DataFrame(out,columns=['formation_date','target_date','n_train','actual','historical_mean','air_persistence','macro_control','oil_augmented','oil_only'])


def scorecard(oos: pd.DataFrame) -> pd.DataFrame:
    y=oos.actual.to_numpy(float)
    rows=[]
    for col in ['historical_mean','air_persistence','macro_control','oil_augmented','oil_only']:
        e=oos[col].to_numpy(float)-y
        rows.append(dict(model=col,n=len(y),rmse=float(np.sqrt(np.mean(e**2))),mae=float(np.mean(np.abs(e))),bias=float(np.mean(e))))
    return pd.DataFrame(rows)


def rmse_gain(oos: pd.DataFrame, challenger: str='oil_augmented', control: str='macro_control') -> float:
    y=oos.actual.to_numpy(float)
    return float(np.sqrt(np.mean((oos[control]-y)**2))-np.sqrt(np.mean((oos[challenger]-y)**2)))


def block_shuffle(x: np.ndarray, rng: np.random.Generator, block: int=12) -> np.ndarray:
    """Non-overlapping whole-year block-order shuffle; last short block retained at end."""
    x=np.asarray(x,float)
    k=len(x)//block
    pieces=[x[j*block:(j+1)*block] for j in range(k)]
    order=rng.permutation(k)
    return np.r_[*(pieces[j] for j in order),x[k*block:]]


def fast_augmented_gain(panel:pd.DataFrame, signal:np.ndarray, config:StudyConfig=StudyConfig(), controls:tuple[str,...]=('air_persistence','lodging_yoy','food_yoy'), base_oos:pd.DataFrame|None=None)->float:
    """Refit challenger at every origin; reuse unchanged control forecasts."""
    if base_oos is None:base_oos=walk_forward(panel,config,controls=controls)
    signal=np.asarray(signal,float)
    y=panel.target_air_yoy.to_numpy(float)
    dates=panel.date.to_numpy();available=panel.available_month.to_numpy()
    cx=panel[list(controls)].to_numpy(float)
    predictions=[]
    for i in range(len(panel)):
        train=np.flatnonzero(available[:i]<=dates[i])
        if len(train)<config.min_train:continue
        X=np.column_stack((cx[train],signal[train]))
        predictions.append(fit_predict_ridge(X,y[train],np.r_[cx[i],signal[i]],config.alpha))
    assert len(predictions)==len(base_oos)
    ctrl=base_oos.macro_control.to_numpy(float);actual=base_oos.actual.to_numpy(float)
    return float(np.sqrt(np.mean((ctrl-actual)**2))-np.sqrt(np.mean((np.asarray(predictions)-actual)**2)))


def placebo(panel: pd.DataFrame, actual_gain: float, n: int=1000, seed: int=SEED) -> pd.DataFrame:
    rng=np.random.default_rng(seed)
    values=panel.oil_relief.to_numpy(float)
    rows=[];base=walk_forward(panel)
    for i in range(n):
        rows.append((i,fast_augmented_gain(panel,block_shuffle(values,rng),base_oos=base)))
    return pd.DataFrame(rows,columns=['rep','gain_rmse'])


def circular_bootstrap(oos: pd.DataFrame,n:int=2000,block:int=12,seed:int=SEED+1)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    a=(oos.macro_control-oos.actual).to_numpy(float)
    b=(oos.oil_augmented-oos.actual).to_numpy(float)
    m=len(a); k=int(np.ceil(m/block)); rows=[]
    for j in range(n):
        starts=rng.integers(0,m,size=k)
        ix=np.concatenate([(s+np.arange(block))%m for s in starts])[:m]
        rows.append((j,float(np.sqrt(np.mean(a[ix]**2))-np.sqrt(np.mean(b[ix]**2)))))
    return pd.DataFrame(rows,columns=['rep','gain_rmse'])


def exposure_sensitivity(panel:pd.DataFrame,n:int=1000,seed:int=SEED+2)->pd.DataFrame:
    rng=np.random.default_rng(seed)
    weights=rng.uniform(0.3,0.9,size=n)
    a=panel.wti_yoy.to_numpy(float);b=panel.wti_3m.to_numpy(float)
    rows=[];base=walk_forward(panel)
    for i,w in enumerate(weights):
        signal=-(w*a+(1-w)*b)
        rows.append((i,w,fast_augmented_gain(panel,signal,base_oos=base)))
    return pd.DataFrame(rows,columns=['rep','w_yoy','gain_rmse'])


def leave_year_out(oos:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for year in sorted(oos.formation_date.dt.year.unique()):
        x=oos[oos.formation_date.dt.year!=year]
        if len(x)>10:rows.append((int(year),len(x),rmse_gain(x)))
    return pd.DataFrame(rows,columns=['excluded_formation_year','n','gain_rmse'])


def regime_sensitivity(oos:pd.DataFrame)->pd.DataFrame:
    dates=oos.target_date
    masks={'all':np.ones(len(oos),bool),'exclude_2020_2021':~dates.dt.year.isin([2020,2021]),'pre_2020':dates.dt.year<2020,'2022_plus':dates.dt.year>=2022,'2024_plus':dates.dt.year>=2024}
    rows=[]
    for k,v in masks.items():
        sub=oos[v]
        if len(sub)>8:rows.append((k,len(sub),rmse_gain(sub)))
    return pd.DataFrame(rows,columns=['regime','n','gain_rmse'])


def alternative_horizons(raw:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for h in [1,3,6]:
        for lag in [2,3,4]:
            cfg=StudyConfig(horizon=h,release_lag=lag)
            panel=build_panel(raw,cfg)
            oos=walk_forward(panel,cfg)
            rows.append((h,lag,len(oos),rmse_gain(oos)))
    return pd.DataFrame(rows,columns=['horizon_months','feature_lag_months','n','gain_rmse'])


def ablations(panel:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for name,ctrl in [('base_all',('air_persistence','lodging_yoy','food_yoy')),('no_lodging',('air_persistence','food_yoy')),('no_food',('air_persistence','lodging_yoy')),('persistence_only',('air_persistence',))]:
        oos=walk_forward(panel,controls=ctrl)
        rows.append((name,len(oos),rmse_gain(oos)))
    return pd.DataFrame(rows,columns=['controls','n','gain_rmse'])
