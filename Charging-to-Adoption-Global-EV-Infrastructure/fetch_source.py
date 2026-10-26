"""Optional online audit of the complete third-party mirror of IEA 2024 data.

Does not run in offline notebook. Never silently overwrites frozen research data.
"""
from pathlib import Path
import hashlib
import io
import urllib.request
import pandas as pd

URL='https://raw.githubusercontent.com/WRicd/IEA-Data-Project/main/data/raw/IEA-EV-Data-2024.csv'
COUNTRIES=('Belgium','Canada','China','Denmark','Finland','France','Germany','Italy',
           'Netherlands','Norway','Portugal','Spain','United Kingdom','USA','Korea','Japan')


def extract(source):
    d=pd.read_csv(io.BytesIO(source))
    d=d[(d.category=='Historical') & d.region.isin(COUNTRIES) & d.year.between(2011,2023)]
    def series(param,mode,powertrain,field):
        a=d[(d.parameter==param)&(d['mode']==mode)&(d.powertrain==powertrain)]
        assert not a.duplicated(['region','year']).any()
        return a[['region','year','value']].rename(columns={'value':field})
    s=series('EV sales share','Cars','EV','ev_sales_share_pct')
    f=series('EV charging points','EV','Publicly available fast','public_fast_points')
    l=series('EV charging points','EV','Publicly available slow','public_slow_points')
    panel=s.merge(f,on=['region','year']).merge(l,on=['region','year'])
    panel=panel.rename(columns={'region':'country'}).sort_values(['country','year']).reset_index(drop=True)
    assert len(panel)==180
    panel.ev_sales_share_pct=panel.ev_sales_share_pct.round(5)
    panel.public_fast_points=panel.public_fast_points.round(2)
    panel.public_slow_points=panel.public_slow_points.round(2)
    return panel


def main():
    raw=urllib.request.urlopen(URL,timeout=30).read()
    print('Upstream SHA256:',hashlib.sha256(raw).hexdigest())
    out=extract(raw)
    original=pd.read_csv(Path(__file__).parent/'data'/'iea_ev_2024_selected.csv')
    cols=list(out.columns)
    same=out[cols].equals(original[cols])
    print('Current mirror equals frozen selected extract:',same)
    if not same:
        diff=out.merge(original,on=['country','year'],suffixes=('_current','_frozen'))
        print('Current mirror differs; do not silently overwrite the frozen study.',len(diff),'matched rows')
    return same

if __name__=='__main__':main()
