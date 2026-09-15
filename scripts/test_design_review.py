"""Meaningful regression checks for occupancy, evidence gating and stale geometry."""
import copy
import unittest
from unittest.mock import patch
import design_review as review
import projection


class ReviewTests(unittest.TestCase):
    def test_scenarios_do_not_double_count_people(self):
        result=review.ventilation()
        totals={}
        for row in result['scenarios']:
            totals[row['scenario']]=totals.get(row['scenario'],0)+row['required_m3h']
        self.assertEqual(totals,{'daily':90,'night':90,'guest_night':150,'reading':90})
        self.assertAlmostEqual(result['geometric_area_total_m2'],122.1213,places=4)
        loads=[r for r in result['winter_sensitivity'] if r['flow_m3h']==60 and r['outdoor_c']==-10 and r['assumed_sensible_efficiency']==0]
        self.assertEqual(loads[0]['sensible_load_w'],603)

    def test_marketing_flow_cannot_pass_closed_bedroom(self):
        result=review.ventilation()
        rows=[r for r in result['device_comparisons'] if r['scenario']=='night' and r['room']=='Bedroom_A']
        p7=next(r for r in rows if r['device']=='TCL_P7')
        ultra=next(r for r in rows if r['device']=='TCL_ULTRA')
        self.assertEqual(p7['advertised_minimum_deficit_m3h'],30)
        self.assertEqual(p7['conclusion'],'不足')
        self.assertEqual(ultra['conclusion'],'条件不足')
        self.assertIsNone(ultra['night_deficit_m3h'])

    def test_known_night_shortfall_is_not_merely_unknown(self):
        original=review.load
        def modified(name):
            result=copy.deepcopy(original(name))
            if name=='ventilation.json':
                result['devices'][2]['night_outdoor_air_m3h']=20
            return result
        with patch.object(review,'load',side_effect=modified):
            rows=review.ventilation()['device_comparisons']
        self.assertTrue(all(r['conclusion']=='不足' for r in rows if r['device']=='TCL_ULTRA'))

    def test_frame_sensitivity_keeps_conflicts(self):
        result=review.dimension_review()
        child=next(r for r in result['beds'] if r['bed']=='bedB' and r['assumed_each_side_overhang_mm']==100)
        self.assertEqual(child['child_bed_foot_to_stowed_chair_mm'],453)
        master=next(r for r in result['beds'] if r['bed']=='bedA' and r['assumed_each_side_overhang_mm']==50)
        self.assertIn('A_bedside_west',master['fixed_hits'])
        laundry=next(r for r in result['robot_candidates'] if r['candidate']=='robot_laundry')
        self.assertIn('laundry_loading',laundry['operation_time_overlaps'])

    def test_stale_projection_is_rejected(self):
        with patch.object(projection,'source_hashes',return_value={'changed':'different'}):
            with self.assertRaisesRegex(RuntimeError,'过期'):
                projection.load_snapshot()


if __name__=='__main__':
    unittest.main()
