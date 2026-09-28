"""A step-by-step k-nearest neighbors example using synthetic data."""

from time import perf_counter

import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


# 1. Generate a large, low-dimensional classification dataset.
# Change n_features to experiment with different numbers of features.
n_features = 2

blob_data = make_blobs(
    n_samples=20_000,
    n_features=n_features,
    centers=5,
    cluster_std=2.0,
    random_state=7,
    return_centers=False,
)
features = np.asarray(blob_data[0])
labels = np.asarray(blob_data[1])

print(f"Number of examples: {features.shape[0]}")
print(f"Number of features per example: {features.shape[1]}")
print(f"Number of classes: {len(np.unique(labels))}\n")

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

# 3. Choose k, the number of nearby training examples to use.
# With k=5, the five closest examples vote on the prediction.
k = 5

# 4. Fit and time a brute-force k-NN model.
# "brute" checks every training example for each test example.
brute_model = KNeighborsClassifier(
    n_neighbors=k,
    algorithm="brute",
    n_jobs=-1,
)

start_time = perf_counter()
brute_model.fit(X_train, y_train)
brute_predictions = brute_model.predict(X_test)
brute_elapsed_seconds = perf_counter() - start_time
brute_accuracy = accuracy_score(y_test, brute_predictions)

print(
    f"brute:     accuracy={brute_accuracy:.1%}, "
    f"time={brute_elapsed_seconds:.2f} seconds"
)

# 5. Fit and time a KD-tree k-NN model.
# A KD-tree divides the data by splitting along feature dimensions.
kd_tree_model = KNeighborsClassifier(
    n_neighbors=k,
    algorithm="kd_tree",
    n_jobs=-1,
)

start_time = perf_counter()
kd_tree_model.fit(X_train, y_train)
kd_tree_predictions = kd_tree_model.predict(X_test)
kd_tree_elapsed_seconds = perf_counter() - start_time
kd_tree_accuracy = accuracy_score(y_test, kd_tree_predictions)

print(
    f"kd_tree:   accuracy={kd_tree_accuracy:.1%}, "
    f"time={kd_tree_elapsed_seconds:.2f} seconds"
)

# 6. Fit and time a ball-tree k-NN model.
# A ball tree groups nearby examples into nested regions, or "balls."
ball_tree_model = KNeighborsClassifier(
    n_neighbors=k,
    algorithm="ball_tree",
    n_jobs=-1,
)

start_time = perf_counter()
ball_tree_model.fit(X_train, y_train)
ball_tree_predictions = ball_tree_model.predict(X_test)
ball_tree_elapsed_seconds = perf_counter() - start_time
ball_tree_accuracy = accuracy_score(y_test, ball_tree_predictions)

print(
    f"ball_tree: accuracy={ball_tree_accuracy:.1%}, "
    f"time={ball_tree_elapsed_seconds:.2f} seconds"
)

# 7. Predict one new example with the KD-tree model.
new_example = np.zeros((1, n_features))
new_prediction = kd_tree_model.predict(new_example)[0]

print(f"\nNew example: {new_example[0]}")
print(f"Predicted class: {new_prediction}")
