# Bagging and Random Forests Demo

Compares a **single deep decision tree**, **bagging**, and a **random forest** on
scikit-learn's two-moons dataset (300 noisy training points, 5,000 test points).

## Run

```
uv run bagging_random_forest.py
```

First run creates the environment automatically. It prints test accuracy and
writes two figures (also opened in your browser):

- `boundaries.html` — decision boundaries of the three models side by side.
  Shading is the predicted probability of the red class.
- `accuracy_vs_trees.html` — test accuracy of bagging and the random forest as
  trees are added (1 to 200), with the single tree as a dashed baseline.

## What to expect

- The single tree has jagged, fully confident regions with small islands around
  noisy points. Averaging 100 trees smooths the boundary and raises test accuracy.
- Accuracy rises quickly with the first few dozen trees, then levels off.
- With only two features the random forest and bagging behave similarly. The
  random-feature trick matters more when there are many features.

## Try changing

- `noise` in `make_moons` (more noise makes the single tree overfit more).
- `max_features` in the random forest.
- `n_estimators`, or `max_depth` on the base tree.
