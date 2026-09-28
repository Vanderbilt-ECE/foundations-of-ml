from pathlib import Path
import pandas as pd

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB


dataset_file = Path(__file__).parent / "SMSSpamCollection"

data = pd.read_csv(dataset_file, sep="\t", header=None, names=["labels", "messages"])

messages = data["messages"].to_numpy()
labels = data["labels"].to_numpy()

messages_train, messages_test, y_train, y_test = train_test_split(
    messages, labels, test_size=0.25, random_state=7, stratify=labels
)

vectorizer = CountVectorizer(binary=True, lowercase=True, stop_words="english")
X_train = vectorizer.fit_transform(messages_train)
X_test = vectorizer.transform(messages_test)

vocabulary = vectorizer.get_feature_names_out()

model = BernoulliNB(alpha=0.1)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

new_messages = np.array(
    ["You won a free prize! Click to claim!", "where do you want to go for dinner?"]
)

new_features = vectorizer.transform(new_messages)
new_predictions = model.predict(new_features)

print(new_predictions)
