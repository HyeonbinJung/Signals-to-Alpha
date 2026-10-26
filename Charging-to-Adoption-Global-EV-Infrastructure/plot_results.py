"""Render frozen-data figures; no invented or illustrative empirical points."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ev_charging_alpha import ROOT, read_data, panel, per_year_rank_ic, metrics, country_leaveout


def create_all_figures():
    raw=read_data()
    p=panel(raw)
    oos=pd.read_csv(ROOT/'results'/'walk_forward_oos.csv')
    null=pd.read_csv(ROOT/'results'/'placebo_null_distribution.csv').iloc[:,0]
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    paths=[]
    def finish(name):
        plt.tight_layout();plt.savefig(out/name,dpi=100,bbox_inches='tight');plt.close();paths.append('figures/'+name)
    # 1. EV share trajectories: chosen countries, explicit not full universe
    fig,ax=plt.subplots(figsize=(10,5))
    for c in ['Norway','China','Germany','France','USA','Japan','Korea']:
        d=raw[raw.country==c];ax.plot(d.year,d.ev_sales_share_pct,marker='.',label=c)
    ax.set(title='EV share of new car sales — selected countries (IEA 2024 vintage)',xlabel='Calendar year',ylabel='Percent of new car sales');ax.legend(ncol=2);ax.grid(alpha=.2);finish('01_ev_share_paths.png')
    # 2. infrastructure mix country-year
    d=raw[raw.year==2023].copy();d['fast_share']=100*d.public_fast_points/(d.public_fast_points+d.public_slow_points)
    fig,ax=plt.subplots(figsize=(9,5));ax.barh(d.sort_values('fast_share').country,d.sort_values('fast_share').fast_share)
    ax.set(title='2023 fast chargers / all public charging points (selected markets)',xlabel='Fast-charger fraction (%)');finish('02_fast_charger_mix.png')
    # 3. lagged factor vs next sales-share acceleration
    d=p[p.year==2023]
    fig,ax=plt.subplots(figsize=(8,5));score=.5*np.tanh(d.fast_log_growth_l1)+.5*np.tanh(d.slow_log_growth_l1)
    ax.scatter(score,d.target_pp)
    for x,y,name in zip(score,d.target_pp,d.country):ax.annotate(name,(x,y),fontsize=7,xytext=(3,2),textcoords='offset points')
    ax.set(title='2022 charging growth score vs 2023 EV sales-share change',xlabel='Fixed-scale charging factor (lagged)',ylabel='2023 share change (percentage points)');ax.grid(alpha=.2);finish('03_factor_scatter_2023.png')
    # 4. OOS forecast RMSE
    m=metrics(oos);order=['mean','country_mean','momentum','controls','full','no_fast','no_slow']
    fig,ax=plt.subplots(figsize=(9,4));ax.bar(order,[m[k]['rmse_pp'] for k in order]);ax.set(title='2018–2023 OOS RMSE: annual share change',ylabel='RMSE (percentage points)');ax.tick_params(axis='x',rotation=20);ax.grid(axis='y',alpha=.2);finish('04_oos_rmse_comparison.png')
    # 5. yearly factor rank IC
    r=per_year_rank_ic(oos);fig,ax=plt.subplots(figsize=(8,4));ax.bar(r.year.astype(str),r.rank_ic);ax.axhline(0,color='black',lw=1)
    ax.set(title='Descriptive cross-country rank IC, charging score vs EV-share change',ylabel='Spearman rank correlation');ax.grid(axis='y',alpha=.2);finish('05_yearly_rank_ic.png')
    # 6. Placebo null
    fig,ax=plt.subplots(figsize=(8,4));ax.hist(null,bins=40,alpha=.85)
    observed=m['controls']['rmse_pp']-m['full']['rmse_pp'];ax.axvline(observed,color='black',ls='--',label=f'Observed {observed:.3f} pp')
    ax.set(title='1,000 within-year charging-feature shuffle placebos',xlabel='RMSE improvement: controls minus full (pp)',ylabel='Count');ax.legend();finish('06_permutation_null.png')
    # 7. country sensitivity
    z=country_leaveout(oos).sort_values('delta_rmse_control_minus_full')
    fig,ax=plt.subplots(figsize=(9,5));ax.barh(z.removed,z.delta_rmse_control_minus_full);ax.axvline(0,color='black',lw=1)
    ax.set(title='Leave-one-country-out OOS RMSE improvement',xlabel='Controls minus full (percentage points)');finish('07_leave_one_country_out.png')
    # 8. forecast error by year
    z=oos.copy();z['control_abs']=(z.controls-z.actual).abs();z['full_abs']=(z.full-z.actual).abs()
    q=z.groupby('year')[['control_abs','full_abs']].mean()
    fig,ax=plt.subplots(figsize=(9,4));q.plot(ax=ax,marker='o');ax.set(title='Mean absolute error by forecast year',ylabel='MAE (pp)');ax.grid(alpha=.2);finish('08_oos_mae_by_year.png')
    return paths

if __name__=='__main__':
    for f in create_all_figures():print(f)
