import unittest
import numpy as np
import pandas as pd
from capl_analysis.stroop import within

class WithinClassTests(unittest.TestCase):
    def test_class_shifts_do_not_change_paired_pearson(self):
        rng=np.random.default_rng(1);rows=[]
        for c in range(8):
            for i in range(6):
                x=rng.normal();y=.3*x+rng.normal()
                rows.append(dict(id=f'{c}_{i}',class_id=str(c),group='GN' if c>=4 else 'GE',x=x,y=y))
        d=pd.DataFrame(rows);r=within(d,'x','y',200,np.random.default_rng(2))
        shifted=d.copy()
        shifted.x += shifted.class_id.astype(int)*13
        shifted.y -= shifted.class_id.astype(int)*7
        s=within(shifted,'x','y',200,np.random.default_rng(2))
        for k in ['r','lo','hi','sim_lo','sim_hi']:self.assertAlmostEqual(r[k],s[k],places=12)
        self.assertLessEqual(r['sim_lo'],r['lo'])
        self.assertGreaterEqual(r['sim_hi'],r['hi'])

    def test_singletons_excluded_per_pair(self):
        rows=[]
        for c in range(4):
            for i in range(3):rows.append(dict(id=f'{c}_{i}',class_id=str(c),group='GE',x=i,y=i+c))
        rows.append(dict(id='single',class_id='S',group='GN',x=100,y=-100))
        d=pd.DataFrame(rows);r=within(d,'x','y',50,np.random.default_rng(2))
        self.assertEqual(r['n'],12);self.assertEqual(r['classes'],4);self.assertAlmostEqual(r['r'],1)
