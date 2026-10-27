"""Transcription of FRED data/IPG3361T3S table as displayed 2026-10-27.
Values are fixed, four-decimal readings. See source_register.csv. Manual transcription
means this is NOT an independently machine-verified copy of the entire official table.
"""
from pathlib import Path
import pandas as pd
import io, zipfile
BASE=Path(__file__).resolve().parent
VALUES={
2010:'64.4182 62.2667 63.9419 63.8429 69.0966 68.5732 73.1780 70.1245 71.1676 71.8161 69.2953 68.8274',
2011:'70.1725 73.7902 76.4730 70.1350 71.2859 71.3130 73.3508 75.5292 75.6320 79.4416 77.6546 79.7104',
2012:'83.7854 82.9372 82.4738 83.8420 82.6774 83.8076 83.2791 81.5091 80.4040 81.5722 83.8754 86.8321',
2013:'84.5637 86.2965 87.8411 87.2297 87.8470 89.5653 84.0474 89.7311 91.5528 90.7073 92.8306 93.1043',
2014:'88.1996 94.3343 95.0483 94.3760 97.2173 97.7374 103.3595 98.1264 96.4387 95.6328 100.4149 99.5852',
2015:'99.2810 95.2407 99.9280 100.8207 104.4538 99.3223 108.3730 102.5238 102.2376 103.0499 100.4358 99.5180',
2016:'102.6787 101.7467 100.6808 102.4201 99.7072 103.7364 104.6827 103.3208 103.4791 103.8431 101.4300 102.3001',
2017:'101.6802 101.3894 98.5683 103.5520 102.0675 100.4789 95.5606 97.8734 99.0724 100.5710 99.0519 100.1347',
2018:'101.5601 104.5676 106.9308 106.8519 99.1038 104.9052 100.0558 104.1271 106.5389 104.7229 103.7371 109.2503',
2019:'100.4853 102.4920 101.6260 100.9370 102.4737 105.9848 102.7050 104.3913 99.5115 93.4023 104.2043 101.1041',
2020:'102.6564 107.8280 75.6491 20.5804 39.3778 85.2413 107.6752 104.7129 102.0821 101.1274 101.4780 103.2304',
2021:'102.3046 92.7865 94.0784 87.6949 90.4312 88.6696 92.4829 91.6833 85.4193 96.1387 100.0637 99.9036',
2022:'99.5854 96.4871 103.5475 104.9525 104.4660 104.5111 106.9355 107.8039 108.1690 111.1824 107.0427 107.0475',
2023:'107.2538 107.2628 104.7958 112.6380 113.6344 109.0854 114.3820 110.1186 109.5162 102.0659 109.5406 112.1376',
2024:'103.8409 109.7089 111.3560 109.2986 109.5921 111.1791 99.5614 108.0037 107.9567 104.1036 107.1703 103.5024',
2025:'97.1065 106.4851 106.2058 105.9218 110.4780 108.7926 107.4701 110.5213 108.4358 102.0345 100.4798 101.0674',
2026:'103.1764 107.3119 105.4990 108.6141 111.8464 112.1220 111.3156 110.8509 107.5781'
}
def make():
    rows=[]
    for y,s in VALUES.items():
        a=[float(v) for v in s.split()]
        assert len(a)==(9 if y==2026 else 12),(y,len(a))
        rows += [(f'{y}-{m:02d}-01',v) for m,v in enumerate(a,1)]
    auto=pd.DataFrame(rows,columns=['date','auto_ip'])
    inherited=BASE/'data'/'raw_manufacturing_prior_study_2026-10-26.csv'
    if inherited.exists():
        manufacturing=pd.read_csv(inherited)
    else:
        raise FileNotFoundError('Frozen inherited IPMAN input is required; see data/source_qa.md')
    merged=auto.merge(manufacturing,on='date',validate='one_to_one')
    assert len(merged)==201 and not merged.isna().any().any()
    assert abs(merged.loc[merged.date=='2020-04-01','auto_ip'].iloc[0]-20.5804)<1e-6
    merged.to_csv(BASE/'data'/'frozen_auto_manufacturing_2026-10-27.csv',index=False,float_format='%.4f')
    auto.to_csv(BASE/'data'/'raw_fred_ipg3361t3s_manual_2026-10-27.csv',index=False,float_format='%.4f')
    manufacturing.to_csv(BASE/'data'/'raw_manufacturing_prior_study_2026-10-26.csv',index=False,float_format='%.4f')
    print('frozen',len(merged),'rows',merged.date.min(),merged.date.max())
if __name__=='__main__':make()
