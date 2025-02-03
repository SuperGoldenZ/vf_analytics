import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, brier_score_loss

from vf_ml import Data

data = Data.load_data()
x = Data.get_x_features(data)
y = (data["Winning Player Number"] == 2).astype(int)  # Player 2 win: 1, Player 1 win: 0

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    x, y, test_size=0.2, random_state=42
)

# Logistic regression model
model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
# model = LogisticRegression(max_iter=1000,  random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)  # Probabilities

# Evaluate performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
print("Classification Report:")
print(
    classification_report(
        y_test, y_pred, target_names=["Player 1 Wins", "Player 2 Wins"]
    )
)

# Brier score for probability calibration
brier = brier_score_loss(y_test, y_proba[:, 1])  # Lower is better
print(f"Brier Score Loss: {brier:.4f}")

# Save the model
import joblib

joblib.dump(model, "logistic_regression_round_win_probability_model.pkl")


# Test with new data
def test_data(p1health, p2health, time_remaining):
    new_data = Data.create_test_data_frame(p1health, p2health, time_remaining, 1, 1)
    proba = model.predict_proba(new_data)  # Predict probabilities for both classes
    win_prob_player2 = proba[:, 1]  # Probability that Player 2 wins
    win_prob_player1 = proba[:, 0]  # Probability that Player 1 wins

    print(f"\n{p1health} vs {p2health} - {time_remaining} seconds")
    print(
        f"Win probabilities p1 {win_prob_player1[:10]} p2 {win_prob_player2[:10]}",
    )


# Test cases
test_data(100, 100, 45)
test_data(100, 100, 44)
test_data(100, 5, 30)
test_data(50, 50, 30)
test_data(25, 25, 30)
test_data(10, 90, 30)
test_data(10, 90, 1)
test_data(50, 50, 1)

test_data(75, 40, 35)
test_data(75, 40, 30)
test_data(75, 40, 20)
test_data(75, 40, 10)
test_data(75, 40, 5)
test_data(75, 40, 1)
