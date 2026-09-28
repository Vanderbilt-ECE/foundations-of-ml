"""A small, step-by-step k-nearest neighbors example using MNIST."""

import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


# 1. Load the MNIST handwriting dataset.
# Each example is a handwritten digit represented by 784 pixel features.
# We use a subset so this simple k-NN example runs in a reasonable amount of time.
features, labels = fetch_openml(
    "mnist_784",
    version=1,
    as_frame=False,
    parser="liac-arff",
    return_X_y=True,
)

# MNIST labels are returned as strings, so convert them to integers.
features = np.asarray(features)
labels = np.asarray(labels)
features = features[:5_000]
labels = labels[:5_000]
labels = labels.astype(int)

print(f"Number of images: {features.shape[0]}")
print(f"Pixels per image: {features.shape[1]}")
print("Possible digits: 0 through 9\n")

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

# 3. Visualize a few input images.
# Each image starts as 784 numbers, so reshape each one into a 28-by-28 grid.
# first_row = np.hstack([X_train[index].reshape(28, 28) for index in range(3)])
# second_row = np.hstack([X_train[index].reshape(28, 28) for index in range(3, 6)])
# third_row = np.hstack([X_train[index].reshape(28, 28) for index in range(6, 9)])
# stacked_images = np.vstack([first_row, second_row, third_row])
stacked_images = np.hstack([X_train[index].reshape(28, 28) for index in range(10)])

print(f"Labels for the displayed images: {y_train[:10]}\n")

plt.imshow(stacked_images, cmap="gray")
plt.axis("off")
plt.show()

# 4. Scale the pixel values to the range 0 to 1.
# k-NN uses distance, so keeping the feature values on a small common scale helps.
X_train = np.asarray(X_train, dtype=np.float32) / 255.0
X_test = np.asarray(X_test, dtype=np.float32) / 255.0

# 5. Choose k, the number of nearby training examples to use.
# With k=3, the three closest handwritten digits vote on the prediction.
k = 3

# 6. Fit a brute-force k-NN model.
# "brute" checks every training example for each test example.
model = KNeighborsClassifier(
    n_neighbors=k,
    algorithm="brute",
    n_jobs=-1,
)

model.fit(X_train, y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(f"Accuracy with k={k}: {accuracy:.1%}")

# 7. Predict one handwritten digit.
# This image came from the test set, so we can compare the prediction with its label.
one_image = X_test[0:1]
one_prediction = model.predict(one_image)[0]
correct_answer = y_test[0]

print(f"\nPredicted digit: {one_prediction}")
print(f"Correct digit: {correct_answer}")
