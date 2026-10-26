"""Generate lightweight, deterministic SVG charts from computed study results."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from run_analysis import ROOT, read_data


def svg_line(filename,title,series,ylabel='value',width=720,height=280):
    pad=52
    series=[(str(label),np.asarray(vals,dtype=float)[::max(1,int(np.ceil(len(vals)/140)))]) for label,vals in series]
    n=max(len(v) for _,v in series)
    allv=np.concatenate([v[np.isfinite(v)] for _,v in series])
    lo=float(np.min(allv)); hi=float(np.max(allv)); spread=max(hi-lo,1e-5)
    lo-=spread*.08;hi+=spread*.08
    W=width-2*pad;H=height-2*pad
    esc=lambda s:str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         f'<text x="{pad}" y="23" font-family="sans-serif" font-size="16">{esc(title)}</text>',
         f'<text x="8" y="{pad}" font-family="sans-serif" font-size="10">{esc(ylabel)}</text>',
         f'<path d="M{pad} {pad}V{pad+H}H{pad+W}" fill="none" stroke="#555"/>']
    for j in range(5):
        y=pad+H*j/4
        value=hi-(hi-lo)*j/4
        svg.append(f'<path d="M{pad} {y:.1f}h{W}" stroke="#ddd" stroke-dasharray="3,3"/>')
        svg.append(f'<text x="{pad-7}" y="{y+4:.1f}" text-anchor="end" font-size="10" font-family="sans-serif">{value:.1f}</text>')
    colors=['#1d4ed8','#b45309','#15803d','#7c3aed']
    for k,(name,arr) in enumerate(series):
        pts=[]
        for i,val in enumerate(arr):
            if np.isfinite(val):pts.append(f'{pad+i*W/max(len(arr)-1,1):.1f},{pad+(hi-val)/(hi-lo)*H:.1f}')
        svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colors[k%len(colors)]}" stroke-width="1.7"/>')
        svg.append(f'<text x="{pad+120*k}" y="{height-8}" fill="{colors[k%len(colors)]}" font-size="11" font-family="sans-serif">{esc(name)}</text>')
    svg.append('</svg>')
    (ROOT/'figures'/filename).write_text(''.join(svg),encoding='utf-8')


def make():
    df=read_data()
    panel=pd.read_csv(ROOT/'data/derived_panel.csv',parse_dates=['origin']).set_index('origin')
    oos=pd.read_csv(ROOT/'results/oos_forecasts.csv',parse_dates=['origin']).set_index('origin')
    res=json.loads((ROOT/'results/metrics.json').read_text())
    svg_line('01_industry_levels.svg','Textile mills vs apparel/leather vs manufacturing',[(c,df[c].to_numpy()) for c in df.columns],'2017=100')
    svg_line('02_yoy_growth.svg','Lagged industry output growth',[('Textiles',panel.textile_yoy),('Apparel',panel.apparel_yoy),('Manufacturing',panel.manufacturing_yoy)],'12m log growth (pp)')
    svg_line('03_fixed_factor.svg','Fixed upstream textile relative-growth signal',[('Factor',panel.factor)],'tanh scale')
    svg_line('04_oos_predictions.svg','Purged OOS: observed apparel vs forecasts',[('Observed',oos.target),('Macro',oos.macro),('Augmented',oos.full)],'log growth (pp)')
    errors=(oos.macro-oos.target)**2-(oos.full-oos.target)**2
    svg_line('05_loss_difference.svg','Paired squared-loss differential (positive = full wins)',[('Macro minus full',errors)],'pp squared')
    placebo=np.loadtxt(ROOT/'results/block_placebo_1000.csv',delimiter=',',skiprows=1)
    boot=np.loadtxt(ROOT/'results/bootstrap_2000.csv',delimiter=',',skiprows=1)
    svg_line('06_placebo_sorted.svg','Exploratory block shuffle null (ordered)',[('Null delta',np.sort(placebo))],'RMSE delta (pp)')
    svg_line('07_bootstrap_sorted.svg','Block-bootstrap paired forecast delta (ordered)',[('Bootstrap',np.sort(boot))],'RMSE delta (pp)')
    exposure=pd.read_csv(ROOT/'results/exposure_1000.csv')
    svg_line('08_exposure_sorted.svg','Analyst-prior exposure perturbation (ordered)',[('Exposure delta',np.sort(exposure.delta_rmse))],'RMSE delta (pp)')
    print('Generated 8 deterministic diagnostic SVGs')

if __name__=='__main__':make()
