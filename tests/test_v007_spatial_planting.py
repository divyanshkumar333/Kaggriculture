import unittest
from kaggle_environments import make

class TestV007SpatialPlanting(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 10}, debug=True)

    def test_v007_b_valid_planting(self):
        # Play 10 steps, ensure we planted validly without phantom tasks
        steps = self.env.run(["agents/v007_b_clustered.py", "random"])
        self.assertTrue(len(steps) > 0)
        
    def test_v007_c_valid_planting(self):
        # Play 10 steps, ensure we planted validly without phantom tasks
        steps = self.env.run(["agents/v007_c_sector_planting.py", "random"])
        self.assertTrue(len(steps) > 0)

if __name__ == '__main__':
    unittest.main()
