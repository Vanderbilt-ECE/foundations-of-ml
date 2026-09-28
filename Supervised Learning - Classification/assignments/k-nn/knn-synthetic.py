import numpy as np
from sklearn.datasets import make_blobs
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

from time import perf_counter

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

X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.25, random_state=7, stratify=labels
)

k = 5

brute_model = KNeighborsClassifier(n_neighbors=k, algorithm="brute", n_jobs=1)
start_time = perf_counter()
brute_model.fit(X_train, y_train)
brute_predictions = brute_model.predict(X_test)
brute_elapsed_time = perf_counter() - start_time
brute_accuracy = accuracy_score(y_test, brute_predictions)


print(brute_elapsed_time)
print(brute_accuracy)


kdtree_model = KNeighborsClassifier(n_neighbors=k, algorithm="kd_tree", n_jobs=1)
start_time = perf_counter()
kdtree_model.fit(X_train, y_train)
kdtree_predictions = brute_model.predict(X_test)
kdtree_elapsed_time = perf_counter() - start_time
kdtree_accuracy = accuracy_score(y_test, brute_predictions)

print(kdtree_elapsed_time)
print(kdtree_accuracy)

balltree_model = KNeighborsClassifier(n_neighbors=k, algorithm="ball_tree", n_jobs=1)
start_time = perf_counter()
balltree_model.fit(X_train, y_train)
balltree_predictions = brute_model.predict(X_test)
balltree_elapsed_time = perf_counter() - start_time
balltree_accuracy = accuracy_score(y_test, brute_predictions)

print(balltree_elapsed_time)
print(balltree_accuracy)
