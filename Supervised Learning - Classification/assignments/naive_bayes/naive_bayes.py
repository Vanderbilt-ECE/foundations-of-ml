"""A small, step-by-step Bernoulli Naive Bayes spam classifier.

Run this file with:

    uv run naive_bayes/naive_bayes.py

The SMS Spam Collection file should be saved next to this script.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB


# 1. Load the tab-separated dataset from the same folder as this script.
dataset_file = Path(__file__).parent / "SMSSpamCollection"
data = pd.read_csv(
    dataset_file,
    sep="\t",
    header=None,
    names=["label", "message"],
)

messages = data["message"].to_numpy()
labels = data["label"].to_numpy()

print(f"Loaded {len(messages)} messages.")
print(f"Ham messages:  {np.sum(labels == 'ham')}")
print(f"Spam messages: {np.sum(labels == 'spam')}\n")


# 3. Split the messages before learning the vocabulary.
# The test messages must remain unseen while the model learns.
messages_train, messages_test, y_train, y_test = train_test_split(
    messages,
    labels,
    test_size=0.25,
    random_state=7,
    stratify=labels,
)


# 4. Turn each message into binary word features.
# A 1 means the word appears at least once; a 0 means it does not appear.
vectorizer = CountVectorizer(binary=True, lowercase=True, stop_words="english")
X_train = vectorizer.fit_transform(messages_train)
X_test = vectorizer.transform(messages_test)
vocabulary = vectorizer.get_feature_names_out()

print(f"Training messages: {X_train.shape[0]}")
print(f"Testing messages:  {X_test.shape[0]}")
print(f"Vocabulary size:   {X_train.shape[1]}\n")


# 5. Fit Bernoulli Naive Bayes.
# BernoulliNB is appropriate because each feature records whether a word
# appears, rather than how many times it appears.
model = BernoulliNB(alpha=1.0)
model.fit(X_train, y_train)


# 6. Predict the labels of messages the model has not seen.
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Test accuracy: {accuracy:.1%}\n")
print("Confusion matrix (rows are actual, columns are predicted):")
print(confusion_matrix(y_test, predictions, labels=model.classes_))
print("\nClassification report:")
print(classification_report(y_test, predictions, labels=model.classes_))


# 7. Try the finished classifier on a few new messages.
new_messages = np.array(
    [
        "Congratulations! You have won a free prize. Text WIN to claim it.",
        "Are we still meeting for lunch today?",
    ]
)
new_features = vectorizer.transform(new_messages)
new_predictions = model.predict(new_features)

print("Example predictions:")
for message, prediction in zip(new_messages, new_predictions):
    print(f"  {prediction:>4} | {message}")
