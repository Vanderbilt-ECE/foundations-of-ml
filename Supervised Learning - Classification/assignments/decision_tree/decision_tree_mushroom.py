"""
Decision Tree Classifier Example: Predicting Mushroom Edibility

This script trains a decision tree on the UCI Mushroom dataset to predict
whether a mushroom is edible (e) or poisonous (p) based on its physical
characteristics (cap shape, odor, color, etc).

The point of this example is to show the basic sklearn workflow:
    1. Load data
    2. Encode categorical features as numbers (trees can't use text directly)
    3. Split into train/test sets
    4. Fit a DecisionTreeClassifier
    5. Evaluate accuracy
    6. Inspect the tree's decision rules
"""

import re

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score

# ---------------------------------------------------------------------------
# 1. Load the data
# ---------------------------------------------------------------------------
# The dataset has no header row, so we pull the column names from the
# accompanying .names file instead of typing them out by hand. In that
# file, each feature is listed on its own indented, numbered line, e.g.
# "     5. odor:      almond=a,anise=l,...", so we can extract the name
# before the colon with a regex.
data_path = "mushroom/agaricus-lepiota.data"
names_path = "mushroom/agaricus-lepiota.names"

with open(names_path) as names_file:
    names_file_text = names_file.read()

feature_names = re.findall(r"^[ \t]+\d+\.\s+([\w?-]+):", names_file_text, re.MULTILINE)
feature_names = [
    name.rstrip("?") for name in feature_names
]  # e.g. "bruises?" -> "bruises"

# The first column in the .data file is the class label ("e" or "p"),
# which isn't part of the numbered feature list above, so we prepend it.
column_names = ["class"] + feature_names

mushrooms_df = pd.read_csv(data_path, header=None, names=column_names)

print("Preview of the mushroom dataset:")
print(mushrooms_df.head())

# Split the label column from the feature columns.
labels = mushrooms_df["class"].to_numpy()
features = mushrooms_df.drop(columns="class").to_numpy()

# ---------------------------------------------------------------------------
# 2. Encode categorical values as numbers
# ---------------------------------------------------------------------------
# scikit-learn's tree models need numeric input, so we convert each
# categorical feature value (e.g. "x", "s", "n") into an integer code.
# OrdinalEncoder does this column by column, fitting on the feature matrix.
feature_encoder = OrdinalEncoder()
encoded_features = feature_encoder.fit_transform(features)

# Encode the labels too: "e" -> 0, "p" -> 1 (order is assigned alphabetically).
label_encoder = OrdinalEncoder()
encoded_labels = label_encoder.fit_transform(labels.reshape(-1, 1)).ravel()

# ---------------------------------------------------------------------------
# 3. Split into training and test sets
# ---------------------------------------------------------------------------
# We hold out 20% of the data to evaluate the model on mushrooms it has
# never seen during training.
X_train, X_test, y_train, y_test = train_test_split(
    encoded_features, encoded_labels, test_size=0.2, random_state=42
)

# ---------------------------------------------------------------------------
# 4. Train the decision tree
# ---------------------------------------------------------------------------
# max_depth limits how many questions the tree can ask before making a
# prediction. Keeping it small makes the printed tree easy to read.
model = DecisionTreeClassifier(max_depth=4, random_state=42)
model.fit(X_train, y_train)

# ---------------------------------------------------------------------------
# 5. Evaluate the model
# ---------------------------------------------------------------------------
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Test accuracy: {accuracy:.4f}")

# ---------------------------------------------------------------------------
# 6. Inspect the learned decision rules
# ---------------------------------------------------------------------------
# export_text prints the tree as a series of if/else questions, which is a
# great way to see exactly how the model is making its decisions.
# feature_names was already parsed from the .names file back in step 1.
print("\nLearned decision rules:")
print(export_text(model, feature_names=feature_names))
