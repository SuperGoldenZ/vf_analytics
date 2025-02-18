"""Class for processing VF data for machine learning"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder


class Data:
    """Methods for processing VF data for machine learning"""

    @staticmethod
    def encode(data, version=2):
        """Encode categorical data"""
        label_encoder = LabelEncoder()
        data["Stage_encoded"] = label_encoder.fit_transform(data["Stage"])

        if version == 2:
            data["Player 1 Ringname Encoded"] = label_encoder.fit_transform(
                data["Player 1 Ringname"]
            )
            data["Player 2 Ringname Encoded"] = label_encoder.fit_transform(
                data["Player 2 Ringname"]
            )
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
        data = data.dropna(subset=["Shun.Drinks.1P"])
        data = data.dropna(subset=["Shun.Drinks.2P"])

        data["health_diff"] = data["P1 Health"] - data["P2 Health"]
        data["rank_diff"] = data["Player 1 Rank"] - data["Player 2 Rank"]

        if data["Time Remaining When Round Ended"] is None:
            data["Time Remaining When Round Ended"] = 45

        data["health_time_interaction"] = data["health_diff"] * (
            45 - data["Time Remaining When Round Ended"].astype(int)
        )
        data["p1_drinks_time"] = data["Shun.Drinks.1P"] * (
            data["Time Remaining When Round Ended"].astype(int)
        )
        data["p2_drinks_time"] = data["Shun.Drinks.2P"] * (
            data["Time Remaining When Round Ended"].astype(int)
        )

        data = Data.encode(data)
        return data

    @staticmethod
    def get_x_features(data, version=1):
        """Retruns x features of the dataset"""
        if version == 1:
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
        if version == 2:
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
                    "Shun.Drinks.1P",
                    "Shun.Drinks.2P",
                    "Stage_encoded",
                    "Player 1 Ringname Encoded",
                    "Player 2 Ringname Encoded",
                    "health_time_interaction",
                    "p1_drinks_time",
                    "p2_drinks_time",
                ]
            ]

    @staticmethod
    def get_linear_features():
        """Return linear features"""
        return [
            "P1 Health",
            "P2 Health",
            "health_diff",
            "Time Remaining When Round Ended",
            "rank_diff",
            "health_time_interaction",
        ]

    @staticmethod
    def get_nonlinear_features():
        """Return nonlinear features"""
        return [
            "Player 1 Rank",
            "Player 2 Rank",
            "P1 Rounds Won So Far",
            "P2 Rounds Won So Far",
        ]

    @staticmethod
    def create_test_data_frame(
        p1health,
        p2health,
        time_remaining,
        p1rank,
        p2rank,
        p1rounds_won_so_far=0,
        p2rounds_won_so_far=0,
        stage="Octagon",
        p1drinks=0,
        p2drinks=0,
        p1ringname="",
        p2ringname="",
        version=1,
    ):
        """For creating a test frame"""

        if time_remaining is None:
            time_remaining = 45

        if version == 1:
            new_data = pd.DataFrame(
                {
                    "P1 Health": [p1health],
                    "P2 Health": [p2health],
                    "health_diff": [p1health - p2health],
                    "Time Remaining When Round Ended": [time_remaining],
                    "Stage": [stage],
                    "Player 1 Rank": [p1rank],
                    "Player 2 Rank": [p2rank],
                    "rank_diff": [0],
                    "P1 Rounds Won So Far": [p1rounds_won_so_far],
                    "P2 Rounds Won So Far": [p2rounds_won_so_far],
                }
            )
        elif version == 2:
            new_data = pd.DataFrame(
                {
                    "P1 Health": [p1health],
                    "P2 Health": [p2health],
                    "health_diff": [p1health - p2health],
                    "Time Remaining When Round Ended": [time_remaining],
                    "Stage": [stage],
                    "Player 1 Rank": [p1rank],
                    "Player 2 Rank": [p2rank],
                    "rank_diff": [0],
                    "P1 Rounds Won So Far": [p1rounds_won_so_far],
                    "P2 Rounds Won So Far": [p2rounds_won_so_far],
                    "Shun.Drinks.1P": [p1drinks],
                    "Shun.Drinks.2P": [p2drinks],
                    "Player 1 Ringname": [p1ringname],
                    "Player 2 Ringname": [p2ringname],
                }
            )

        new_data = Data.encode(new_data, version)
        del new_data["Stage"]

        if version == 2:
            del new_data["Player 1 Ringname"]
            del new_data["Player 2 Ringname"]

        new_data["health_time_interaction"] = [
            (p1health - p2health) * (45 - int(time_remaining))
        ]

        if version == 2:
            new_data["p1_drinks_time"] = new_data["Shun.Drinks.1P"] * (
                new_data["Time Remaining When Round Ended"].astype(int)
            )
            new_data["p2_drinks_time"] = new_data["Shun.Drinks.2P"] * (
                new_data["Time Remaining When Round Ended"].astype(int)
            )

        return new_data
