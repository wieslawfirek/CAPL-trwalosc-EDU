import unittest
import numpy as np
import pandas as pd
from scipy import stats
from capl_analysis.robust import robust,holm
from capl_analysis.data import load,wide,supplemental_sample
from capl_analysis.supplement import assoc
from pathlib import Path
import capl_analysis.supplement as sup

ROOT=Path(__file__).resolve().parents[1]
class StatisticsTests(unittest.TestCase):
    def test_holm_known_values(self):
        np.testing.assert_allclose(holm([.01,.04,.03]),[.03,.06,.06])
    def test_rank_slope_matches_spearman_with_ties(self):
        rng=np.random.default_rng(123);cl=np.repeat(np.arange(12),8);x=rng.integers(0,8,len(cl));y=x+rng.integers(-4,4,len(cl));rx=stats.zscore(stats.rankdata(x),ddof=1);ry=stats.zscore(stats.rankdata(y),ddof=1)
        f=robust(np.c_[np.ones(len(x)),rx],ry,cl)
        self.assertAlmostEqual(f['beta'][1],stats.spearmanr(x,y).statistic,12)
        self.assertGreater(f['inference'][1]['df'],0)
    def test_cr2_invariant_under_cluster_relabeling(self):
        rng=np.random.default_rng(34);cl=np.repeat(np.arange(8),12);x=np.c_[np.ones(len(cl)),rng.normal(size=len(cl))];y=x@np.array([2,3])+rng.normal(size=len(cl))
        a=robust(x,y,cl);b=robust(x,y,100-cl)
        np.testing.assert_allclose(a['cov'],b['cov'],rtol=1e-10)
    def test_example_schema_and_counts(self):
        d,a=load(ROOT/'examples/capl_synthetic_long.csv');self.assertEqual(a['students'],300);self.assertEqual(len(d),700);self.assertTrue((d[d.group=='GN'].time==3).all());self.assertEqual(len(wide(d)),300)
        self.assertEqual(supplemental_sample(d)[1],0)
    def test_csv_retains_distinct_floating_point_values(self):
        import tempfile
        d=pd.read_csv(ROOT/'examples/capl_synthetic_long.csv',float_precision='round_trip')
        d.loc[0,'PC']=20.;d.loc[1,'PC']=np.nextafter(20.,21.)
        for i in [0,1]:d.loc[i,'AR']=d.loc[i,['PC','DB','MC','KU']].sum()
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'example.csv';d.to_csv(p,index=False);z,_=load(p)
            self.assertNotEqual(z.loc[0,'PC'],z.loc[1,'PC'])
            self.assertEqual(z.loc[1,'PC'],np.nextafter(20.,21.))
    def test_within_class_offset_invariance(self):
        d,_=load(ROOT/'examples/capl_synthetic_long.csv');d=d[d.time==3].dropna(subset=['AR','EDU_Matematyka_wynik']).copy();sup.B=100;sup.rng=np.random.default_rng(42);a=assoc(d,'AR','EDU_Matematyka_wynik')
        shifts=d.class_id.astype('category').cat.codes*5.;d.AR+=shifts;d.EDU_Matematyka_wynik-=shifts;sup.rng=np.random.default_rng(42);b=assoc(d,'AR','EDU_Matematyka_wynik')
        self.assertAlmostEqual(a['r_within'],b['r_within'],12)
if __name__=='__main__':unittest.main()
