import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import numpy as np
import joblib
import cv2

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, brier_score_loss
from vf_ml.data import Data


class WinProbability:
    def __init__(self, process=True, version=1):
        self.round_model = None
        self.match_model = None
        self.version = version

        if process:
            self.round_model = joblib.load(
                f"logistic_regression_round_win_probability_model_v{version}.pkl"
            )
            self.match_model = joblib.load(
                f"logistic_regression_match_win_probability_model_v{version}.pkl"
            )

    def generate_win_prob_chart_with_single_line(
        self,
        round_number,
        stage,
        frame_data,
        p1rank,
        p2rank,
        frame_num=0,
        save_to_file=True,
        p1character="",
        p2character="",
        winner_player_number=None,
        p1rounds_won_so_far=0,
        p2rounds_won_so_far=0,
    ):
        last_time_digit = 45
        for frame in frame_data:
            (frame.win_prob_player1, frame.win_prob_player2) = self.get_win_probability(
                p1health=frame.p1info.health,
                p2health=frame.p2info.health,
                stage=stage,
                time_remaining=frame.time_seconds_remaining,
                p1rank=p1rank,
                p2rank=p2rank,
                p1rounds_won_so_far=p1rounds_won_so_far,
                p2rounds_won_so_far=p2rounds_won_so_far,
                p1drinks=frame.p1info.drinks,
                p2drinks=frame.p2info.drinks,
            )
            frame.elapsed_time = 45 - int(frame.time_seconds_remaining)
            last_time_digit = 45 - int(frame.time_seconds_remaining)

        # Extract time_remaining and win probabilities for Player 1 (used as win probability for the chart)
        time_remaining = np.array([frame.elapsed_time for frame in frame_data])
        win_prob = np.array(
            [frame.win_prob_player1 for frame in frame_data]
        )  # You can also use Player 2 here if needed

        # Create a figure with the desired size
        fig, ax = plt.subplots(figsize=(6, 0.8))

        # Plot the win probability line
        ax.plot(time_remaining, win_prob, "bo-", label="Win Probability", markersize=4)

        # Set the limits for the Y-axis (0 to 1 for win probability)
        ax.set_ylim(0, 1)

        # Customize Y-axis labels: top is 100% for Player 1, bottom is 100% for Player 2, and no label in the middle
        # va='center'
        # , ha='left'
        ax.set_yticks([0, 1])
        ax.set_yticklabels([f"P2\n{p2character}", f"P1\n{p1character}"], fontsize=16)

        if last_time_digit < 45:
            last_time_digit += 1

        # Set labels and title
        ax.set_title(f"Round {round_number} Win Probability", fontsize=20)

        if winner_player_number == 1:
            ax.plot(
                [last_time_digit], [1], "ro", markersize=12, label="Win!"
            )  # Red dot at the top
            ax.set_title(f"Round {round_number-1} Win Probability")
        elif winner_player_number == 2:

            ax.plot(
                [last_time_digit], [0.1], "ro", markersize=12, label="Win!"
            )  # Red dot at the bottom
            ax.set_title(f"Round {round_number-1} Win Probability")

        # Set the X-axis to represent time remaining, from 45 to 0
        ax.set_xlim(0, 45)
        ax.set_xticks(np.arange(45, -1, -5))  # From 45 to 0 with a step of -5 seconds
        ax.set_xticklabels(np.arange(45, -1, -5))  # Make sure labels match the ticks

        # Add a dotted horizontal line at the middle (50% win probability)
        ax.axhline(y=0.5, color="gray", linestyle="--", linewidth=1)
        ax.set_facecolor((1, 1, 1, 0.55))

        out_filename = "win_probability.png"
        plt.savefig(out_filename, bbox_inches="tight", facecolor=(1, 1, 1, 0.55))
        plt.close(fig)

    # Encode categorical data
    @staticmethod
    def encode(data):
        label_encoder = LabelEncoder()
        data["Stage_encoded"] = label_encoder.fit_transform(data["Stage"])
        data["p1character_encoded"] = label_encoder.fit_transform(data["p1character"])
        data["p2character_encoded"] = label_encoder.fit_transform(data["p2character"])
        return data

    def get_win_probability(
        self,
        p1health,
        p2health,
        stage,
        time_remaining,
        p1rank,
        p2rank,
        p1rounds_won_so_far,
        p2rounds_won_so_far,
        match_probability=False,
        p1drinks=0,
        p2drinks=0,
    ):
        if self.match_model is None or self.round_model is None:
            return (0.5, 0.5)

        if match_probability == False:
            return (0.5, 0.5)

        new_data = Data.create_test_data_frame(
            p1health=p1health,
            p2health=p2health,
            time_remaining=time_remaining,
            p1rank=p1rank,
            p2rank=p2rank,
            p1rounds_won_so_far=p1rounds_won_so_far,
            p2rounds_won_so_far=p2rounds_won_so_far,
            stage=stage,
            version=self.version,
            p1drinks=p1drinks,
            p2drinks=p2drinks,
        )

        if match_probability:
            proba = self.match_model.predict_proba(
                new_data
            )  # Predict probabilities for both classes
        else:
            proba = self.round_model.predict_proba(
                new_data
            )  # Predict probabilities for both classes

        win_prob_player2 = proba[:, 1]  # Probability that Player 2 wins
        win_prob_player1 = proba[:, 0]  # Probability that Player 1 wins
        return (win_prob_player1, win_prob_player2)

    def generate_match_win_prob_chart_with_single_line(
        self,
        round_number,
        stage,
        frame_data,
        p1rank,
        p2rank,
        frame_num=0,
        save_to_file=True,
        p1character="",
        p2character="",
        winner_player_number=None,
        p1rounds_won_so_far=0,
        p2rounds_won_so_far=0,
    ):
        last_time_digit = 45
        x = 0

        p1rounds_won_so_far = 0
        p2rounds_won_so_far = 0

        temp_frame_count = 0
        finished_round_frame_count = 0
        last_win_prob_player_1 = 0

        # Create a figure with the desired size
        fig, ax = plt.subplots(figsize=(6, 1.0))

        for frame in frame_data:
            (frame.win_prob_player1, frame.win_prob_player2) = self.get_win_probability(
                p1health=frame.p1info.health,
                p2health=frame.p2info.health,
                stage=stage,
                time_remaining=frame.time_seconds_remaining,
                p1rank=p1rank,
                p2rank=p2rank,
                p1rounds_won_so_far=p1rounds_won_so_far,
                p2rounds_won_so_far=p2rounds_won_so_far,
                match_probability=True,
                p1drinks=frame.p1info.drinks,
                p2drinks=frame.p2info.drinks,
            )
            temp_frame_count += 1

            if frame.winning_player_number == 1:
                p1rounds_won_so_far += 1
                finished_round_frame_count = temp_frame_count
                ax.plot(
                    [frame.id], [1], "o", color="#f12323", markersize=12, label="Win!"
                )  # Red dot at the top               i

            elif frame.winning_player_number == 2:
                p2rounds_won_so_far += 1
                finished_round_frame_count = temp_frame_count
                ax.plot(
                    [frame.id],
                    [0.05],
                    "o",
                    color="#2187ef",
                    markersize=12,
                    label="Win!",
                )  # Red dot at the bottom

            frame.id = x
            x += 0.20

            frame.elapsed_time = 45 - int(frame.time_seconds_remaining)
            last_time_digit = 45 - int(frame.time_seconds_remaining)
            last_win_prob_player_1 = frame.win_prob_player1

        # Extract time_remaining and win probabilities for Player 1 (used as win probability for the chart)
        id_x_axis = np.array([frame.id for frame in frame_data])
        win_prob = np.array(
            [frame.win_prob_player1 for frame in frame_data]
        )  # You can also use Player 2 here if needed

        # Plot the win probability line
        ax.plot(id_x_axis, win_prob, "bo-", label="Win Probability", markersize=4)

        # Set the limits for the Y-axis (0 to 1 for win probability)
        ax.set_ylim(0, 1)

        # Customize Y-axis labels: top is 100% for Player 1, bottom is 100% for Player 2, and no label in the middle
        # va='center'
        # , ha='left'
        ax.set_yticks([0, 1])
        ax.set_yticklabels(
            [f"{p2character}", f"{p1character}"], fontsize=15, fontweight="bold"
        )

        yticks = ax.get_yticklabels()
        yticks[0].set_va("bottom")  # Moves the P2 label higher
        yticks[1].set_va("top")  # Ensures P1 label stays aligned properly
        yticks[0].set_color("#2187ef")  # Example: P2 label in orange-red
        yticks[1].set_color("#f12323")  # Example: P1 label in blue

        if last_time_digit < 45:
            last_time_digit += 1

        # Set labels and title
        # ax.set_title(f"Match Win Probability")
        ax.set_title(f" ")

        # Set the X-axis to represent time remaining, from 45 to 0
        ax.set_xlim(0, 45 + (finished_round_frame_count / 4))
        ax.set_xticks(
            np.arange(45 + (finished_round_frame_count / 4), 0, 1)
        )  # From 45 to 0 with a step of -5 seconds
        ax.set_xticklabels(np.arange(5, 0, 1))  # Make sure labels match the ticks

        # Add a dotted horizontal line at the middle (50% win probability)
        ax.axhline(y=0.5, color="gray", linestyle="--", linewidth=1)
        ax.set_facecolor((1, 1, 1, 0.55))

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ax.text(
            xlim[1] - 1,  # Near the right edge, but inside the plot
            ylim[0] + 0.1,  # Same height as P2's tick label
            f"{int((1-last_win_prob_player_1)*100)}%",
            ha="right",  # Right-aligned
            va="bottom",
            fontsize=18,
            fontweight="bold",
            color="#2187ef",  # Match P2 color if needed
        )

        ax.text(
            xlim[1] - 1,  # Near the right edge, but inside the plot
            ylim[1] - 0.1,  # Same height as P1's tick label
            f"{int(last_win_prob_player_1*100)}%",
            ha="right",
            va="top",
            fontsize=18,
            fontweight="bold",
            color="#f12323",  # Match P1 color if needed
        )

        for frame in frame_data:
            if frame.last_frame_in_round:
                ax.axvline(x=frame.id, color="black", linestyle="--", linewidth=1)

        out_filename = "match_win_probability.png"
        plt.savefig(out_filename, bbox_inches="tight", facecolor=(1, 1, 1, 0.55))
        plt.close(fig)
        return out_filename
