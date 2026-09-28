"""A small, step-by-step linear SVM example using a synthetic 3D dataset.

Run this file with:

    uv run svm/svm.py
"""

import numpy as np
import plotly.graph_objects as go
from sklearn.datasets import make_blobs
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


# 1. Generate two clusters that a single flat plane can separate.
# A large cluster_std relative to the distance between centers would make the
# clusters overlap, so the centers here are spaced well apart.
blob_data = make_blobs(
    n_samples=300,
    n_features=3,
    centers=[[-5, -5, -5], [5, 5, 5]],
    cluster_std=5,
    random_state=7,
    return_centers=False,
)
features = np.asarray(blob_data[0])
labels = np.asarray(blob_data[1])

print(f"Number of examples: {features.shape[0]}")
print(f"Class 0: {np.sum(labels == 0)}")
print(f"Class 1: {np.sum(labels == 1)}\n")


# 2. Visualize the data in 3D before fitting anything.
# Color and marker shape both encode the class, so the two groups are easy
# to tell apart even if colors are hard to distinguish.
class_0 = labels == 0
class_1 = labels == 1

figure = go.Figure()
figure.add_trace(
    go.Scatter3d(
        x=features[class_0, 0],
        y=features[class_0, 1],
        z=features[class_0, 2],
        mode="markers",
        name="Class 0",
        marker=dict(size=4, color="royalblue", symbol="circle"),
    )
)
figure.add_trace(
    go.Scatter3d(
        x=features[class_1, 0],
        y=features[class_1, 1],
        z=features[class_1, 2],
        mode="markers",
        name="Class 1",
        marker=dict(size=4, color="firebrick", symbol="diamond"),
    )
)
figure.update_layout(
    title="Synthetic Two-Cluster Dataset",
    scene=dict(
        xaxis_title="Feature 1",
        yaxis_title="Feature 2",
        zaxis_title="Feature 3",
    ),
)
figure.show()


# 3. Split the data into training data and testing data.
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


# 4. Scale the features so each measurement contributes fairly to the margin.
# SVMs are sensitive to feature scale because they rely on distances.
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)


# 5. Fit a simple linear SVM.
# A linear kernel draws a single flat decision boundary (a hyperplane) between
# the classes, with no kernel trick involved.
model = SVC(kernel="linear", C=1.0)
model.fit(X_train, y_train)


# 6. Make predictions for the test examples.
predictions = model.predict(X_test)


# 7. Compare predictions with the correct answers.
accuracy = accuracy_score(y_test, predictions)
print(f"Test accuracy: {accuracy:.1%}\n")
print("Confusion matrix (rows are actual, columns are predicted):")
print(confusion_matrix(y_test, predictions, labels=model.classes_))
print("\nClassification report:")
print(classification_report(y_test, predictions, labels=model.classes_))


# 8. Visualize the fitted hyperplane along with the (scaled) data.
# The SVM learned weights w and a bias b such that w . x + b = 0 on the
# hyperplane. Solving that equation for the third feature turns the plane
# into a surface we can draw over a grid of the first two features.
X_all = np.vstack([X_train, X_test])
y_all = np.concatenate([y_train, y_test])
class_0_scaled = y_all == 0
class_1_scaled = y_all == 1

weights = model.coef_[0]
bias = model.intercept_[0]

print("Weights: ", weights, " Bias: ", bias)

x_range = np.linspace(X_all[:, 0].min(), X_all[:, 0].max(), 10)
y_range = np.linspace(X_all[:, 1].min(), X_all[:, 1].max(), 10)
grid_x, grid_y = np.meshgrid(x_range, y_range)
grid_z = -(weights[0] * grid_x + weights[1] * grid_y + bias) / weights[2]

hyperplane_figure = go.Figure()
hyperplane_figure.add_trace(
    go.Scatter3d(
        x=X_all[class_0_scaled, 0],
        y=X_all[class_0_scaled, 1],
        z=X_all[class_0_scaled, 2],
        mode="markers",
        name="Class 0",
        marker=dict(size=4, color="royalblue", symbol="circle"),
    )
)
hyperplane_figure.add_trace(
    go.Scatter3d(
        x=X_all[class_1_scaled, 0],
        y=X_all[class_1_scaled, 1],
        z=X_all[class_1_scaled, 2],
        mode="markers",
        name="Class 1",
        marker=dict(size=4, color="firebrick", symbol="diamond"),
    )
)
hyperplane_figure.add_trace(
    go.Surface(
        x=grid_x,
        y=grid_y,
        z=grid_z,
        name="Decision boundary",
        opacity=0.5,
        showscale=False,
        colorscale=[[0, "lightgray"], [1, "lightgray"]],
    )
)
hyperplane_figure.update_layout(
    title="SVM Decision Boundary (scaled features)",
    scene=dict(
        xaxis_title="Feature 1 (scaled)",
        yaxis_title="Feature 2 (scaled)",
        zaxis_title="Feature 3 (scaled)",
    ),
)
hyperplane_figure.show()


# 9. Predict the class of one new example.
new_example = np.array([[4, 6, 5]])
new_example_scaled = scaler.transform(new_example)
new_prediction = model.predict(new_example_scaled)[0]

print(f"\nNew example: {new_example[0]}")
print(f"Predicted class: {new_prediction}")
