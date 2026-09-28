import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

features, labels = fetch_openml(
    "mnist_784", version=1, as_frame=False, parser="liac-arff", return_X_y=True
)

features = np.asarray(features)
labels = np.asarray(labels)

features = features[:5000]
labels = labels[:5000]

X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.25, random_state=7, stratify=labels
)

# stacked_images = np.hstack([X_train[index].reshape(28, 28) for index in range(10)])
# plt.imshow(stacked_images, cmap="gray")
# plt.axis("off")
# plt.show()
#

X_train = np.asarray(X_train, dtype=np.float32) / 255.0
X_test = np.asarray(X_test, dtype=np.float32) / 255.0

model = KNeighborsClassifier(n_neighbors=10, algorithm="brute", n_jobs=-1)

model.fit(X_train, y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print(accuracy)

first_image = X_test[0:1]
first_label = y_test[0:1]

print(model.predict(first_image))
print(first_label)
