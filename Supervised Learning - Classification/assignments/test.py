import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression


rng = np.random.default_rng(7)

class_0 = rng.normal(loc=(-2, -2), scale=1, size=(50, 2))
class_1 = rng.normal(loc=(2, 2), scale=1, size=(50, 2))


features = np.vstack([class_0, class_1])
y = np.hstack([np.zeros(50), np.ones(50)])

X = np.c_[np.ones(len(y)), features]

figure = go.Figure()
figure.add_scatter(x=class_0[:, 0], y=class_0[:, 1], mode="markers", name="class_0")
figure.add_scatter(x=class_1[:, 0], y=class_1[:, 1], mode="markers", name="class_0")
# figure.show()

model = LogisticRegression(C=10000000, solver="lbfgs", fit_intercept=False)
model.fit(X, y)

probabilities = model.predict_proba(X)[:, 1]

predictions = (probabilities >= 0.5).astype(int)
print(predictions)
