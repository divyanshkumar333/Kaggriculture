import os
import json

class OpponentPosterior:
    def __init__(self):
        # We start with a uniform prior over the known meta families
        self.P = {
            "COW_RUSH": 0.5,
            "BERRY_FLYWHEEL": 0.5
        }
    
    def update(self, obs, opp_features):
        """
        Bayesian update of the opponent's strategy family using public features.
        """
        day = obs.get("day", 0)
        
        # We only update if we have meaningful divergence
        if day >= 4:
            opp_cows = opp_features.get("opp_cows", 0)
            opp_strawberries = opp_features.get("opp_strawberries", 0)
            opp_workers = opp_features.get("opp_total_workers", 1)
            
            # Likelihoods based on empirical meta rules
            # COW_RUSH aggressively buys cows > 2 by day 6.
            # BERRY_FLYWHEEL buys 0-2 cows, and scales workers > 6 by day 10.
            
            l_cow_rush = 0.5
            l_berry = 0.5
            
            if opp_cows >= 3:
                # Highly likely COW_RUSH
                l_cow_rush = 0.9
                l_berry = 0.1
            elif opp_cows <= 1 and day >= 8:
                # Highly likely BERRY
                l_cow_rush = 0.1
                l_berry = 0.9
                
            if opp_strawberries > 5:
                l_cow_rush = 0.05
                l_berry = 0.95
                
            if opp_workers >= 8 and opp_cows < 3:
                l_cow_rush = 0.01
                l_berry = 0.99
                
            # Update posterior
            unnorm_cow = self.P["COW_RUSH"] * l_cow_rush
            unnorm_berry = self.P["BERRY_FLYWHEEL"] * l_berry
            
            total = unnorm_cow + unnorm_berry
            if total > 0:
                self.P["COW_RUSH"] = unnorm_cow / total
                self.P["BERRY_FLYWHEEL"] = unnorm_berry / total
                
        return self.P

def get_best_counter_policy(posterior):
    """
    Given the posterior distribution, return the optimal policy.
    Based on the non-transitive matrix:
    V097 beats BERRY_FLYWHEEL
    V025-A beats V097
    BERRY_FLYWHEEL beats V025-A
    """
    
    # If the opponent is BERRY_FLYWHEEL, V097 is the known optimal counter (4-0)
    # If the opponent is COW_RUSH (V025-A), V025-A is the optimal counter (tie) 
    # Wait! If the opponent is COW_RUSH, V025-A ties V025-A (0.5 EV). V097 loses (0.0 EV). Flywheel wins (1.0 EV).
    # Ah! Flywheel beats V025-A! 
    # Therefore, the optimal counter to COW_RUSH is actually BERRY_FLYWHEEL.
    # The optimal counter to BERRY_FLYWHEEL is V097.
    
    ev_v025 = posterior["COW_RUSH"] * 0.5 + posterior["BERRY_FLYWHEEL"] * 0.0
    ev_v097 = posterior["COW_RUSH"] * 0.0 + posterior["BERRY_FLYWHEEL"] * 1.0
    ev_flywheel = posterior["COW_RUSH"] * 1.0 + posterior["BERRY_FLYWHEEL"] * 0.0
    
    # Select max EV
    best_ev = -1
    best_policy = "V025-A"
    
    if ev_v025 > best_ev:
        best_ev = ev_v025
        best_policy = "V025-A"
    if ev_v097 > best_ev:
        best_ev = ev_v097
        best_policy = "V097"
    if ev_flywheel > best_ev:
        best_ev = ev_flywheel
        best_policy = "BERRY_FLYWHEEL"
        
    return best_policy, self.P
