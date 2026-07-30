"""Compact executable checks for the generated presentation examples."""

import numpy as np
from scipy import stats
from scipy.stats import loguniform
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs, make_classification
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import RandomizedSearchCV, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


def check_ensembles() -> None:
    X, y = make_classification(
        n_samples=240, n_features=8, n_informative=5, random_state=0
    )
    rf = RandomForestClassifier(
        n_estimators=80, max_features="sqrt", oob_score=True, random_state=0
    ).fit(X, y)
    assert 0 <= rf.oob_score_ <= 1

    ada = AdaBoostClassifier(
        estimator=DecisionTreeClassifier(max_depth=1),
        n_estimators=30,
        random_state=0,
    )
    assert np.isfinite(cross_val_score(ada, X, y, cv=3)).all()

    rng = np.random.default_rng(0)
    Xr = rng.uniform(0, 10, (120, 1))
    yr = np.sin(Xr[:, 0]) + rng.normal(0, 0.1, 120)
    pred = np.zeros_like(yr)
    initial_mse = np.mean((yr - pred) ** 2)
    for _ in range(30):
        tree = DecisionTreeRegressor(max_depth=2, random_state=0)
        tree.fit(Xr, yr - pred)
        pred += 0.1 * tree.predict(Xr)
    assert np.isfinite(pred).all() and np.mean((yr - pred) ** 2) < initial_mse

    variance = lambda rho, B: rho + (1 - rho) / B
    assert variance(0.2, 100) < variance(0.2, 10)
    assert abs(variance(0.2, 1_000_000) - 0.2) < 1e-5


def check_evaluation() -> None:
    y_true = np.array([0] * 90 + [1] * 10)
    y_pred = np.array([0] * 95 + [1] * 5)
    assert precision_score(y_true, y_pred) == 1
    assert recall_score(y_true, y_pred) == 0.5
    assert np.isclose(f1_score(y_true, y_pred), 2 / 3)
    assert confusion_matrix(y_true, y_pred).shape == (2, 2)

    X, y = make_classification(n_samples=240, n_features=8, random_state=3)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    scores_a = cross_val_score(model, X, y, cv=5)
    scores_b = cross_val_score(
        DecisionTreeClassifier(max_depth=3, random_state=0), X, y, cv=5
    )
    _, p_value = stats.ttest_rel(scores_a, scores_b)
    assert np.isfinite(scores_a).all() and np.isfinite(p_value)
    fitted = model.fit(X, y)
    assert np.isfinite(roc_auc_score(y, fitted.predict_proba(X)[:, 1]))


def check_unsupervised() -> None:
    X, _ = make_blobs(n_samples=240, centers=3, cluster_std=0.7, random_state=0)
    km = KMeans(n_clusters=3, n_init=10, random_state=0).fit(X)
    assert km.cluster_centers_.shape == (3, 2)
    assert silhouette_score(X, km.labels_) > 0.5

    pca = PCA(n_components=0.95).fit(X)
    reduced = pca.transform(X)
    assert pca.explained_variance_ratio_.sum() >= 0.95
    assert reduced.shape[0] == X.shape[0]

    gmm = GaussianMixture(n_components=3, random_state=0).fit(X)
    responsibility = gmm.predict_proba(X)
    assert responsibility.shape == (len(X), 3)
    assert np.allclose(responsibility.sum(axis=1), 1)
    bics = [GaussianMixture(k, random_state=0).fit(X).bic(X) for k in range(1, 6)]
    assert np.isfinite(bics).all()


def check_neural_math() -> None:
    rng = np.random.default_rng(0)
    W1, W2 = rng.normal(size=(4, 3)), rng.normal(size=(2, 4))
    x = np.array([1.0, 2.0, 3.0])
    assert np.allclose(W2 @ (W1 @ x), (W2 @ W1) @ x)

    sigmoid = lambda z: 1 / (1 + np.exp(-z))
    z = np.linspace(-6, 6, 1001)
    assert np.isclose((sigmoid(z) * (1 - sigmoid(z))).max(), 0.25)
    assert 0.25**10 < 1e-5

    batch = rng.normal(7, 3, (256, 20))
    normalized = (batch - batch.mean(0)) / np.sqrt(batch.var(0) + 1e-8)
    assert np.allclose(normalized.mean(0), 0, atol=1e-12)
    assert np.allclose(normalized.var(0), 1, atol=1e-7)

    # Equivalent tensor-shape checks for the Keras CNN shown in the deck.
    side = 28
    side = side - 3 + 1  # valid 3x3 convolution
    side //= 2  # 2x2 pooling
    side = side - 3 + 1
    side //= 2
    assert (side, side, 64) == (5, 5, 64)
    assert 20 * 64 + 64 == 1344  # first dense-layer parameter count


def check_optimization() -> None:
    grad = lambda theta: np.array([10 * theta[0], theta[1]])
    loss = lambda theta: 0.5 * (10 * theta[0] ** 2 + theta[1] ** 2)
    theta = np.array([1.0, 1.0])
    initial = loss(theta)
    m = np.zeros_like(theta)
    v = np.zeros_like(theta)
    for t in range(1, 51):
        g = grad(theta)
        m = 0.9 * m + 0.1 * g
        v = 0.999 * v + 0.001 * g**2
        theta -= 0.1 * (m / (1 - 0.9**t)) / (np.sqrt(v / (1 - 0.999**t)) + 1e-8)
    assert np.isfinite(theta).all() and loss(theta) < initial

    X, y = make_classification(n_samples=180, n_features=6, random_state=0)
    search = RandomizedSearchCV(
        SVC(),
        {"C": loguniform(1e-2, 1e2), "gamma": loguniform(1e-4, 1)},
        n_iter=5,
        cv=3,
        random_state=0,
    ).fit(X, y)
    assert np.isfinite(search.best_score_)


def check_capstone_pipeline() -> None:
    X, y = make_classification(
        n_samples=240, n_features=10, weights=[0.75, 0.25], random_state=42
    )
    candidates = [
        make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        RandomForestClassifier(n_estimators=40, random_state=42),
        GradientBoostingClassifier(random_state=42),
    ]
    scores = [cross_val_score(model, X, y, cv=3, scoring="f1") for model in candidates]
    assert all(np.isfinite(score).all() for score in scores)

    group = np.array([0] * 120 + [1] * 120)
    pred = candidates[0].fit(X, y).predict(X)
    group_rates = [pred[group == value].mean() for value in [0, 1]]
    assert np.isfinite(group_rates).all()


if __name__ == "__main__":
    check_ensembles()
    check_evaluation()
    check_unsupervised()
    check_neural_math()
    check_optimization()
    check_capstone_pipeline()
    print("presentation example checks passed")
