import unittest
from kaggle_environments import make

class TestV008Clustering(unittest.TestCase):
    def setUp(self):
        self.env = make("kaggriculture", configuration={"episodeSteps": 10}, debug=True)

    def test_v008_a_control_valid(self):
        steps = self.env.run(["agents/v008_a_control.py", "random"])
        self.assertTrue(len(steps) > 0)
        
    def test_v008_b_adaptive_cluster_valid(self):
        steps = self.env.run(["agents/v008_b_adaptive_cluster.py", "random"])
        self.assertTrue(len(steps) > 0)
        
    def test_v008_c_task_density_valid(self):
        steps = self.env.run(["agents/v008_c_task_density.py", "random"])
        self.assertTrue(len(steps) > 0)
        
    def test_v008_d_dynamic_clusters_valid(self):
        steps = self.env.run(["agents/v008_d_dynamic_clusters.py", "random"])
        self.assertTrue(len(steps) > 0)

if __name__ == '__main__':
    unittest.main()
