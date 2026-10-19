import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_analysis import load_data,make_panel,evaluate,score,block_ci

class TestStudy(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.df=load_data()
 def test_data(self):
  self.assertEqual(len(self.df),357)
  self.assertEqual(self.df.date.iloc[0].strftime('%Y-%m'),'1997-01')
  self.assertEqual(self.df.date.iloc[-1].strftime('%Y-%m'),'2026-09')
 def test_lag_and_target(self):
  import numpy as np
  p=make_panel(self.df,3)
  t=int(p.t.iloc[0]); g=self.df.henry_hub_usd_mmbtu; w=self.df.wti_usd_barrel
  self.assertEqual(t,13)
  self.assertAlmostEqual(p.oil_gas_spread.iloc[0],np.log(w.iloc[t-1]/(6*g.iloc[t-1])))
  self.assertAlmostEqual(p.y.iloc[0],100*np.log(g.iloc[t+3]/g.iloc[t-1]))
 def test_purged_oos(self):
  p=evaluate(self.df,3)
  self.assertEqual(len(p),242)
  self.assertEqual(p.date.iloc[0],'2006-05')
  self.assertEqual(p.date.iloc[-1],'2026-06')
  self.assertEqual(p.n_train.iloc[0],96)
  self.assertTrue((p.n_train.diff().dropna()==1).all())
 def test_metrics(self):
  p=evaluate(self.df,3); s=score(p)
  self.assertAlmostEqual(s['control']['rmse'],30.9113664007,places=4)
  self.assertAlmostEqual(s['full']['rmse'],32.7068742129,places=4)
  self.assertGreater(s['full']['rmse'],s['control']['rmse'])
 def test_placebo(self):
  self.assertEqual(len(evaluate(self.df,3,12)),230)
 def test_bootstrap(self):
  ci=block_ci(evaluate(self.df,3),replications=20,seed=3)
  self.assertLess(ci[0],ci[1])

if __name__=='__main__': unittest.main()
