"""A small, step-by-step k-nearest neighbors example using the Iris dataset."""

import numpy as np
from typing import cast

from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler


# 1. Load the Iris dataset.
# The features are flower measurements. The target is the flower species.
iris = cast(dict[str, np.ndarray], load_iris(return_X_y=False))
features = iris["data"]
labels = iris["target"]
target_names = iris["target_names"]

print(f"Number of flowers: {features.shape[0]}")
print(f"Number of features per flower: {features.shape[1]}")
print(f"Flower species: {target_names}\n")

# 2. Split the data into training data and testing data.
# The model learns from the training data and is evaluated on unseen test data.
X_train, X_test, y_train, y_test = train_test_split(
    features,
    labels,
    test_size=0.25,
    random_state=7,
    stratify=labels,
)

print(f"Training examples: {len(X_train)}")
print(f"Testing examples: {len(X_test)}\n")

# 3. Scale the features so each measurement contributes fairly to distance.
# k-NN uses distance, so a feature with larger numbers could otherwise dominate.
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_test = scaler.transform(X_test)

# 4. Choose k, the number of nearby training examples to use.
# With k=5, the five closest flowers vote on the prediction.
k = 5
model = KNeighborsClassifier(n_neighbors=k)

# 5. Fit the model.
# k-NN mainly remembers the scaled training examples instead of learning weights.
model.fit(X_train, y_train)

# 6. Make predictions for the test examples.
predictions = model.predict(X_test)

# 7. Compare predictions with the correct answers.
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy with k={k}: {accuracy:.1%}")

# 8. Predict the species of one new flower.
# The measurements are: sepal length, sepal width, petal length, petal width.
new_flower = np.array([[5.1, 3.5, 1.4, 0.2]])
# new_flower_scaled = scaler.transform(new_flower)
# new_prediction = model.predict(new_flower_scaled)[0]
new_prediction = model.predict(new_flower)[0]

print(f"\nNew flower measurements: {new_flower[0]}")
print(f"Predicted species: {target_names[new_prediction]}")
