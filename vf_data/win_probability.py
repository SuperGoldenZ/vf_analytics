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

class WinProbability:
    def __init__(self):
        self.model = joblib.load('logistic_regression_round_win_probability_model.pkl')

    def generate_win_prob_chart_with_single_line(self, round_number, stage, frame_data, frame_num=0, save_to_file = True):
        for frame in frame_data:
            (frame.win_prob_player1, frame.win_prob_player2) = self.get_win_probability(p1health=frame.p1info.health, p2health=frame.p2info.health, stage=stage,time_remaining=frame.time_seconds_remaining)
            frame.elapsed_time = 45-int(frame.time_seconds_remaining)

        # Extract time_remaining and win probabilities for Player 1 (used as win probability for the chart)        
        time_remaining = np.array([frame.elapsed_time for frame in frame_data])
        win_prob = np.array([frame.win_prob_player1 for frame in frame_data])  # You can also use Player 2 here if needed

        # Create a figure with the desired size
        fig, ax = plt.subplots(figsize=(6, 0.75))
        
        # Plot the win probability line
        ax.plot(time_remaining, win_prob, 'bo-', label="Win Probability", markersize=3)
        
        # Set the limits for the Y-axis (0 to 1 for win probability)
        ax.set_ylim(0, 1)
        
        # Customize Y-axis labels: top is 100% for Player 1, bottom is 100% for Player 2, and no label in the middle
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Player 2', 'Player 1'], fontsize=12)
        
        # Set the X-axis to represent time remaining, from 45 to 0
        ax.set_xlim(0, 45)
        ax.set_xticks(np.arange(45, -1, -5))  # From 45 to 0 with a step of -5 seconds
        ax.set_xticklabels(np.arange(45, -1, -5))  # Make sure labels match the ticks
        
        # Set labels and title
        #ax.set_xlabel('Elapsed Time (seconds)')
        #ax.set_ylabel('Win Probability')
        ax.set_title('Win Probability Over Time')
        
        # Add a dotted horizontal line at the middle (50% win probability)
        ax.axhline(y=0.5, color='gray', linestyle='--', linewidth=1)

        # Optionally: Adding text labels for the current probability at the last frame
        #ax.text(time_remaining[-1], win_prob[-1] + 0.05, f"{float(win_prob[-1])*100:.2f}%", ha='center')

        # Add a legend
        #ax.legend(loc='upper left')

        # Save the figure to a file (you can save to a location for OBS to pick up)
        
        #out_filename=f'r{round_number}_{frame_num}_win_probability_chart.png'
        out_filename = "win_probability.png"
        plt.savefig(out_filename, bbox_inches='tight')
        plt.close(fig)
        return out_filename


    # Encode categorical data
    @staticmethod
    def encode(data):
        label_encoder = LabelEncoder()
        data['Stage_encoded'] = label_encoder.fit_transform(data['Stage'])
        data['p1character_encoded'] = label_encoder.fit_transform(data['p1character'])
        data['p2character_encoded'] = label_encoder.fit_transform(data['p2character'])
        return data

    def get_win_probability(self, p1health, p2health, stage, time_remaining):
        new_data = pd.DataFrame({
            'p1health': [p1health],
            'p2health': [p2health],
            'health_diff': [p1health - p2health],
            'time_remaining': [time_remaining],
            'Stage': [stage],
            'p1character': ["Blaze"],
            'p2character': ["Blaze"],
        })
    
        new_data = WinProbability.encode(new_data)
        del new_data['p1character']
        del new_data['p2character']
        del new_data['p1character_encoded']
        del new_data['p2character_encoded']
        del new_data['Stage']    
        new_data['health_time_interaction'] = [(p1health - p2health) * (45 - int(time_remaining))]

        proba = self.model.predict_proba(new_data)  # Predict probabilities for both classes
        win_prob_player2 = proba[:, 1]  # Probability that Player 2 wins
        win_prob_player1 = proba[:, 0]  # Probability that Player 1 wins
        return (win_prob_player1, win_prob_player2)
    
