"""Class for processing VF data for machine learning"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder

class Data:
    """Methods for processing VF data for machine learning"""

    @staticmethod
    def encode(data):
        """Encode categorical data"""
        label_encoder = LabelEncoder()
        data["Stage_encoded"] = label_encoder.fit_transform(data["Stage"])
        return data

    @staticmethod
    def load_data(filename="vf_match_data.csv"):
        """Load and pre-process the data"""
        data = pd.read_csv(filename)
        data = data[data["Time Remaining When Round Ended"] != "NA"]
        data = data.dropna(subset=["P1 Health"])
        data = data.dropna(subset=["P2 Health"])
        data = data.dropna(subset=["Time Remaining When Round Ended"])
        data = data.dropna(subset=["Player 1 Rank"])
        data = data.dropna(subset=["Player 2 Rank"])

        data["health_diff"] = data["P1 Health"] - data["P2 Health"]
        data["rank_diff"] = data["Player 1 Rank"] - data["Player 2 Rank"]
        data["health_time_interaction"] = data["health_diff"] * (
            45 - data["Time Remaining When Round Ended"]
        )
        data = Data.encode(data)
        return data

    @staticmethod
    def get_x_features(data):
        """Retruns x features of the dataset"""
        return data[
        [
            "P1 Health",
            "P2 Health",
            "health_diff",
            "Time Remaining When Round Ended",        
            "Player 1 Rank",
            "Player 2 Rank",
            "rank_diff",
            "P1 Rounds Won So Far",
            "P2 Rounds Won So Far",
            "Stage_encoded",
            "health_time_interaction",
        ]
    ]

    @staticmethod
    def get_linear_features():
        """Return linear features"""
        return ["P1 Health", "P2 Health", "health_diff", "Time Remaining When Round Ended", "rank_diff", "health_time_interaction"]

    @staticmethod
    def get_nonlinear_features():
        """Return nonlinear features"""
        return ["Player 1 Rank", "Player 2 Rank", "P1 Rounds Won So Far", "P2 Rounds Won So Far"]

    @staticmethod
    def create_test_data_frame(p1health, p2health, time_remaining, p1rank, p2rank, p1rounds_won_so_far = 0, p2_rounds_won_so_far = 0):
        """For creating a test frame"""
        new_data = pd.DataFrame(
            {
                "P1 Health": [p1health],
                "P2 Health": [p2health],
                "health_diff": [p1health - p2health],
                "Time Remaining When Round Ended": [time_remaining],
                "Stage": ["Octagon"],
                "Player 1 Rank": [p1rank],
                "Player 2 Rank": [p2rank],
                "rank_diff": [0],
                "P1 Rounds Won So Far": [p1rounds_won_so_far],
                "P2 Rounds Won So Far": [p2_rounds_won_so_far],                        
            }
        )

        new_data = Data.encode(new_data)
        del new_data["Stage"]

        new_data["health_time_interaction"] = [
            (p1health - p2health) * (45 - time_remaining)
        ]

        return new_data