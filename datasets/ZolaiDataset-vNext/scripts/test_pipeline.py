import unittest
from baseline_inventory import normalize,folded,digest
from build_candidate import checks,source_group,Groups,split_for
class PipelineTests(unittest.TestCase):
 def row(self):return {'sentence_id':'TEST-FIXTURE','permission_status':'Approved','review_status':'approved','spelling_standard':'unknown','notes':'Source: https://example.org/article/?tracking=1; Published: 2026-01-01'}
 def test_normalization_preserves_case_and_diacritics(self):
  self.assertEqual(normalize('  A\tpa\u0301  hi. '),'A pá hi.');self.assertEqual(folded('A PÁ hi!'),'a pá hi')
 def test_contact_and_permission_quarantine(self):
  r=self.row();bad,_=checks(r,'Naupang te hi. Contact: fixture@example.org ding hi.');self.assertIn('possible_contact_or_sensitive_identifier',bad)
  r['permission_status']='Unknown';bad,_=checks(r,'Zolai ahih leh Zomi te minam pau leh lai ahi hi.');self.assertIn('permission_not_approved',bad)
 def test_corruption_and_html_quarantine(self):
  bad,_=checks(self.row(),'Zomi te minam pau \ufffd ahi hi. <script>alert(1)</script>');self.assertIn('corrupt_or_control_text',bad);self.assertIn('html_markup',bad)
 def test_article_group_ignores_tracking(self):
  a=source_group(self.row());r=self.row();r['notes']='Source: https://example.org/article/#section; Published: 2025-01-01';self.assertEqual(a,source_group(r))
 def test_duplicate_components_stay_in_same_split(self):
  g=Groups();g.union('article-b','article-a');g.union('article-c','article-b');self.assertEqual(len({split_for(g.find(x)) for x in ['article-a','article-b','article-c']}),1)
 def test_candidate_never_claims_native_review(self):
  _,flags=checks(self.row(),'Zolai ahih leh Zomi te minam pau leh lai ahi hi.');self.assertIn('independent_native_review_unknown',flags)
if __name__=='__main__':unittest.main()
