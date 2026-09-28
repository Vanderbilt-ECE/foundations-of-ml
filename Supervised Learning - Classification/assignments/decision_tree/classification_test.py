import re

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score

data_path = "./mushroom/agaricus-lepiota.data"
names_path = "./mushroom/agaricus-lepiota.names"

with open(names_path) as names_file:
    names_file_text = names_file.read()

feature_names = re.findall(r"^[ \t]+\d+\.\s+([\w?-]+):", names_file_text, re.MULTILINE)
feature_names = [
    name.rstrip("?") for name in feature_names
]  # e.g. "bruises?" -> "bruises"

column_names = ["class"] + feature_names

mushrooms_df = pd.read_csv(data_path, header=None, names=column_names)

labels = mushrooms_df["class"].to_numpy()
features = mushrooms_df.drop(columns="class").to_numpy()


feature_encoder = OrdinalEncoder()
encoded_features = feature_encoder.fit_transform(features)

label_encoder = OrdinalEncoder()
encoded_labels = label_encoder.fit_transform(labels.reshape(-1, 1)).ravel()

X_train, X_test, y_train, y_test = train_test_split(
    encoded_features, encoded_labels, test_size=0.25, random_state=7
)

model = DecisionTreeClassifier(max_depth=None, random_state=7)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(accuracy)

print(export_text(model, feature_names=feature_names))
