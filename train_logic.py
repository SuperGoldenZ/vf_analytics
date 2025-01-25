import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, brier_score_loss

# Encode categorical data
def encode(data):
    label_encoder = LabelEncoder()
    data['Stage_encoded'] = label_encoder.fit_transform(data['Stage'])
    data['p1character_encoded'] = label_encoder.fit_transform(data['p1character'])
    data['p2character_encoded'] = label_encoder.fit_transform(data['p2character'])
    return data

# Load and preprocess the data
data = pd.read_csv('140k.csv')
data = data[data['time_remaining'] != "NA"]
data = data.dropna(subset=['p1health'])
data = data.dropna(subset=['time_remaining'])

#print(data)

data['health_diff'] = data['p1health'] - data['p2health']
data['health_time_interaction'] = data['health_diff'] * (45 - data['time_remaining'])
data = encode(data)

# Define features and target
X = data[['p1health', 'p2health', 'health_diff', 'time_remaining', 'Stage_encoded', 'health_time_interaction']]
#print(X[X.isnull().any(axis=1)])

y = (data['round_winner'] == 2).astype(int)  # Player 2 win: 1, Player 1 win: 0

# Split into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Logistic regression model
model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)
#model = LogisticRegression(max_iter=1000,  random_state=42)
model.fit(X_train, y_train)

# Test the model
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)  # Probabilities

# Evaluate performance
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Player 1 Wins', 'Player 2 Wins']))

# Brier score for probability calibration
brier = brier_score_loss(y_test, y_proba[:, 1])  # Lower is better
print(f"Brier Score Loss: {brier:.4f}")

# Save the model
import joblib
joblib.dump(model, 'logistic_regression_round_win_probability_model.pkl')

# Test with new data
def test_data(p1health, p2health, time_remaining):
    new_data = pd.DataFrame({
        'p1health': [p1health],
        'p2health': [p2health],
        'health_diff': [p1health - p2health],
        'time_remaining': [time_remaining],
        'Stage': ["Octagon"],
        'p1character': ["Blaze"],
        'p2character': ["Blaze"],
    })
    
    new_data = encode(new_data)
    del new_data['p1character']
    del new_data['p2character']
    del new_data['p1character_encoded']
    del new_data['p2character_encoded']
    del new_data['Stage']
    
    new_data['health_time_interaction'] = [(p1health - p2health) * (45 - time_remaining)]
    
    proba = model.predict_proba(new_data)  # Predict probabilities for both classes
    win_prob_player2 = proba[:, 1]  # Probability that Player 2 wins
    win_prob_player1 = proba[:, 0]  # Probability that Player 1 wins
    
    print(f"\n{p1health} vs {p2health} - {time_remaining} seconds")
    print(f"Win probabilities p1 {win_prob_player1[:10]} p2 {win_prob_player2[:10]}", )

# Test cases
test_data(100,100,45)
test_data(100,100,44)
test_data(100,5,30)
test_data(50,50,30)
test_data(25,25,30)
test_data(10,90,30)
test_data(10,90,1)
test_data(50,50,1)

test_data(75,40,35)
test_data(75,40,30)
test_data(75,40,20)
test_data(75,40,10)
test_data(75,40,5)
test_data(75,40,1)