"""
Unit tests for the rule-based scoring logic
"""

import unittest
from services.rules import calculate_rule_score

class TestRuleScoring(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_offer = {
            "name": "AI Outreach Automation",
            "value_props": ["24/7 outreach", "6x more meetings"],
            "ideal_use_cases": ["B2B SaaS mid-market"]
        }
    
    def test_decision_maker_role_scoring(self):
        """Test scoring for decision maker roles"""
        lead = {
            "name": "John Doe",
            "role": "CEO",
            "company": "TestCorp",
            "industry": "SaaS",
            "location": "San Francisco",
            "linkedin_bio": "CEO at TestCorp"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 20 (role) + 20 (industry match) + 10 (complete data) = 50
        self.assertEqual(score, 50)
    
    def test_influencer_role_scoring(self):
        """Test scoring for influencer roles"""
        lead = {
            "name": "Jane Smith",
            "role": "Marketing Manager",
            "company": "TestCorp",
            "industry": "Technology",
            "location": "New York",
            "linkedin_bio": "Marketing Manager at TestCorp"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 10 (role) + 10 (adjacent industry) + 10 (complete data) = 30
        self.assertEqual(score, 30)
    
    def test_no_role_match_scoring(self):
        """Test scoring for non-matching roles"""
        lead = {
            "name": "Bob Johnson",
            "role": "Intern",
            "company": "TestCorp",
            "industry": "Retail",
            "location": "Chicago",
            "linkedin_bio": "Intern at TestCorp"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 0 (role) + 0 (industry) + 10 (complete data) = 10
        self.assertEqual(score, 10)
    
    def test_incomplete_data_scoring(self):
        """Test scoring with incomplete data"""
        lead = {
            "name": "Alice Brown",
            "role": "Head of Growth",
            "company": "TestCorp",
            "industry": "B2B SaaS",
            "location": "",  # Missing location
            "linkedin_bio": "Growth leader"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 20 (role) + 20 (industry match) + 0 (incomplete data) = 40
        self.assertEqual(score, 40)
    
    def test_exact_icp_match(self):
        """Test exact ICP matching"""
        lead = {
            "name": "Charlie Wilson",
            "role": "Director of Sales",
            "company": "SaaS Company",
            "industry": "B2B SaaS mid-market",
            "location": "Austin",
            "linkedin_bio": "Sales director"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 20 (role) + 20 (exact ICP match) + 10 (complete data) = 50
        self.assertEqual(score, 50)
    
    def test_adjacent_industry_match(self):
        """Test adjacent industry matching"""
        lead = {
            "name": "Diana Lee",
            "role": "VP Engineering",
            "company": "TechCorp",
            "industry": "Software",
            "location": "Seattle",
            "linkedin_bio": "VP of Engineering"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        # Should get: 20 (role) + 10 (adjacent industry) + 10 (complete data) = 40
        self.assertEqual(score, 40)
    
    def test_max_score_limit(self):
        """Test that score doesn't exceed 50"""
        # This test ensures the max score cap works
        lead = {
            "name": "Max Score",
            "role": "Chief Executive Officer",
            "company": "Perfect Match Corp",
            "industry": "B2B SaaS mid-market technology software",
            "location": "Silicon Valley",
            "linkedin_bio": "CEO with perfect profile"
        }
        
        score = calculate_rule_score(lead, self.sample_offer)
        self.assertLessEqual(score, 50)
    
    def test_empty_lead_data(self):
        """Test scoring with empty lead data"""
        lead = {}
        score = calculate_rule_score(lead, self.sample_offer)
        self.assertEqual(score, 0)
    
    def test_empty_offer_data(self):
        """Test scoring with empty offer data"""
        lead = {
            "name": "Test User",
            "role": "CEO",
            "company": "TestCorp",
            "industry": "SaaS",
            "location": "San Francisco",
            "linkedin_bio": "CEO at TestCorp"
        }
        
        empty_offer = {}
        score = calculate_rule_score(lead, empty_offer)
        # Should get: 20 (role) + 10 (adjacent industry) + 10 (complete data) = 40
        self.assertEqual(score, 40)

if __name__ == "__main__":
    unittest.main()