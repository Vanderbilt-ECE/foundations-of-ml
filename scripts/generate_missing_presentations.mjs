import { mkdirSync, writeFileSync } from 'node:fs'
import { join } from 'node:path'

const raw = String.raw
const decks = []

const ensemble = 'Ensemble Methods'
decks.push(
  {
    subject: ensemble,
    title: 'Bagging and Random Forests',
    subtitle: 'Turn unstable trees into a stable ensemble',
    seed: 610,
    slides: [
      {
        title: 'Bootstrap Sampling', kind: 'equation',
        items: [
          ['Sample with replacement', 'Draw n observations from n rows; repeats are expected.'],
          ['Out-of-bag rows', 'About 36.8% of the original rows are absent from one bootstrap sample.'],
          ['Why it matters', 'One dataset can imitate many plausible training sets.'],
        ],
        formula: raw`\left(1-\frac1n\right)^n \longrightarrow e^{-1}\approx0.368`,
        notes: 'Derive the out-of-bag fraction and connect bootstrap resampling to the repeated-training-set thought experiment from bias–variance.',
      },
      {
        title: 'Bagging = Bootstrap + Aggregate', kind: 'flow',
        items: [
          ['Train in parallel', 'Fit the same high-variance learner on many bootstrap samples.'],
          ['Combine', 'Average for regression; majority vote for classification.'],
          ['Effect', 'Variance falls while the base learner’s bias changes little.'],
        ],
        nodes: ['Dataset', 'Bootstrap samples', 'Deep trees', 'Average / vote'],
        formula: raw`\hat f_{\mathrm{bag}}(x)=\frac1B\sum_{b=1}^B\hat f_b(x)`,
        notes: 'Reuse the dartboard intuition: averaging tightens the prediction cloud around roughly the same center.',
      },
      {
        title: 'Why Trees Are the Natural Base Learner', kind: 'compare',
        items: [
          ['Deep decision tree', 'Low bias, high variance: plenty of instability for averaging to remove.'],
          ['Linear regression', 'Already comparatively stable: bagging has little variance to cancel.'],
          ['Design rule', 'Bagging pays off when base learners are accurate but unstable.'],
        ],
        notes: 'Answer the natural “why not bag everything?” question directly using the bias–variance framework.',
      },
      {
        title: 'Random Forests Add Feature Randomness', kind: 'network',
        items: [
          ['Correlated trees limit averaging', 'A dominant feature can force nearly every bagged tree into the same early splits.'],
          ['Random feature subsets', 'At each split, consider only m of the d available features.'],
          ['More diversity', 'Different roots and branches reduce correlation between tree errors.'],
        ],
        formula: raw`m\approx\sqrt d\ \text{for classification (a common default)}`,
        notes: 'Feature subsampling exists to decorrelate trees; that is the key addition over plain bagging.',
      },
      {
        title: 'Out-of-Bag Evaluation', kind: 'code',
        items: [
          ['For each row', 'Predict using only trees whose bootstrap sample omitted that row.'],
          ['Nearly free validation', 'Aggregate those predictions into an OOB score without a separate split.'],
        ],
        code: raw`from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=200, max_features="sqrt",
    oob_score=True, random_state=0,
)

rf.fit(X, y)
print(rf.oob_score_)`,
        notes: 'Compare OOB accuracy with 5-fold cross-validation and explain why this shortcut is specific to bootstrap-based ensembles.',
      },
      {
        title: 'Feature Importance — Useful, Not Causal', kind: 'chart',
        items: [
          ['Impurity reduction', 'Aggregate how much each feature improves splits across all trees.'],
          ['Practical use', 'A quick global view for interpretation and feature screening.'],
          ['Caveats', 'High-cardinality and correlated features can distort the ranking.'],
        ],
        chartLabels: ['f₁', 'f₂', 'f₃', 'f₄', 'f₅'],
        notes: 'Stress that feature importance is predictive attribution, not causal evidence.',
      },
      {
        title: 'Bagging vs. the Next Idea', kind: 'summary',
        items: [
          ['Bootstrap', 'Simulate many training sets.'],
          ['Bagging', 'Average high-variance learners.'],
          ['Random forest', 'Decorrelate trees with feature randomness.'],
        ],
        next: 'Next: boosting trains weak learners sequentially, each correcting what remains wrong.',
        notes: 'Close on parallel-and-independent versus sequential-and-corrective.',
      },
    ],
  },
  {
    subject: ensemble,
    title: 'Boosting (AdaBoost, Gradient Boosting)',
    displayTitle: 'Boosting: AdaBoost and Gradient Boosting',
    subtitle: 'Build strength by learning from mistakes',
    seed: 640,
    slides: [
      {
        title: 'The Boosting Idea', kind: 'flow',
        items: [
          ['Weak learners', 'Use shallow trees that are only slightly better than guessing.'],
          ['Sequential focus', 'Each round pays more attention to what the ensemble still gets wrong.'],
          ['Weighted combination', 'Many small corrections become one strong predictor.'],
        ],
        nodes: ['Weak model 1', 'Residual mistakes', 'Weak model 2', 'Strong ensemble'],
        notes: 'Contrast weak shallow trees here with the strong deep trees used by bagging.',
      },
      {
        title: 'AdaBoost Reweights Examples', kind: 'equation',
        items: [
          ['Weighted error', 'Measure a stump using the current example weights.'],
          ['Learner weight', 'More accurate stumps receive a larger final vote.'],
          ['Example update', 'Increase weights on mistakes; decrease them on correct cases.'],
        ],
        formula: raw`\alpha_t=\frac12\log\frac{1-\epsilon_t}{\epsilon_t},\qquad w_i^{(t+1)}=w_i^{(t)}e^{-\alpha_t y_i h_t(x_i)}`,
        notes: 'Plug in errors near zero and near one-half to show how the learner vote behaves.',
      },
      {
        title: 'AdaBoost in scikit-learn', kind: 'code',
        items: [
          ['Base learner', 'A depth-1 decision stump.'],
          ['Ensemble', 'One hundred adaptive rounds.'],
        ],
        code: raw`from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

stump = DecisionTreeClassifier(max_depth=1)
ada = AdaBoostClassifier(
    estimator=stump, n_estimators=100, random_state=0,
)
print(cross_val_score(ada, X, y, cv=5).mean())`,
        notes: 'A weak learner is intentionally simple; strength comes from the sequence.',
      },
      {
        title: 'Gradient Boosting Fits What Is Still Wrong', kind: 'equation',
        items: [
          ['General loss', 'Fit each new learner to the negative gradient of the current loss.'],
          ['Squared error', 'The negative gradient is simply the residual y − F(x).'],
          ['Function-space descent', 'Add a small learned function instead of moving one parameter vector.'],
        ],
        formula: raw`\begin{aligned}F_t(x)&=F_{t-1}(x)+\eta h_t(x)\\-\frac{\partial}{\partial F}\frac12(y-F)^2&=y-F\end{aligned}`,
        notes: 'Connect η directly to the learning rate from gradient descent and describe boosting as descent in function space.',
      },
      {
        title: 'A Minimal Gradient-Boosting Loop', kind: 'code',
        items: [
          ['Predict', 'Start with a simple running prediction.'],
          ['Correct', 'Fit a shallow tree to residuals.'],
        ],
        code: raw`pred = np.zeros(len(y_reg))
trees = []
for _ in range(50):
    residual = y_reg - pred
    tree = DecisionTreeRegressor(max_depth=2)
    tree.fit(X_reg, residual)
    pred += 0.1 * tree.predict(X_reg)
    trees.append(tree)

assert np.isfinite(pred).all()`,
        notes: 'Plot the running prediction after several rounds so students can see successive residual correction.',
      },
      {
        title: 'Learning Rate and Number of Rounds', kind: 'chart',
        items: [
          ['Small η', 'Slower, finer corrections; usually needs more estimators.'],
          ['Large η', 'Fast progress but greater risk of chasing noise.'],
          ['Unlike bagging', 'Too many boosting rounds can overfit.'],
        ],
        chartLabels: ['20', '50', '100', '200', '400'],
        notes: 'Use the validation curve to explain why n_estimators is an active tuning choice for boosting.',
      },
      {
        title: 'Bagging vs. Boosting', kind: 'compare',
        items: [
          ['Bagging', 'Parallel deep trees; bootstrap diversity; primarily reduces variance.'],
          ['Boosting', 'Sequential shallow trees; corrective updates; primarily reduces bias.'],
          ['Practical reality', 'Gradient-boosted trees are exceptionally strong on structured data.'],
        ],
        notes: 'Make students articulate why deep versus shallow base learners fit each strategy.',
      },
      {
        title: 'Boosting in One View', kind: 'summary',
        items: [
          ['AdaBoost', 'Reweight hard examples.'],
          ['Gradient boosting', 'Fit negative gradients.'],
          ['Tune', 'Balance η against rounds.'],
        ],
        next: 'Next: a formal explanation of why diverse ensembles work.',
        notes: 'Emphasize sequential correction as the unifying idea.',
      },
    ],
  },
  {
    subject: ensemble,
    title: 'Why Ensembles Work',
    subtitle: 'Diversity turns many imperfect models into one stronger model',
    seed: 670,
    slides: [
      {
        title: 'Diversity Is the Essential Ingredient', kind: 'compare',
        items: [
          ['Identical errors', 'Perfectly correlated models fail on the same cases; averaging changes nothing.'],
          ['Different errors', 'Less-correlated mistakes partially cancel when predictions are combined.'],
          ['How algorithms create it', 'Bootstrap samples, feature subsets, and corrective reweighting manufacture diversity.'],
        ],
        notes: 'Reframe both bagging and boosting as techniques for generating useful disagreement.',
      },
      {
        title: 'Variance of an Averaged Ensemble', kind: 'equation',
        items: [
          ['Independent models', 'When ρ = 0, variance shrinks by a factor of B.'],
          ['Correlated models', 'Positive error correlation creates a nonzero floor.'],
          ['Design implication', 'Lowering ρ can matter more than merely adding estimators.'],
        ],
        formula: raw`\operatorname{Var}\!\left(\frac1B\sum_b\hat f_b\right)=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2\ \longrightarrow\ \rho\sigma^2`,
        notes: 'Use the limit to explain random-forest diminishing returns and the value of feature subsampling.',
      },
      {
        title: 'Correlation Sets the Variance Floor', kind: 'chart',
        items: [
          ['ρ = 0', 'Variance keeps falling toward zero.'],
          ['ρ = 0.2', 'More models help, then flatten at 0.2σ².'],
          ['ρ = 0.5', 'A highly correlated ensemble has little room to improve.'],
        ],
        chartLabels: ['1', '10', '50', '100', '500'],
        notes: 'The plot is the rigorous justification for decorrelating trees.',
      },
      {
        title: 'Bias–Variance, Revisited', kind: 'flow',
        items: [
          ['Bagging / random forests', 'Start with a low-bias, high-variance deep tree and reduce variance.'],
          ['Boosting', 'Start with high-bias, low-variance stumps and correct systematic error.'],
          ['One framework', 'Both methods move a learner toward lower expected test error.'],
        ],
        nodes: ['Base learner', 'Manufacture diversity', 'Combine', 'Lower test error'],
        notes: 'This is the theoretical synthesis of the full ensemble unit.',
      },
      {
        title: 'The Limits of Ensembling', kind: 'cards',
        items: [
          ['Noise floor', 'No ensemble can remove irreducible uncertainty in the data.'],
          ['Diminishing returns', 'Additional estimators eventually add little accuracy.'],
          ['Latency and compute', 'Hundreds of models cost more to train and query than one.'],
          ['Interpretability', 'A forest is harder to explain than a single tree.'],
        ],
        notes: 'Accuracy is only one axis; deployment cost and explanation burden matter too.',
      },
      {
        title: 'Why Ensembles Work', kind: 'summary',
        items: [
          ['Diversity', 'Errors must differ.'],
          ['Correlation', 'Sets the variance floor.'],
          ['Tradeoffs', 'Noise, cost, and opacity remain.'],
        ],
        next: 'Next: unsupervised learning—finding structure without labels.',
        notes: 'Mark the close of the supervised-learning arc.',
      },
    ],
  },
)

const unsupervised = 'Unsupervised Learning'
decks.push(
  {
    subject: unsupervised,
    title: 'k-Means and Hierarchical Clustering',
    subtitle: 'Find groups when no labels define the answer',
    seed: 710,
    slides: [
      {
        title: 'The k-Means Objective', kind: 'equation',
        items: [
          ['Partition', 'Assign n observations to K clusters.'],
          ['Centroids', 'Represent each cluster by its mean.'],
          ['Loss without labels', 'Minimize squared distance to the assigned centroid.'],
        ],
        formula: raw`J=\sum_{i=1}^n\lVert x_i-\mu_{c_i}\rVert_2^2`,
        notes: 'Both the discrete assignments and continuous centroids are unknown, which motivates alternating updates.',
      },
      {
        title: 'Lloyd’s Algorithm Alternates Two Easy Steps', kind: 'flow',
        items: [
          ['Assign', 'Send each point to its nearest centroid.'],
          ['Update', 'Move each centroid to the mean of its assigned points.'],
          ['Repeat', 'J never increases, so the process converges to a local optimum.'],
        ],
        nodes: ['Initialize μ', 'Assign cᵢ', 'Update μ', 'Converged?'],
        formula: raw`c_i\leftarrow\arg\min_k\lVert x_i-\mu_k\rVert^2,\quad \mu_k\leftarrow\frac1{|C_k|}\sum_{i\in C_k}x_i`,
        notes: 'Animate the assign/update loop and distinguish convergence from finding the global optimum.',
      },
      {
        title: 'Initialization Changes the Answer', kind: 'compare',
        items: [
          ['Single random start', 'Centroids can crowd one region and settle in a poor local optimum.'],
          ['Multiple restarts', 'Keep the run with the smallest final inertia.'],
          ['k-means++', 'Favor initial centroids far from those already selected.'],
        ],
        notes: 'Practical k-means is best-of-many-runs k-means, usually with k-means++.',
      },
      {
        title: 'Choosing K Without Labels', kind: 'chart',
        items: [
          ['Elbow', 'Inertia always falls; look for diminishing returns.'],
          ['Silhouette', 'Reward tight clusters that are separated from their nearest neighbor cluster.'],
          ['No oracle', 'These are structural diagnostics, not ground-truth accuracy.'],
        ],
        chartLabels: ['2', '3', '4', '5', '6'],
        formula: raw`s(i)=\frac{b(i)-a(i)}{\max(a(i),b(i))}`,
        notes: 'Compare the monotonic inertia curve with a silhouette curve that can have a clear maximum.',
      },
      {
        title: 'Where k-Means Fails', kind: 'cards',
        items: [
          ['Nonconvex shapes', 'One centroid cannot represent a curved cluster.'],
          ['Unequal sizes', 'Euclidean partitions can steal points from a larger cluster.'],
          ['Outliers', 'Means and squared distance are not robust.'],
          ['Unscaled features', 'Large numeric ranges dominate distance.'],
        ],
        notes: 'Tie each failure to the exact squared-Euclidean objective.',
      },
      {
        title: 'Hierarchical Clustering Builds a Dendrogram', kind: 'flow',
        items: [
          ['Bottom up', 'Start with one cluster per point.'],
          ['Merge', 'Repeatedly combine the closest pair under a linkage rule.'],
          ['Choose later', 'Cut the dendrogram after fitting to obtain any desired number of clusters.'],
        ],
        nodes: ['Points', 'Small groups', 'Larger branches', 'One hierarchy'],
        notes: 'The hierarchy is the output; K becomes a post-hoc cut rather than an upfront input.',
      },
      {
        title: 'Linkage Defines “Closest Clusters”', kind: 'cards',
        items: [
          ['Single', 'Nearest pair; prone to chaining.'],
          ['Complete', 'Farthest pair; favors compact groups.'],
          ['Average', 'Average all cross-cluster pair distances.'],
          ['Ward', 'Minimize the increase in within-cluster variance.'],
        ],
        notes: 'Treat linkage as the structural assumption of hierarchical clustering.',
      },
      {
        title: 'Two Ways to Find Groups', kind: 'summary',
        items: [
          ['k-means', 'Fast, flat, needs K.'],
          ['Hierarchical', 'Rich tree, higher cost.'],
          ['Both', 'Scale distance features first.'],
        ],
        next: 'Next: reduce dimensionality with PCA, t-SNE, and UMAP.',
        notes: 'Choose based on scale and whether the hierarchy itself is useful.',
      },
    ],
  },
  {
    subject: unsupervised,
    title: 'Dimensionality Reduction - PCA, t-SNE, UMAP',
    displayTitle: 'Dimensionality Reduction: PCA, t-SNE, and UMAP',
    subtitle: 'Compress data while preserving useful structure',
    seed: 740,
    slides: [
      {
        title: 'Why Reduce Dimension?', kind: 'cards',
        items: [
          ['Visualize', 'Project high-dimensional data into two or three dimensions.'],
          ['Denoise', 'Discard directions containing little stable variation.'],
          ['Accelerate', 'Give downstream k-NN or k-means fewer coordinates.'],
          ['Compress', 'Represent many correlated features with a smaller latent basis.'],
        ],
        notes: 'Distinguish raw feature count from intrinsic degrees of freedom.',
      },
      {
        title: 'PCA Maximizes Projected Variance', kind: 'equation',
        items: [
          ['Center first', 'PCA describes variation around the data mean.'],
          ['Choose a unit direction', 'Prevent the objective from growing by simple rescaling.'],
          ['Equivalent view', 'The same subspace minimizes linear reconstruction error.'],
        ],
        formula: raw`v_1=\arg\max_{\lVert v\rVert=1}v^\top\Sigma v`,
        notes: 'Use an elongated point cloud: its long axis creates the widest one-dimensional projection.',
      },
      {
        title: 'The Optimizer Is an Eigenvector', kind: 'equation',
        items: [
          ['Constrained objective', 'Use a Lagrange multiplier for vᵀv = 1.'],
          ['Stationary condition', 'Σv = λv.'],
          ['Select', 'The largest eigenvalue gives the largest achievable variance.'],
        ],
        formula: raw`\mathcal L=v^\top\Sigma v-\lambda(v^\top v-1)\ \Rightarrow\ \Sigma v=\lambda v`,
        notes: 'This is the promised payoff of eigendecomposition and the spectral theorem.',
      },
      {
        title: 'Full PCA Is a Change of Basis', kind: 'flow',
        items: [
          ['Order eigenvectors', 'Sort covariance directions by descending eigenvalue.'],
          ['Keep the first k', 'They are mutually orthogonal because Σ is symmetric.'],
          ['Project', 'Coordinates in that basis are the principal-component scores.'],
        ],
        nodes: ['Centered X', 'Covariance Σ', 'Eigenvectors Qₖ', 'XQₖ'],
        formula: raw`\Sigma=Q\Lambda Q^\top,\qquad X_{\mathrm{reduced}}=X_{\mathrm{centered}}Q_k`,
        notes: 'Reconstruction error corresponds to variance in the discarded directions.',
      },
      {
        title: 'PCA in scikit-learn', kind: 'code',
        items: [
          ['Fit', 'Learn principal directions from training data.'],
          ['Transform', 'Project into the lower-dimensional coordinates.'],
        ],
        code: raw`from sklearn.decomposition import PCA

pca = PCA(n_components=0.95)
X_train_small = pca.fit_transform(X_train)
X_test_small = pca.transform(X_test)

assert pca.explained_variance_ratio_.sum() >= 0.95
assert X_train_small.shape[1] <= X_train.shape[1]`,
        notes: 'Fit PCA inside a pipeline or only on training data to avoid leakage.',
      },
      {
        title: 'Explained Variance Chooses k', kind: 'chart',
        items: [
          ['Eigenvalue', 'Variance captured by one component.'],
          ['Ratio', 'Divide by total variance.'],
          ['Cumulative target', 'Keep enough components for a target such as 95%.'],
        ],
        chartLabels: ['PC1', 'PC2', 'PC3', 'PC4', 'PC5'],
        formula: raw`r_k=\frac{\lambda_k}{\sum_j\lambda_j}`,
        notes: 'Connect the scree-plot elbow to choosing K for k-means.',
      },
      {
        title: 'PCA vs. t-SNE / UMAP', kind: 'compare',
        items: [
          ['PCA', 'Linear, deterministic, fast, globally interpretable variance axes.'],
          ['t-SNE / UMAP', 'Nonlinear, visualization-focused, preserve local neighborhoods.'],
          ['Caution', 'Distances and apparent cluster sizes in nonlinear embeddings can mislead.'],
        ],
        notes: 'Use nonlinear embeddings to explore, not as proof of true cluster separation.',
      },
      {
        title: 'Dimensionality Reduction', kind: 'summary',
        items: [
          ['PCA', 'Eigenvectors of covariance.'],
          ['Variance', 'Guides retained dimension.'],
          ['Nonlinear maps', 'Reveal local manifolds.'],
        ],
        next: 'Next: Gaussian mixtures make clustering probabilistic.',
        notes: 'The covariance ellipse has become a working algorithm.',
      },
    ],
  },
  {
    subject: unsupervised,
    title: 'Gaussian Mixture Models',
    subtitle: 'Replace hard spherical clusters with soft probabilistic components',
    seed: 770,
    slides: [
      {
        title: 'A Mixture Is a Generative Story', kind: 'equation',
        items: [
          ['Choose a component', 'Sample k according to its mixing weight πₖ.'],
          ['Generate a point', 'Draw x from that component’s Gaussian.'],
          ['Flexible density', 'Several simple Gaussians form a multimodal distribution.'],
        ],
        formula: raw`p(x)=\sum_{k=1}^K\pi_k\,\mathcal N(x\mid\mu_k,\Sigma_k),\qquad \sum_k\pi_k=1`,
        notes: 'Build the one-dimensional picture by adding two weighted bell curves.',
      },
      {
        title: 'Responsibilities Are Soft Assignments', kind: 'equation',
        items: [
          ['Posterior membership', 'Each point receives a probability for every component.'],
          ['Bayes’ theorem', 'Prior × likelihood, normalized across components.'],
          ['Boundary uncertainty', 'Ambiguous points can split responsibility between clusters.'],
        ],
        formula: raw`\gamma_{ik}=P(z_i=k\mid x_i)=\frac{\pi_k\mathcal N(x_i\mid\mu_k,\Sigma_k)}{\sum_j\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j)}`,
        notes: 'Map prior, likelihood, and posterior directly to the probability unit.',
      },
      {
        title: 'Expectation–Maximization', kind: 'flow',
        items: [
          ['E-step', 'Compute responsibilities using current parameters.'],
          ['M-step', 'Update means, covariances, and mixing weights using weighted statistics.'],
          ['Repeat', 'Likelihood improves until convergence to a local optimum.'],
        ],
        nodes: ['Initialize', 'E: soft assign', 'M: update', 'Converged?'],
        formula: raw`\mu_k=\frac{\sum_i\gamma_{ik}x_i}{\sum_i\gamma_{ik}},\qquad \pi_k=\frac1n\sum_i\gamma_{ik}`,
        notes: 'Place EM beside k-means assign/update: hard assignments become probabilities.',
      },
      {
        title: 'Fit and Inspect a GMM', kind: 'code',
        items: [
          ['predict_proba', 'Returns responsibilities whose rows sum to one.'],
          ['predict', 'Uses the largest responsibility when a hard label is needed.'],
        ],
        code: raw`from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(
    n_components=3, covariance_type="full", random_state=0,
)
gmm.fit(X)
responsibility = gmm.predict_proba(X)

assert responsibility.shape == (len(X), 3)
assert np.allclose(responsibility.sum(axis=1), 1)`,
        notes: 'Show confidently assigned center points and blended boundary points.',
      },
      {
        title: 'What GMM Fixes—and Costs', kind: 'compare',
        items: [
          ['More flexible', 'Full covariance supports tilted, elongated, differently sized clusters and soft membership.'],
          ['More parameters', 'Each component estimates a covariance matrix as well as a mean.'],
          ['Tradeoff', 'Needs more data and can face numerical instability in high dimension.'],
        ],
        notes: 'Flexibility addresses the k-means failure gallery but reintroduces variance and estimation cost.',
      },
      {
        title: 'Choose Components With Information Criteria', kind: 'chart',
        items: [
          ['Likelihood rewards fit', 'More components can always explain the sample better.'],
          ['AIC / BIC penalize complexity', 'Extra free parameters must earn their keep.'],
          ['Decision', 'Prefer the K with the smallest criterion.'],
        ],
        chartLabels: ['1', '2', '3', '4', '5'],
        formula: raw`\mathrm{BIC}=-2\log\hat L+p\log n,\qquad \mathrm{AIC}=-2\log\hat L+2p`,
        notes: 'Connect fit-plus-penalty directly to regularization and bias–variance.',
      },
      {
        title: 'Probabilistic Clustering', kind: 'summary',
        items: [
          ['Mixture', 'Weighted Gaussian components.'],
          ['EM', 'Soft assign, then update.'],
          ['BIC / AIC', 'Balance fit and complexity.'],
        ],
        next: 'Next: neural networks return to supervised learning with composable nonlinear models.',
        notes: 'Close the unsupervised unit by linking geometry, eigendecomposition, and probability.',
      },
    ],
  },
)
const evaluation = 'Model Evaluation'
decks.push(
  {
    subject: evaluation,
    title: 'Accuracy, Precision, Recall, F1, ROC-AUC',
    displayTitle: 'Accuracy, Precision, Recall, F1, and ROC/AUC',
    subtitle: 'Choose metrics that reflect the real cost of mistakes',
    seed: 510,
    slides: [
      {
        title: 'Accuracy Can Look Great and Be Useless', kind: 'equation',
        items: [
          ['Imbalanced data', '990 healthy cases and 10 disease cases.'],
          ['Trivial classifier', 'Always predict “healthy.”'],
          ['The trap', '99% accuracy, but zero detected disease cases.'],
        ],
        formula: raw`\mathrm{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}=0.99`,
        notes: 'Let the 99% result land before revealing its zero recall.',
      },
      {
        title: 'Four Counts Under Every Metric', kind: 'matrix',
        items: [
          ['TP', 'Predicted positive, actually positive.'],
          ['TN', 'Predicted negative, actually negative.'],
          ['FP', 'False alarm.'],
          ['FN', 'Missed positive.'],
        ],
        notes: 'Make students state each cell in the disease-screening context.',
      },
      {
        title: 'Precision and Recall Ask Different Questions', kind: 'equation',
        items: [
          ['Precision', 'When the model says yes, how often is it right?'],
          ['Recall', 'Of all real positives, how many did the model catch?'],
          ['Tradeoff', 'Changing a decision threshold usually moves one against the other.'],
        ],
        formula: raw`\mathrm{Precision}=\frac{TP}{TP+FP},\qquad \mathrm{Recall}=\frac{TP}{TP+FN}`,
        notes: 'Spam filtering often prioritizes precision; screening often prioritizes recall.',
      },
      {
        title: 'F1 Penalizes Imbalance', kind: 'equation',
        items: [
          ['Harmonic mean', 'Both precision and recall must be reasonably high.'],
          ['Example', 'Precision 1.0 and recall 0.01 gives F1 ≈ 0.0198, not 0.505.'],
          ['Fβ', 'Use β when recall and precision have unequal importance.'],
        ],
        formula: raw`F_1=2\frac{PR}{P+R},\qquad F_\beta=(1+\beta^2)\frac{PR}{\beta^2P+R}`,
        notes: 'Contrast arithmetic and harmonic means to show why F1 cannot be gamed by one strong component.',
      },
      {
        title: 'ROC Curves Sweep the Threshold', kind: 'chart',
        items: [
          ['Each point', 'A different classification threshold.'],
          ['Axes', 'True-positive rate versus false-positive rate.'],
          ['Ideal', 'Near the upper-left corner; the diagonal is random ranking.'],
        ],
        chartLabels: ['0', '.25', '.50', '.75', '1'],
        notes: 'Describe moving along the curve operationally: lower thresholds catch more positives and more false alarms.',
      },
      {
        title: 'AUC Measures Ranking Quality', kind: 'equation',
        items: [
          ['Threshold independent', 'Summarizes the entire ROC curve.'],
          ['Probability view', 'Chance that a random positive receives a higher score than a random negative.'],
          ['Not calibration', 'A strong AUC does not choose a useful operating threshold for you.'],
        ],
        formula: raw`\mathrm{AUC}=P\big(s(x^+)>s(x^-)\big)`,
        notes: 'AUC assesses ranking, not whether predicted probabilities are calibrated.',
      },
      {
        title: 'Choose the Metric From the Consequences', kind: 'cards',
        items: [
          ['Accuracy', 'Balanced classes and similar error costs.'],
          ['Precision', 'False positives are costly.'],
          ['Recall', 'False negatives are costly.'],
          ['F1 / AUC', 'Balance P–R or compare ranking across thresholds.'],
        ],
        notes: 'Metric choice is a modeling decision tied to the real application.',
      },
      {
        title: 'A Metric Toolbox', kind: 'summary',
        items: [
          ['Counts', 'Start with TP, TN, FP, FN.'],
          ['Costs', 'Know which error hurts.'],
          ['Thresholds', 'Evaluate the full tradeoff.'],
        ],
        next: 'Next: read the confusion matrix itself, including the multiclass case.',
        notes: 'Every metric is a different summary of underlying decisions and their errors.',
      },
    ],
  },
  {
    subject: evaluation,
    title: 'Confusion Matrices',
    subtitle: 'See which mistakes a classifier makes—not only how many',
    seed: 530,
    slides: [
      {
        title: 'The Binary Confusion Matrix', kind: 'matrix',
        items: [
          ['Diagonal', 'Correct predictions: TN and TP.'],
          ['Off-diagonal', 'Errors: FP and FN.'],
          ['Axis warning', 'Libraries disagree on orientation—always read the labels.'],
        ],
        notes: 'Have students derive accuracy, precision, and recall directly from the four cells.',
      },
      {
        title: 'Same Accuracy, Different Failure', kind: 'compare',
        items: [
          ['Model A', 'Errors concentrate in false positives: many false alarms.'],
          ['Model B', 'Errors concentrate in false negatives: many missed positives.'],
          ['Why the matrix wins', 'A single accuracy number cannot distinguish these consequences.'],
        ],
        notes: 'Ask which model fits airport screening versus spam filtering.',
      },
      {
        title: 'Compute and Display the Matrix', kind: 'code',
        items: [
          ['Raw counts', 'confusion_matrix returns the table.'],
          ['Readable diagnostic', 'ConfusionMatrixDisplay adds labels and intensity.'],
        ],
        code: raw`from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
)

y_pred = model.predict(X_test)
cm = confusion_matrix(y_test, y_pred)
ConfusionMatrixDisplay(
    cm, display_labels=["Negative", "Positive"],
).plot()`,
        notes: 'Insist on held-out predictions for evaluation, not training-set predictions.',
      },
      {
        title: 'Multiclass: A K × K Error Map', kind: 'matrix',
        items: [
          ['Diagonal', 'Correct predictions for each class.'],
          ['Off-diagonal structure', 'Specific class pairs the model confuses.'],
          ['Per-class metrics', 'Treat one class as positive against all others.'],
        ],
        formula: raw`P_k=\frac{C_{kk}}{\sum_i C_{ik}},\qquad R_k=\frac{C_{kk}}{\sum_j C_{kj}}`,
        notes: 'Use digit confusions such as 4↔9 to show that errors often reveal data structure.',
      },
      {
        title: 'Macro, Weighted, and Micro Averaging', kind: 'cards',
        items: [
          ['Macro', 'Average classes equally; rare classes matter as much as common ones.'],
          ['Weighted', 'Weight each class by its support.'],
          ['Micro', 'Pool all decisions first; equals accuracy for single-label multiclass.'],
          ['Rule of thumb', 'Inspect per-class metrics when a rare class is important.'],
        ],
        notes: 'Show how weighted and micro averages can hide failure on a rare but important class.',
      },
      {
        title: 'One Table, Every Classification Metric', kind: 'summary',
        items: [
          ['Diagnose', 'Read error direction.'],
          ['Generalize', 'Use K × K for multiclass.'],
          ['Summarize carefully', 'Choose averaging explicitly.'],
        ],
        next: 'Next: decide whether two measured model scores are genuinely different.',
        notes: 'The matrix preserves information that every aggregate metric discards.',
      },
    ],
  },
  {
    subject: evaluation,
    title: 'Statistical Significance in Model Comparison',
    subtitle: 'Is a measured improvement real—or sampling noise?',
    seed: 550,
    slides: [
      {
        title: 'Performance Estimates Are Random Variables', kind: 'equation',
        items: [
          ['A test score is a statistic', 'It depends on which observations landed in the test set.'],
          ['Resample, remeasure', 'A different split gives a different number for the same procedure.'],
          ['Implication', '“91% vs. 89%” is incomplete without uncertainty.'],
        ],
        formula: raw`\widehat{\mathrm{Acc}}=\frac1n\sum_{i=1}^n\mathbf1[\hat y_i=y_i]`,
        notes: 'Connect the distribution of accuracy across splits to the sampling distribution of a sample mean.',
      },
      {
        title: 'The Null-Hypothesis Frame', kind: 'chart',
        items: [
          ['H₀', 'The models have equal true performance; the observed gap is noise.'],
          ['p-value', 'How surprising a gap this large would be if H₀ were true.'],
          ['Not what it means', 'It is not the probability that H₀ is true.'],
        ],
        chartLabels: ['−Δ', '', '0', '', '+Δ'],
        notes: 'Treat 0.05 as a convention, not a cliff; discuss effect size alongside evidence.',
      },
      {
        title: 'McNemar’s Test Uses Paired Disagreements', kind: 'matrix',
        items: [
          ['Same test examples', 'Each row has a prediction from model A and model B.'],
          ['Informative cells', 'A-right/B-wrong versus A-wrong/B-right.'],
          ['Ignore agreements', 'Both-right and both-wrong do not distinguish the models.'],
        ],
        formula: raw`\chi^2=\frac{(|n_{01}-n_{10}|-1)^2}{n_{01}+n_{10}}`,
        notes: 'Distinguish this model-agreement table from a predicted-vs-actual confusion matrix.',
      },
      {
        title: 'Paired Tests Across CV Folds', kind: 'equation',
        items: [
          ['Pair the folds', 'Both models are evaluated on the same held-out observations.'],
          ['Test differences', 'Analyze dᵢ = score Aᵢ − score Bᵢ.'],
          ['Caveat', 'Overlapping training folds violate full independence and can make ordinary t-tests optimistic.'],
        ],
        formula: raw`t=\frac{\bar d}{s_d/\sqrt{k}}`,
        notes: 'Present the paired t-test as a useful heuristic with a real dependence caveat.',
      },
      {
        title: 'Statistical vs. Practical Significance', kind: 'compare',
        items: [
          ['Statistically significant', 'The observed effect is unlikely under the null model.'],
          ['Practically meaningful', 'The effect is large enough to justify complexity, cost, or risk.'],
          ['Report both', 'Give the effect size and an interval, not only a p-value.'],
        ],
        notes: 'Large samples can make tiny, worthless improvements look statistically decisive.',
      },
      {
        title: 'Model Comparison Checklist', kind: 'cards',
        items: [
          ['Pair observations', 'Exploit shared examples or folds.'],
          ['Quantify uncertainty', 'Intervals or paired tests.'],
          ['Control multiplicity', 'Do not cherry-pick one winner from many tests.'],
          ['Judge value', 'Weigh the effect against deployment cost.'],
        ],
        notes: 'Connect multiple comparisons to repeatedly touching the test set.',
      },
      {
        title: 'Trustworthy Comparisons', kind: 'summary',
        items: [
          ['Scores vary', 'One number is one sample.'],
          ['Pair wisely', 'Use shared outcomes.'],
          ['Size matters', 'Practical ≠ statistical.'],
        ],
        next: 'Next: common evaluation failures—leakage and class imbalance.',
        notes: 'A comparison needs uncertainty, effect size, and deployment context.',
      },
    ],
  },
  {
    subject: evaluation,
    title: 'Common Pitfalls - Data Leakage and Class Imbalance',
    displayTitle: 'Common Pitfalls: Data Leakage and Class Imbalance',
    subtitle: 'When excellent-looking numbers cannot be trusted',
    seed: 580,
    slides: [
      {
        title: 'Data Leakage: Information From the Wrong Time', kind: 'flow',
        items: [
          ['Definition', 'Unavailable or held-out information influences training.'],
          ['Result', 'Evaluation looks excellent; deployment collapses.'],
          ['Diagnostic question', 'Would this information exist at prediction time?'],
        ],
        nodes: ['Full data', 'Leaky transform', 'Train', 'Inflated score'],
        notes: 'Frame leakage as a timing and information-boundary failure.',
      },
      {
        title: 'Split Before You Fit Preprocessing', kind: 'compare',
        items: [
          ['Wrong', 'Fit scaling, imputation, or selection on the full dataset, then split.'],
          ['Right', 'Split first; fit transforms only on training data; apply them unchanged to validation/test.'],
          ['Best guardrail', 'Use a Pipeline so cross-validation refits preprocessing inside each training fold.'],
        ],
        notes: 'This is the most common beginner leakage path and the easiest one to prevent structurally.',
      },
      {
        title: 'A Pipeline Enforces the Boundary', kind: 'code',
        items: [
          ['Fit', 'Each fold learns its own scaling statistics.'],
          ['Transform', 'Held-out rows never influence those statistics.'],
        ],
        code: raw`from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

model = make_pipeline(
    StandardScaler(), LogisticRegression(),
)
scores = cross_val_score(model, X, y, cv=5)
assert np.isfinite(scores).all()`,
        notes: 'Default to pipelines whenever preprocessing learns anything from data.',
      },
      {
        title: 'Target and Temporal Leakage', kind: 'flow',
        items: [
          ['Target proxy', 'A feature indirectly encodes the label, such as collections status for default.'],
          ['Future information', 'A feature window extends beyond the moment of prediction.'],
          ['Symptom', 'Suspiciously high performance that cannot survive real timing constraints.'],
        ],
        nodes: ['Past features', 'Prediction time', 'Future event', 'Leaked label'],
        notes: 'Audit feature availability at the exact decision timestamp.',
      },
      {
        title: 'Class Imbalance Distorts Training and Evaluation', kind: 'equation',
        items: [
          ['Evaluation', 'Accuracy can ignore near-total failure on a rare class.'],
          ['Training', 'The majority class dominates average empirical risk.'],
          ['Consequence', 'The fitted model learns that majority-favoring errors are cheap.'],
        ],
        formula: raw`\widehat R(\theta)=\frac1n\sum_i\ell(f_\theta(x_i),y_i)`,
        notes: 'Connect imbalance directly to the loss function, not only the metric.',
      },
      {
        title: 'Mitigation Has Tradeoffs', kind: 'cards',
        items: [
          ['Class weighting', 'Increase the loss contribution of minority examples.'],
          ['Resampling', 'Over-sample the minority or under-sample the majority.'],
          ['Threshold tuning', 'Move the operating point to favor recall or precision.'],
          ['Metrics', 'Report per-class precision, recall, and F1.'],
        ],
        notes: 'No mitigation is free; align its tradeoff with real error costs.',
      },
      {
        title: 'Before You Ship', kind: 'cards',
        items: [
          ['Preprocessing', 'Was every learned transform fit only on training data?'],
          ['Availability', 'Do all features exist at prediction time?'],
          ['Metric', 'Does it expose minority-class performance?'],
          ['Test discipline', 'Was the test set touched once, after decisions were fixed?'],
        ],
        notes: 'Present this as a reusable checklist for every course project.',
      },
      {
        title: 'Evaluation Can Fail Before the Metric', kind: 'summary',
        items: [
          ['Leakage', 'Breaks information boundaries.'],
          ['Imbalance', 'Hides and trains failure.'],
          ['Pipelines', 'Prevent common mistakes.'],
        ],
        next: 'Next: ensemble methods combine trees for stronger predictions.',
        notes: 'The setup must be sound before any metric or significance test is meaningful.',
      },
    ],
  },
)

const neural = 'Neural Networks and Deep Learning Basics'
decks.push(
  {
    subject: neural,
    title: 'Perceptrons and Multilayer Networks',
    subtitle: 'Familiar ingredients, composed into nonlinear models',
    seed: 810,
    slides: [
      {
        title: 'A Perceptron Is One Artificial Neuron', kind: 'equation',
        items: [
          ['Weighted sum', 'Combine the inputs exactly as in a linear model.'],
          ['Hard decision', 'A step function converts the score to 0 or 1.'],
          ['Close relative', 'Logistic regression uses the same score with a smooth sigmoid.'],
        ],
        formula: raw`z=w^\top x+b,\qquad \hat y=\mathbf1[z\ge0]`,
        notes: 'Run the hand-built AND gate and emphasize that the architecture is already familiar.',
      },
      {
        title: 'One Linear Boundary Cannot Solve XOR', kind: 'matrix',
        items: [
          ['Inputs', '00 and 11 map to 0; 01 and 10 map to 1.'],
          ['Geometry', 'The positive points occupy opposite corners.'],
          ['Limitation', 'No single line separates the two labels.'],
        ],
        notes: 'Invite students to draw a separating line before revealing why every attempt fails.',
      },
      {
        title: 'Hidden Layers Combine Several Boundaries', kind: 'network',
        items: [
          ['Hidden units', 'Each learns its own linear score and nonlinearity.'],
          ['Output unit', 'Combines learned intermediate features.'],
          ['Result', 'Even one hidden layer can carve out a nonlinear XOR region.'],
        ],
        formula: raw`h=\sigma(W_1x+b_1),\qquad \hat y=\sigma(W_2h+b_2)`,
        notes: 'Explain the two hidden half-planes and how the output combines them.',
      },
      {
        title: 'Without Activations, Depth Collapses', kind: 'equation',
        items: [
          ['Composition', 'A stack of linear maps is still one linear map.'],
          ['No extra capacity', 'More matrices alone cannot solve XOR.'],
          ['Essential ingredient', 'A nonlinearity between layers prevents collapse.'],
        ],
        formula: raw`W_2(W_1x)=(W_2W_1)x=W_{\mathrm{effective}}x`,
        notes: 'Use a numerical allclose check to make the algebra concrete.',
      },
      {
        title: 'Universal Approximation—with Important Caveats', kind: 'chart',
        items: [
          ['Existence', 'A wide enough hidden layer can approximate any continuous function on a bounded domain.'],
          ['Not a training guarantee', 'The theorem does not say gradient descent will find those weights.'],
          ['Not a generalization guarantee', 'Representing a function is not the same as learning it from finite data.'],
        ],
        chartLabels: ['2', '4', '8', '16', '32'],
        notes: 'Do not summarize this theorem as “networks can learn anything.”',
      },
      {
        title: 'Architecture Vocabulary', kind: 'network',
        items: [
          ['Input', 'Raw features; no learned transformation.'],
          ['Hidden layers', 'Linear maps plus nonlinear activations.'],
          ['Output', 'Sigmoid, softmax, or linear activation matched to the task.'],
          ['Capacity', 'Width counts units; depth counts learned layers.'],
        ],
        notes: 'Compute 20×64 + 64 parameters for one dense layer by hand.',
      },
      {
        title: 'Build the Network', kind: 'code',
        items: [
          ['Two hidden layers', 'ReLU creates nonlinear features.'],
          ['Binary output', 'Sigmoid returns a score in (0, 1).'],
        ],
        code: raw`import keras
from keras import layers

model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(64, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(1, activation="sigmoid"),
])
model.summary()`,
        notes: 'Map the code line by line to the architecture diagram.',
      },
      {
        title: 'From Architecture to Training', kind: 'summary',
        items: [
          ['Perceptron', 'One linear boundary.'],
          ['MLP', 'Compose nonlinear layers.'],
          ['Capacity', 'Width and depth matter.'],
        ],
        next: 'Next: backpropagation computes every network gradient efficiently.',
        notes: 'Architecture tells us how predictions flow forward; training remains unanswered.',
      },
    ],
  },
  {
    subject: neural,
    title: 'Backpropagation',
    subtitle: 'The chain rule, organized and reused at scale',
    seed: 830,
    slides: [
      {
        title: 'Forward Pass: Compute and Cache', kind: 'flow',
        items: [
          ['Layer calculation', 'Compute pre-activation z and activation a in order.'],
          ['Cache', 'Retain intermediate values for the backward pass.'],
          ['Memory cost', 'Training stores more than inference because gradients need those values.'],
        ],
        nodes: ['x = a⁰', 'z¹, a¹', 'z², a²', 'loss L'],
        formula: raw`z^{(l)}=W^{(l)}a^{(l-1)}+b^{(l)},\qquad a^{(l)}=\sigma(z^{(l)})`,
        notes: 'Inference can discard intermediates; training cannot.',
      },
      {
        title: 'Output-Layer Gradient', kind: 'equation',
        items: [
          ['Start at the loss', 'Differentiate with respect to the final activation.'],
          ['Local derivative', 'Multiply by the output activation derivative.'],
          ['Parameter gradients', 'Use the previous activation as the input to this layer.'],
        ],
        formula: raw`\delta^{(L)}=\frac{\partial L}{\partial a^{(L)}}\odot\sigma'(z^{(L)}),\quad \frac{\partial L}{\partial W^{(L)}}=\delta^{(L)}(a^{(L-1)})^\top`,
        notes: 'This is the single-neuron chain-rule example from calculus with layer notation.',
      },
      {
        title: 'Hidden-Layer Errors Propagate Recursively', kind: 'equation',
        items: [
          ['Downstream influence', 'A hidden unit contributes through every connected unit in the next layer.'],
          ['Transpose weights', 'Collect those downstream contributions.'],
          ['Local derivative', 'Multiply by this layer’s activation slope.'],
        ],
        formula: raw`\delta^{(l)}=((W^{(l+1)})^\top\delta^{(l+1)})\odot\sigma'(z^{(l)})`,
        notes: 'The matrix product contains the multivariable chain rule’s sum over downstream paths.',
      },
      {
        title: 'Forward, Then Backward', kind: 'network',
        items: [
          ['Forward', 'Inputs → activations → prediction → loss.'],
          ['Backward', 'Loss gradient → layer deltas → parameter gradients.'],
          ['Reuse', 'Each cached activation and each delta is computed once.'],
        ],
        notes: 'Use two colors for forward values and backward gradient flow.',
      },
      {
        title: 'A Two-Layer Backward Pass', kind: 'code',
        items: [
          ['Output first', 'Compute δ₂ from the loss.'],
          ['Then hidden', 'Reuse δ₂ to compute δ₁.'],
        ],
        code: raw`def backward(cache, y, W2):
    a1, a2 = cache["a1"], cache["a2"]
    delta2 = 2 * (a2 - y) * a2 * (1 - a2)
    dW2 = np.outer(delta2, a1)

    delta1 = (W2.T @ delta2) * a1 * (1 - a1)
    dW1 = np.outer(delta1, cache["x"])
    return dW1, dW2`,
        notes: 'Highlight the exact reuse of delta2 in the hidden-layer calculation.',
      },
      {
        title: 'Why Backpropagation Is Efficient', kind: 'compare',
        items: [
          ['Naive approach', 'Recompute shared paths separately for every weight.'],
          ['Backpropagation', 'Dynamic programming on the computation graph: reuse each local derivative.'],
          ['Scale', 'All gradients cost roughly one forward pass plus one backward pass.'],
        ],
        notes: 'This reuse is what makes millions or billions of parameters trainable.',
      },
      {
        title: 'Automatic Differentiation', kind: 'flow',
        items: [
          ['Record operations', 'Libraries construct a computation graph during the forward pass.'],
          ['Apply chain rule', 'Traverse the graph backward automatically.'],
          ['Same math', 'model.fit hides backpropagation; it does not replace it.'],
        ],
        nodes: ['Model code', 'Computation graph', 'Autodiff', 'Gradients'],
        notes: 'Emphasize that autodiff is the derived algorithm made general.',
      },
      {
        title: 'Backpropagation', kind: 'summary',
        items: [
          ['Forward', 'Compute and cache.'],
          ['Backward', 'Propagate δ recursively.'],
          ['Autodiff', 'Automates the graph traversal.'],
        ],
        next: 'Next: activation and initialization choices determine whether gradients flow well.',
        notes: 'Preview sigmoid saturation and vanishing gradients.',
      },
    ],
  },
  {
    subject: neural,
    title: 'Activation Functions and Initialization',
    subtitle: 'Small choices that decide whether deep training succeeds',
    seed: 850,
    slides: [
      {
        title: 'Sigmoid Saturates', kind: 'chart',
        items: [
          ['Derivative ceiling', 'σ′(z) ≤ 0.25 everywhere.'],
          ['Flat tails', 'Large |z| produces a derivative near zero.'],
          ['Deep product', 'Repeated small derivatives shrink early-layer gradients exponentially.'],
        ],
        chartLabels: ['−6', '−3', '0', '3', '6'],
        formula: raw`\sigma'(z)=\sigma(z)(1-\sigma(z)),\qquad \prod_{l=2}^L\sigma'(z^{(l)})\to0`,
        notes: 'Even best-case repeated multiplication by 0.25 vanishes quickly.',
      },
      {
        title: 'Tanh Helps, But Still Saturates', kind: 'equation',
        items: [
          ['Zero-centered', 'Outputs range from −1 to 1.'],
          ['Larger peak slope', 'The derivative reaches 1 near zero.'],
          ['Same tail problem', 'Large magnitudes still flatten the function.'],
        ],
        formula: raw`\begin{aligned}\tanh(z)&=2\sigma(2z)-1\\\tanh'(z)&=1-\tanh^2(z)\end{aligned}`,
        notes: 'Tanh is a rescaled sigmoid: better centered, not a complete cure.',
      },
      {
        title: 'ReLU Is the Modern Default', kind: 'equation',
        items: [
          ['Simple', 'One max operation.'],
          ['Positive side', 'Derivative is exactly 1, so it does not saturate there.'],
          ['Scale', 'Cheap enough for enormous numbers of activations.'],
        ],
        formula: raw`\mathrm{ReLU}(z)=\max(0,z),\qquad \mathrm{ReLU}'(z)=\mathbf1[z>0]`,
        notes: 'A simpler function became more effective precisely by removing saturation on one side.',
      },
      {
        title: 'Leaky ReLU Keeps a Recovery Path', kind: 'compare',
        items: [
          ['Dying ReLU', 'A unit that stays negative outputs zero and receives zero gradient forever.'],
          ['Leaky ReLU', 'A small negative-side slope keeps a nonzero gradient.'],
          ['Minimal fix', 'The tiny slope is enough to let a “dead” unit recover.'],
        ],
        formula: raw`f(z)=\begin{cases}z&z>0\\0.01z&z\le0\end{cases}`,
        notes: 'Tie permanent death directly to multiplying the backprop signal by zero.',
      },
      {
        title: 'Zero Initialization Preserves Bad Symmetry', kind: 'network',
        items: [
          ['Identical start', 'All units in a layer compute the same output.'],
          ['Identical gradient', 'Backprop updates them in exactly the same way.'],
          ['No specialization', 'Many neurons behave as one forever.'],
        ],
        notes: 'Random weights are needed to break symmetry, not for decorative randomness.',
      },
      {
        title: 'Match Random Scale to the Activation', kind: 'equation',
        items: [
          ['Xavier / Glorot', 'Stabilizes variance for tanh or sigmoid-like activations.'],
          ['He', 'Uses extra variance to account for ReLU zeroing about half its inputs.'],
          ['Goal', 'Keep activations and gradients from shrinking or exploding across depth.'],
        ],
        formula: raw`\operatorname{Var}(W_{\mathrm{Xavier}})\approx\frac{2}{n_{in}+n_{out}},\qquad \operatorname{Var}(W_{\mathrm{He}})=\frac{2}{n_{in}}`,
        notes: 'Initialization addresses unstable scale before the first training step happens.',
      },
      {
        title: 'Practical Pairings', kind: 'cards',
        items: [
          ['Hidden layers', 'ReLU or Leaky ReLU with He initialization.'],
          ['Binary output', 'Sigmoid.'],
          ['Multiclass output', 'Softmax.'],
          ['Regression output', 'Linear activation.'],
        ],
        notes: 'Keras defaults are sensible, but their rationale is now visible.',
      },
      {
        title: 'Make Gradients Flow', kind: 'summary',
        items: [
          ['Avoid saturation', 'Prefer ReLU-family hidden units.'],
          ['Break symmetry', 'Never initialize all weights equally.'],
          ['Control scale', 'Use Xavier or He.'],
        ],
        next: 'Next: CNNs and RNNs adapt these pieces to images and sequences.',
        notes: 'Activation and initialization work as a pair.',
      },
    ],
  },
  {
    subject: neural,
    title: 'CNNs and RNNs (Light Touch)',
    displayTitle: 'Convolutional and Recurrent Networks',
    subtitle: 'Specialized structure for images and sequences',
    seed: 870,
    slides: [
      {
        title: 'Dense Layers Ignore Image Structure', kind: 'compare',
        items: [
          ['Parameter explosion', '224×224×3 pixels feeding 1,000 units means about 150 million weights.'],
          ['Lost locality', 'Flattening does not tell a dense layer which pixels are neighbors.'],
          ['CNN response', 'Share small filters across nearby spatial regions.'],
        ],
        notes: 'Compute the parameter count aloud; spatial locality is the deeper motivation.',
      },
      {
        title: 'Convolution Shares a Local Filter', kind: 'matrix',
        items: [
          ['Small kernel', 'A learned 3×3 grid slides across the image.'],
          ['Weight sharing', 'The same nine weights detect a pattern everywhere.'],
          ['Feature maps', 'Different filters learn edges, textures, and shapes.'],
        ],
        formula: raw`Y_{ij}=\sum_{u,v}K_{uv}X_{i+u,j+v}`,
        notes: 'Weight sharing cuts parameters and encodes translation-aware pattern detection.',
      },
      {
        title: 'A Compact CNN', kind: 'code',
        items: [
          ['Convolve + pool', 'Extract and downsample spatial features.'],
          ['Flatten late', 'Preserve structure until learned features exist.'],
        ],
        code: raw`cnn = keras.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(32, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, 3, activation="relu"),
    layers.MaxPooling2D(2),
    layers.Flatten(),
    layers.Dense(10, activation="softmax"),
])`,
        notes: 'Trace height × width × channels through every layer.',
      },
      {
        title: 'RNNs Share Weights Across Time', kind: 'flow',
        items: [
          ['Ordered input', 'Text, time series, and audio depend on sequence.'],
          ['Hidden state', 'Carry a learned summary from earlier steps.'],
          ['Time sharing', 'Reuse the same transition weights at every position.'],
        ],
        nodes: ['x₁ → h₁', 'x₂ → h₂', 'x₃ → h₃', 'output'],
        formula: raw`h_t=\sigma(W_{hh}h_{t-1}+W_{xh}x_t+b_h)`,
        notes: 'Unroll the recurrent cell so the repeated structure becomes concrete.',
      },
      {
        title: 'Long Sequences Recreate Vanishing Gradients', kind: 'chart',
        items: [
          ['Backpropagation through time', 'The chain rule multiplies through many recurrent steps.'],
          ['Plain RNN', 'Long-range dependencies become hard to learn.'],
          ['LSTM / GRU', 'Gates create paths that preserve information and gradient flow.'],
        ],
        chartLabels: ['t', 't−5', 't−10', 't−25', 't−50'],
        notes: 'The mechanism matches vanishing gradients across depth; only the axis changed to time.',
      },
      {
        title: 'Choose Architecture From Data Structure', kind: 'cards',
        items: [
          ['Dense', 'Tabular data with no special spatial or sequential structure.'],
          ['CNN', 'Grid-like local structure: images and spectrograms.'],
          ['RNN / LSTM', 'Ordered, variable-length sequences.'],
          ['Beyond', 'Transformers increasingly dominate many sequence tasks.'],
        ],
        notes: 'The goal is architectural judgment, not a full convolution or LSTM derivation.',
      },
      {
        title: 'Same Machinery, Specialized Layout', kind: 'summary',
        items: [
          ['CNN', 'Share across space.'],
          ['RNN', 'Share across time.'],
          ['Both', 'Train with backpropagation.'],
        ],
        next: 'Next: batch normalization and dropout make deep training more reliable.',
        notes: 'The novelty is architectural structure; layers, activations, and gradients are unchanged.',
      },
    ],
  },
  {
    subject: neural,
    title: 'Practical Training Issues - Vanishing Gradients, Batch Norm, Dropout',
    displayTitle: 'Practical Training: Batch Normalization and Dropout',
    subtitle: 'Stabilize gradient flow and regularize deep networks',
    seed: 890,
    slides: [
      {
        title: 'Vanishing and Exploding Are One Product Problem', kind: 'chart',
        items: [
          ['Factors below one', 'Early-layer gradients vanish.'],
          ['Factors above one', 'Gradients explode and training diverges.'],
          ['Across depth or time', 'The same mechanism affects dense nets, CNNs, and RNNs.'],
        ],
        chartLabels: ['1', '5', '10', '15', '20 layers'],
        formula: raw`\delta^{(1)}\propto\prod_{l=2}^L (W^{(l)})^\top\sigma'(z^{(l)})`,
        notes: 'Unify both failure directions as repeated multiplication with unstable scale.',
      },
      {
        title: 'Batch Normalization Stabilizes Layer Inputs', kind: 'equation',
        items: [
          ['Normalize', 'Use mini-batch mean and variance.'],
          ['Restore flexibility', 'Learn scale γ and shift β.'],
          ['Analogy', 'Like StandardScaler, but inside the network at many layers.'],
        ],
        formula: raw`\hat z_i=\frac{z_i-\mu_B}{\sqrt{\sigma_B^2+\epsilon}},\qquad y_i=\gamma\hat z_i+\beta`,
        notes: 'Normalization stabilizes training but does not rigidly force the final learned distribution.',
      },
      {
        title: 'Batch Norm in a Network', kind: 'code',
        items: [
          ['Order', 'Dense → BatchNormalization → Activation.'],
          ['Benefit', 'More stable activations often permit larger learning rates.'],
        ],
        code: raw`model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(64),
    layers.BatchNormalization(),
    layers.Activation("relu"),
    layers.Dense(32),
    layers.BatchNormalization(),
    layers.Activation("relu"),
    layers.Dense(1, activation="sigmoid"),
])`,
        notes: 'Batch-dependent noise can add mild regularization, but stability is the primary purpose.',
      },
      {
        title: 'Dropout Trains Randomly Thinned Networks', kind: 'network',
        items: [
          ['Training', 'Randomly set a fraction of activations to zero each forward pass.'],
          ['Pressure', 'No narrow set of neurons can become indispensable.'],
          ['Inference', 'Use the full network; inverted dropout already handled scaling during training.'],
        ],
        formula: raw`\tilde a_j=\frac{m_j}{1-p}a_j,\qquad m_j\sim\mathrm{Bernoulli}(1-p)`,
        notes: 'Emphasize the unique train-versus-inference behavior.',
      },
      {
        title: 'Dropout Connects Regularization and Ensembling', kind: 'compare',
        items: [
          ['Regularization view', 'Random removal prevents brittle co-adaptation, like a structural constraint.'],
          ['Ensemble view', 'Each mask selects a different thinned subnetwork.'],
          ['Important caveat', 'Subnetworks share weights, so dropout is not literally bagging.'],
        ],
        notes: 'This is an informal but useful connection back to the ensemble unit.',
      },
      {
        title: 'A Complete Modern Dense Network', kind: 'code',
        items: [
          ['Stability', 'Batch normalization plus ReLU.'],
          ['Generalization', 'Dropout between learned blocks.'],
        ],
        code: raw`model = keras.Sequential([
    layers.Input(shape=(20,)),
    layers.Dense(128), layers.BatchNormalization(),
    layers.Activation("relu"), layers.Dropout(0.3),
    layers.Dense(64), layers.BatchNormalization(),
    layers.Activation("relu"), layers.Dropout(0.3),
    layers.Dense(1, activation="sigmoid"),
])`,
        notes: 'Have students identify which earlier lecture supplied each component.',
      },
      {
        title: 'Make Deep Networks Train and Generalize', kind: 'summary',
        items: [
          ['Scale', 'Control gradient products.'],
          ['Batch norm', 'Stabilize activations.'],
          ['Dropout', 'Regularize with random masks.'],
        ],
        next: 'Next: open the optimizer black box—SGD, momentum, RMSProp, and Adam.',
        notes: 'Close the neural-networks unit as architecture + gradients + practical stabilization.',
      },
    ],
  },
)

const optimization = 'Optimization in Practice'
decks.push(
  {
    subject: optimization,
    title: 'Gradient Descent Variants - SGD, Momentum, Adam',
    displayTitle: 'Gradient Descent Variants: SGD, Momentum, and Adam',
    subtitle: 'Make descent faster, smoother, and adaptive',
    seed: 910,
    slides: [
      {
        title: 'Plain SGD Zigzags', kind: 'chart',
        items: [
          ['Noisy gradient', 'A mini-batch estimates the full-data direction.'],
          ['Ill-conditioned surface', 'Steep and shallow axes need different effective step sizes.'],
          ['Result', 'Oscillation across the steep axis and slow progress along the shallow one.'],
        ],
        chartLabels: ['0', '5', '10', '20', '30 steps'],
        formula: raw`\theta_{t+1}=\theta_t-\alpha\nabla J(\theta_t)`,
        notes: 'Use elongated loss contours to make the zigzag visible.',
      },
      {
        title: 'Momentum Accumulates a Useful Direction', kind: 'equation',
        items: [
          ['Moving average', 'Blend the current gradient with recent history.'],
          ['Cancel oscillation', 'Alternating steep-axis gradients partially cancel.'],
          ['Reinforce progress', 'Consistent shallow-axis gradients accumulate.'],
        ],
        formula: raw`v_{t+1}=\beta v_t+(1-\beta)g_t,\qquad \theta_{t+1}=\theta_t-\alpha v_{t+1}`, 
        notes: 'β = 0.9 remembers roughly the recent ten gradients with geometrically decaying influence.',
      },
      {
        title: 'One Global Learning Rate Is a Compromise', kind: 'compare',
        items: [
          ['Large-gradient parameters', 'Need smaller effective steps to remain stable.'],
          ['Small-gradient parameters', 'Need larger effective steps to make progress.'],
          ['Adaptive goal', 'Learn a separate scale for every parameter from gradient history.'],
        ],
        notes: 'Momentum improves direction but still shares α across all parameters.',
      },
      {
        title: 'RMSProp Rescales by Squared Gradients', kind: 'equation',
        items: [
          ['Second moment', 'Track an exponential average of g² per parameter.'],
          ['Automatic scale', 'Large typical gradients get smaller steps; tiny ones get larger steps.'],
          ['Numerical guard', 'ε prevents division by zero.'],
        ],
        formula: raw`\begin{aligned}s_{t+1}&=\beta_2s_t+(1-\beta_2)g_t^2\\\theta_{t+1}&=\theta_t-\frac{\alpha g_t}{\sqrt{s_{t+1}}+\epsilon}\end{aligned}`,
        notes: 'RMSProp and momentum solve different problems with parallel moving-average machinery.',
      },
      {
        title: 'Adam Combines Both Ideas', kind: 'equation',
        items: [
          ['First moment m', 'Momentum-style average of gradients.'],
          ['Second moment v', 'RMSProp-style average of squared gradients.'],
          ['Bias correction', 'Compensate for both estimates starting at zero.'],
        ],
        formula: raw`\begin{aligned}\hat m_t&=m_t/(1-\beta_1^t),\quad \hat v_t=v_t/(1-\beta_2^t)\\\theta_{t+1}&=\theta_t-\alpha\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}\end{aligned}`,
        notes: 'Explain why the correction matters most in the earliest steps.',
      },
      {
        title: 'Adam Update in Code', kind: 'code',
        items: [
          ['Smooth', 'm carries direction.'],
          ['Adapt', 'v scales each coordinate.'],
        ],
        code: raw`m = np.zeros_like(theta)
v = np.zeros_like(theta)
for t in range(1, steps + 1):
    g = grad(theta)
    m = beta1 * m + (1 - beta1) * g
    v = beta2 * v + (1 - beta2) * g**2
    m_hat = m / (1 - beta1**t)
    v_hat = v / (1 - beta2**t)
    theta -= alpha * m_hat / (np.sqrt(v_hat) + eps)`,
        notes: 'Overlay SGD, momentum, RMSProp, and Adam paths on the same contours.',
      },
      {
        title: 'Practical Optimizer Choice', kind: 'cards',
        items: [
          ['Adam', 'Strong low-effort default for most neural-network training.'],
          ['SGD + momentum', 'Can generalize better on some well-studied tasks with careful schedules.'],
          ['Classical models', 'Prefer closed-form or specialized convex solvers when available.'],
          ['No universal winner', 'Optimizer performance remains problem dependent.'],
        ],
        notes: 'Adam is a robust default, not a theorem of universal superiority.',
      },
      {
        title: 'From SGD to Adam', kind: 'summary',
        items: [
          ['Momentum', 'Smooth direction.'],
          ['RMSProp', 'Adapt coordinate scale.'],
          ['Adam', 'Combine and correct bias.'],
        ],
        next: 'Next: tune every model hyperparameter systematically.',
        notes: 'Ask of any optimizer: which concrete failure of the previous one does it fix?',
      },
    ],
  },
  {
    subject: optimization,
    title: 'Hyperparameter Tuning Strategies',
    subtitle: 'Spend a fixed search budget where it teaches you the most',
    seed: 930,
    slides: [
      {
        title: 'Search Spaces Grow Combinatorially', kind: 'equation',
        items: [
          ['Interactions', 'The best learning rate can depend on batch size and regularization.'],
          ['Expensive trials', 'Each candidate may require a full cross-validated fit.'],
          ['Grid explosion', 'A few values across many dimensions become thousands of combinations.'],
        ],
        formula: raw`N_{\mathrm{configurations}}=v^h`,
        notes: 'Three choices across ten hyperparameters already means 59,049 configurations.',
      },
      {
        title: 'Grid Search Is the Exhaustive Baseline', kind: 'matrix',
        items: [
          ['Strength', 'Find the best point inside the stated grid.'],
          ['Weakness', 'Spend equal compute on promising and useless regions.'],
          ['Hidden cost', 'Configurations multiply again by the number of CV folds.'],
        ],
        notes: 'A 4 × 4 grid with five folds requires 80 model fits.',
      },
      {
        title: 'Random Search Covers Important Axes Better', kind: 'compare',
        items: [
          ['Grid', 'Repeats a small set of values along every axis.'],
          ['Random', 'Samples more distinct values of each parameter for the same trial budget.'],
          ['Why it wins', 'Often only a few hyperparameters strongly control performance.'],
        ],
        notes: 'Use the “only one axis matters” picture to make the advantage intuitive.',
      },
      {
        title: 'Sample Multiplicative Parameters on a Log Scale', kind: 'chart',
        items: [
          ['Orders of magnitude', '0.001 → 0.01 matters like 0.01 → 0.1.'],
          ['Linear sampling', 'Overrepresents the high end of a wide interval.'],
          ['Log-uniform', 'Gives each power-of-ten band equal attention.'],
        ],
        chartLabels: ['10⁻⁴', '10⁻³', '10⁻²', '10⁻¹', '1'],
        formula: raw`\log_{10}h\sim\mathcal U(-4,0)`,
        notes: 'Learning rate, C, gamma, and regularization strength are common log-scale candidates.',
      },
      {
        title: 'RandomizedSearchCV', kind: 'code',
        items: [
          ['Fixed budget', 'n_iter controls the number of configurations.'],
          ['Distributions', 'Describe ranges instead of enumerating every point.'],
        ],
        code: raw`from scipy.stats import loguniform
from sklearn.model_selection import RandomizedSearchCV

search = RandomizedSearchCV(
    SVC(),
    {"C": loguniform(1e-2, 1e2),
     "gamma": loguniform(1e-4, 1)},
    n_iter=20, cv=5, random_state=0,
)
search.fit(X, y)`,
        notes: 'One hundred fits here regardless of how finely the distributions could be sampled.',
      },
      {
        title: 'Bayesian Optimization Learns From Trials', kind: 'flow',
        items: [
          ['Surrogate model', 'Estimate performance and uncertainty across the search space.'],
          ['Acquisition', 'Choose the next candidate where promise or uncertainty is high.'],
          ['Tradeoff', 'Fewer expensive trials at the cost of a more complex search algorithm.'],
        ],
        nodes: ['Evaluate', 'Update surrogate', 'Choose next', 'Evaluate'],
        notes: 'Keep the treatment conceptual; recognize the method and its value proposition.',
      },
      {
        title: 'A Practical Broad-to-Narrow Workflow', kind: 'flow',
        items: [
          ['Start broad', 'Random search over wide, sensible ranges.'],
          ['Narrow', 'Refine around promising regions.'],
          ['Lock decisions', 'Select the final configuration with validation or CV.'],
          ['Test once', 'Use the untouched test set only at the end.'],
        ],
        nodes: ['Wide random search', 'Focused search', 'Final model', 'One test'],
        notes: 'The strategy never relaxes train/validation/test discipline.',
      },
      {
        title: 'Tune Systematically', kind: 'summary',
        items: [
          ['Budget', 'Count evaluations.'],
          ['Scale', 'Use log ranges when appropriate.'],
          ['Discipline', 'Never tune on test.'],
        ],
        next: 'Next: broader context—fairness, interpretability, and responsible deployment.',
        notes: 'These methods apply to every hyperparameter encountered in the course.',
      },
    ],
  },
)

const broader = 'Broader Context'
decks.push(
  {
    subject: broader,
    title: 'Fairness, Bias, and Interpretability',
    subtitle: 'Ask what a model does, why, and to whom',
    seed: 1010,
    slides: [
      {
        title: 'Bias Can Enter at Every Stage', kind: 'flow',
        items: [
          ['Data bias', 'Historical inequity or underrepresentation becomes the pattern to learn.'],
          ['Label bias', 'Past human decisions may encode discrimination.'],
          ['Measurement bias', 'Features and proxies can track protected attributes indirectly.'],
        ],
        nodes: ['Data', 'Labels', 'Features', 'Model decision'],
        notes: 'ERM has no intrinsic fairness objective; it can faithfully reproduce an unfair data-generating process.',
      },
      {
        title: 'Three Group Fairness Definitions', kind: 'cards',
        items: [
          ['Demographic parity', 'Equal positive prediction rates across groups.'],
          ['Equalized odds', 'Equal true-positive and false-positive rates across groups.'],
          ['Predictive parity', 'Equal precision across groups.'],
          ['Audit method', 'Compute familiar evaluation metrics separately within each group.'],
        ],
        notes: 'Fairness auditing extends confusion-matrix analysis by slicing on group membership.',
      },
      {
        title: 'Fairness Metrics Can Be Mutually Incompatible', kind: 'equation',
        items: [
          ['Impossibility result', 'When group base rates differ and prediction is imperfect, common definitions cannot all hold.'],
          ['Not an engineering bug', 'No better optimizer removes the mathematical conflict.'],
          ['Value judgment', 'The application and affected stakeholders must determine which harms matter most.'],
        ],
        formula: raw`\begin{aligned}\text{unequal base rates}+\text{imperfect prediction}\\\Longrightarrow\ \text{fairness tradeoffs}\end{aligned}`, 
        notes: 'Fairness is not one scalar objective waiting to be optimized.',
      },
      {
        title: 'Individual and Group Fairness Can Conflict', kind: 'compare',
        items: [
          ['Individual fairness', 'Treat similar individuals similarly.'],
          ['Hard question', 'Defining “similar” requires a value-laden distance metric.'],
          ['Tension', 'Meeting a group statistic can require different treatment for otherwise similar cases.'],
        ],
        notes: 'Connect the similarity metric to k-NN and clustering, now with real stakes.',
      },
      {
        title: 'Interpretability Has Global and Local Forms', kind: 'compare',
        items: [
          ['Global', 'Understand overall model behavior: coefficients or a small decision tree.'],
          ['Local', 'Explain one prediction even when the whole model is too complex to summarize.'],
          ['Why it matters', 'Debugging, trust, compliance, and fairness audits.'],
        ],
        notes: 'Place course models on a spectrum from linear models and trees to forests and neural networks.',
      },
      {
        title: 'SHAP Explains One Prediction Additively', kind: 'chart',
        items: [
          ['Baseline', 'Start at the model’s average prediction.'],
          ['Feature contributions', 'Each feature pushes this case up or down.'],
          ['Local sum', 'Contributions add to the final prediction.'],
        ],
        chartLabels: ['baseline', 'income', 'debt', 'history', 'final'],
        notes: 'Contrast local SHAP values with global random-forest feature importance; neither establishes causality.',
      },
      {
        title: 'Fairness and Interpretability', kind: 'summary',
        items: [
          ['Audit sources', 'Data, labels, proxies.'],
          ['Choose values', 'Definitions conflict.'],
          ['Explain', 'Use global and local tools.'],
        ],
        next: 'Next: distribution shift, feedback loops, adversarial inputs, and misuse.',
        notes: 'The goal is informed scrutiny, not a single universal fairness formula.',
      },
    ],
  },
  {
    subject: broader,
    title: 'Ethical Considerations and Failure Modes',
    subtitle: 'Anticipate how deployed systems can fail and cause harm',
    seed: 1030,
    slides: [
      {
        title: 'Distribution Shift Breaks the i.i.d. Assumption', kind: 'chart',
        items: [
          ['Training world', 'Validation assumes future observations resemble past data.'],
          ['Deployment world', 'Populations, behavior, or upstream collection can change.'],
          ['Silent failure', 'The system keeps returning confident predictions as accuracy decays.'],
        ],
        chartLabels: ['train', 'launch', 'month 2', 'month 4', 'month 6'],
        notes: 'Monitoring is an ongoing process, not a one-time validation checkbox.',
      },
      {
        title: 'Feedback Loops Change the Data Being Predicted', kind: 'flow',
        items: [
          ['Prediction', 'The model influences a real decision.'],
          ['Action', 'The decision changes what gets observed.'],
          ['Retraining', 'New, intervention-shaped data becomes the next training set.'],
          ['Amplification', 'Small initial bias can grow across cycles.'],
        ],
        nodes: ['Prediction', 'Decision', 'Observed data', 'Retrain ↻'],
        notes: 'Cross-validation inside one static dataset cannot detect a multi-cycle feedback loop.',
      },
      {
        title: 'Confidently Wrong at the Edges', kind: 'compare',
        items: [
          ['Adversarial input', 'A deliberately small perturbation flips a prediction.'],
          ['Out of distribution', 'An unfamiliar input is forced into one of the known classes.'],
          ['Safety implication', 'Critical systems need detection, fallback, and human-review paths.'],
        ],
        notes: 'Softmax normalizes over known classes; it does not create a built-in “none of the above.”',
      },
      {
        title: 'Dual-Use Capabilities', kind: 'compare',
        items: [
          ['Beneficial use', 'Accessibility, diagnosis support, fraud detection, creative assistance.'],
          ['Harmful use', 'Surveillance, manipulation, discriminatory screening, disinformation.'],
          ['Design responsibility', 'Consider foreseeable misuse, not only intended use.'],
        ],
        notes: 'Treat misuse analysis like security threat modeling: a routine design practice.',
      },
      {
        title: 'A Human-Centered Deployment Checklist', kind: 'cards',
        items: [
          ['Affected people', 'Who bears the consequences, and did they have input?'],
          ['Error costs', 'Who pays for false positives and false negatives?'],
          ['Monitoring', 'How will shift and feedback be detected after launch?'],
          ['Appeal', 'Can a person contest or obtain human review of a decision?'],
        ],
        notes: 'Combine this with the technical leakage/imbalance checklist from model evaluation.',
      },
      {
        title: 'Failure-Mode Thinking', kind: 'summary',
        items: [
          ['Shift', 'The world changes.'],
          ['Loops', 'Predictions change the world.'],
          ['Edges and misuse', 'Inputs and intent matter.'],
        ],
        next: 'Next: place classical ML and modern deep learning in one map.',
        notes: 'Build a repeatable “what could go wrong?” habit before deployment.',
      },
    ],
  },
  {
    subject: broader,
    title: 'Where Classical ML Ends and Modern Deep Learning Begins',
    subtitle: 'Choose tools from the problem—not from fashion',
    seed: 1050,
    slides: [
      {
        title: 'The Boundary Is Fuzzy', kind: 'compare',
        items: [
          ['Classical ML', 'Regression, trees, SVMs, ensembles, clustering, PCA—with comparatively compact models.'],
          ['Deep learning', 'Composed neural networks with learned representations and large parameter counts.'],
          ['Convention, not theorem', 'A shallow neural net and logistic regression already share structure.'],
        ],
        notes: 'Do not present classical methods as disposable prerequisites for “real” ML.',
      },
      {
        title: 'When Classical ML Is Often Better', kind: 'cards',
        items: [
          ['Tabular data', 'Boosted trees and forests remain formidable defaults.'],
          ['Small datasets', 'Lower-capacity methods need fewer examples.'],
          ['Interpretability', 'Linear models and trees can be easier to justify.'],
          ['Limited compute', 'Training and serving are usually much cheaper.'],
        ],
        notes: 'Many day-to-day industry problems are structured data problems.',
      },
      {
        title: 'Where Deep Learning Changed the Landscape', kind: 'chart',
        items: [
          ['Unstructured input', 'Images, audio, and text benefit from learned representations.'],
          ['Scale', 'Large networks can keep improving with much more data and compute.'],
          ['Less manual feature engineering', 'Useful representations emerge from raw input.'],
        ],
        chartLabels: ['small data', '', 'medium', '', 'large data'],
        notes: 'Present the scale curve as a domain-dependent pattern, not a universal law.',
      },
      {
        title: 'A Practical Choice Map', kind: 'flow',
        items: [
          ['Data structure', 'Tabular or unstructured?'],
          ['Data volume', 'Enough examples for a high-capacity model?'],
          ['Constraints', 'Interpretability, latency, budget, and maintenance.'],
        ],
        nodes: ['Problem', 'Data + scale', 'Constraints', 'Model family'],
        notes: 'The strongest method is the one that fits the full operating context.',
      },
      {
        title: 'The Mathematical Foundations Do Not Change', kind: 'flow',
        items: [
          ['Linear algebra', 'Data, representations, and transformations.'],
          ['Probability and statistics', 'Uncertainty, likelihood, and evaluation.'],
          ['Calculus', 'Gradients and the chain rule.'],
          ['Methodology', 'Generalization, validation, and careful measurement.'],
        ],
        nodes: ['Foundations', 'Classical ML', 'Deep learning', 'Future models'],
        notes: 'New architectures add structure and scale; they do not replace the semester’s mathematical core.',
      },
      {
        title: 'One Field, Many Useful Tools', kind: 'summary',
        items: [
          ['Classical', 'Strong on tabular and small data.'],
          ['Deep', 'Strong on unstructured data at scale.'],
          ['Foundations', 'Transfer to both.'],
        ],
        next: 'Next: the capstone applies the complete pipeline independently.',
        notes: 'Close the technical curriculum by validating the entire toolkit.',
      },
    ],
  },
)

decks.push({
  subject: 'Capstone - Project Time',
  title: 'End-to-End Project Guide',
  displayTitle: 'Capstone Project: An End-to-End ML Pipeline',
  subtitle: 'Integrate the whole semester into one defensible project',
  seed: 1110,
  slides: [
    {
      title: 'Choose a Clear, Feasible Problem', kind: 'cards',
      items: [
        ['Target', 'Regression for continuous outcomes; classification for discrete labels.'],
        ['Scale', 'Enough rows for honest splits, small enough for fast iteration.'],
        ['Interest', 'Domain curiosity improves feature engineering and error analysis.'],
        ['Success', 'State in one sentence what a useful model would accomplish.'],
      ],
      notes: 'Structured tabular data is the safest scope for this course capstone.',
    },
    {
      title: 'Stage 1 — EDA and Cleaning', kind: 'code',
      items: [
        ['Understand', 'Shape, types, missingness, duplicates, and outliers.'],
        ['Investigate', 'Suspiciously perfect target relationships may signal leakage.'],
      ],
      code: raw`df = pd.read_csv("project_data.csv")
df.info()
print(df.describe())
print(df.isna().sum())
print("duplicates:", df.duplicated().sum())

target_corr = df.corr(numeric_only=True)["target"]
print(target_corr.sort_values(ascending=False))`,
      notes: 'Document cleaning decisions; do not silently mutate the dataset.',
    },
    {
      title: 'Stage 2 — Split, Then Preprocess', kind: 'flow',
      items: [
        ['Split first', 'Create train, validation, and test boundaries before learned preprocessing.'],
        ['Pipeline', 'Fit imputers, encoders, and scalers only on training folds.'],
        ['Feature engineering', 'Use domain knowledge without peeking at held-out outcomes.'],
      ],
      nodes: ['Raw data', 'Train / val / test', 'Pipeline fit on train', 'Transform held-out'],
      notes: 'This is the capstone’s non-negotiable leakage boundary.',
    },
    {
      title: 'Stage 3 — Establish a Baseline', kind: 'compare',
      items: [
        ['Dummy baseline', 'What does a trivial mean or majority prediction achieve?'],
        ['Simple model', 'Try linear or logistic regression before complex learners.'],
        ['Earn complexity', 'A forest or boosted model should improve enough to justify itself.'],
      ],
      notes: 'Without a baseline, a seemingly high score has no useful context.',
    },
    {
      title: 'Compare Models With Cross-Validation', kind: 'code',
      items: [
        ['Same folds', 'Create paired performance estimates across candidates.'],
        ['Right metric', 'Use F1, ROC-AUC, or a regression metric matched to the problem.'],
      ],
      code: raw`models = {
    "baseline": DummyClassifier(strategy="most_frequent"),
    "logistic": LogisticRegression(max_iter=1000),
    "forest": RandomForestClassifier(random_state=42),
    "boosting": GradientBoostingClassifier(random_state=42),
}
for name, model in models.items():
    score = cross_val_score(model, X_train, y_train,
                            cv=5, scoring="f1")
    print(name, score.mean(), score.std())`,
      notes: 'Tune promising candidates with the broad-to-narrow search workflow.',
    },
    {
      title: 'Stage 4 — Rigorous Evaluation', kind: 'matrix',
      items: [
        ['Metrics', 'Choose based on real false-positive and false-negative costs.'],
        ['Error analysis', 'Inspect the confusion matrix or residual plots.'],
        ['Robustness', 'Check imbalance, leakage, and plausible distribution shift.'],
        ['Test set', 'Touch it once after every modeling choice is locked.'],
      ],
      notes: 'Write the final test evaluation once and accept the result.',
    },
    {
      title: 'Stage 5 — Interpret and Write Honestly', kind: 'cards',
      items: [
        ['Explain', 'Feature importance or SHAP should agree with domain sense.'],
        ['Limitations', 'Name populations, conditions, and inputs the model does not cover.'],
        ['Consequences', 'Discuss costs, fairness, monitoring, and appeal.'],
        ['Narrative', 'Problem → evidence → choices → results → limitations.'],
      ],
      notes: 'A strong report is more than a leaderboard score.',
    },
    {
      title: 'The Complete Pipeline', kind: 'flow',
      items: [
        ['Integrate', 'Every stage maps to an earlier course unit.'],
        ['Be disciplined', 'Information boundaries and evaluation methodology hold the project together.'],
        ['Exercise judgment', 'The capstone is intentionally less prescribed than homework.'],
      ],
      nodes: ['EDA', 'Split + features', 'Model + tune', 'Evaluate + explain'],
      notes: 'Walk the pipeline once more and name the earlier lecture supporting each stage.',
    },
    {
      title: 'Final Course Takeaways', kind: 'summary',
      items: [
        ['Foundations', 'Math transfers.'],
        ['Method', 'Validate honestly.'],
        ['Responsibility', 'Consider real consequences.'],
      ],
      next: 'Build one complete, clear, reproducible project—and tell the truth about what it can and cannot do.',
      notes: 'Close on durable habits rather than any single algorithm.',
    },
  ],
})

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

function itemCards(items, columns = 2) {
  return `<div class="grid grid-cols-${columns} gap-4 mt-6">
${items.map(([label, text], index) => `<div v-click border="2 solid ${['teal', 'blue', 'amber', 'violet'][index % 4]}-800" bg="${['teal', 'blue', 'amber', 'violet'][index % 4]}-800/20" rounded-lg p-4>
<div class="font-bold text-${['teal', 'blue', 'amber', 'violet'][index % 4]}-300 mb-2">${escapeHtml(label)}</div>
<div class="text-sm leading-relaxed opacity-90">${escapeHtml(text)}</div>
</div>`).join('\n')}
</div>`
}

function compactItems(items) {
  return `<div class="space-y-3 mt-4">
${items.map(([label, text], index) => `<div v-click border="2 solid white/5" bg="white/5" rounded-lg px-4 py-3>
<span class="font-bold text-${['teal', 'blue', 'amber', 'violet'][index % 4]}-300">${escapeHtml(label)}</span>
<span class="text-sm opacity-85"> — ${escapeHtml(text)}</span>
</div>`).join('\n')}
</div>`
}

function formulaBlock(formula) {
  if (!formula) return ''
  return `<div v-click class="mt-4" style="font-size: .9em" border="2 solid teal-800" bg="teal-800/20" rounded-lg px-4 py-3>

$$
${formula}
$$

</div>`
}

function flowVisual(nodes) {
  return `<div class="mt-5" role="img" aria-label="${escapeHtml(nodes.join(' then '))}">
${nodes.map((node, index) => `<div v-click class="flex items-center gap-3">
<div class="w-8 h-8 rounded-full bg-${['teal', 'blue', 'amber', 'violet'][index % 4]}-500/20 border-2 border-${['teal', 'blue', 'amber', 'violet'][index % 4]}-700 flex items-center justify-center text-sm font-bold">${index + 1}</div>
<div class="flex-1 rounded-lg border-2 border-white/10 bg-white/5 px-3 py-2 text-sm font-bold">${escapeHtml(node)}</div>
</div>`).join('\n<div class="ml-4 h-1 border-l-2 border-teal-400/50"></div>\n')}
</div>`
}

function networkVisual(title) {
  return `<svg role="img" aria-label="Network diagram for ${escapeHtml(title)}" viewBox="0 0 440 290" class="w-full max-w-xl mx-auto mt-8">
  <g stroke="#475569" stroke-width="2" opacity=".75">
    <line x1="70" y1="75" x2="190" y2="55"/><line x1="70" y1="75" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="145"/><line x1="70" y1="215" x2="190" y2="235"/>
    <line x1="190" y1="55" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="95"/><line x1="190" y1="145" x2="315" y2="195"/><line x1="190" y1="235" x2="315" y2="195"/>
    <line x1="315" y1="95" x2="405" y2="145"/><line x1="315" y1="195" x2="405" y2="145"/>
  </g>
  <g fill="#0f172a" stroke-width="4"><circle cx="70" cy="75" r="22" stroke="#60a5fa"/><circle cx="70" cy="215" r="22" stroke="#60a5fa"/><circle cx="190" cy="55" r="22" stroke="#2dd4bf"/><circle cx="190" cy="145" r="22" stroke="#2dd4bf"/><circle cx="190" cy="235" r="22" stroke="#2dd4bf"/><circle cx="315" cy="95" r="22" stroke="#f59e0b"/><circle cx="315" cy="195" r="22" stroke="#f59e0b"/><circle cx="405" cy="145" r="24" stroke="#a78bfa"/></g>
  <g fill="#cbd5e1" style="font-size: 13px" text-anchor="middle"><text x="70" y="265">input</text><text x="190" y="275">hidden / diverse</text><text x="315" y="245">combine</text><text x="405" y="185">output</text></g>
</svg>`
}

function chartVisual(slide) {
  const labels = slide.chartLabels || ['A', 'B', 'C', 'D', 'E']
  return `<svg role="img" aria-label="Conceptual chart for ${escapeHtml(slide.title)}" viewBox="0 0 500 310" class="w-full max-w-xl mx-auto mt-7">
  <line x1="55" y1="260" x2="470" y2="260" stroke="#64748b" stroke-width="2"/><line x1="55" y1="35" x2="55" y2="260" stroke="#64748b" stroke-width="2"/>
  <path d="M60 235 C130 210,145 70,220 100 S320 210,465 55" fill="none" stroke="#2dd4bf" stroke-width="5"/>
  <path d="M60 245 C135 230,205 195,270 165 S385 110,465 95" fill="none" stroke="#60a5fa" stroke-width="4" stroke-dasharray="9 7"/>
  <g fill="#f59e0b">${[0, 1, 2, 3, 4].map((_, i) => `<circle cx="${65 + i * 98}" cy="${[230, 185, 110, 150, 65][i]}" r="6"/>`).join('')}</g>
  <g fill="#cbd5e1" style="font-size: 12px" text-anchor="middle">${labels.slice(0, 5).map((label, i) => `<text x="${65 + i * 98}" y="285">${escapeHtml(label)}</text>`).join('')}</g>
  <g style="font-size: 12px"><text x="335" y="42" fill="#5eead4">primary signal</text><text x="335" y="82" fill="#93c5fd">comparison</text></g>
</svg>`
}

function matrixVisual(title) {
  return `<div role="img" aria-label="Two by two matrix for ${escapeHtml(title)}" class="mt-8 max-w-lg mx-auto">
<div class="grid grid-cols-[6rem_1fr_1fr] gap-2 text-center text-sm">
<div></div><div class="font-bold text-blue-300">Column A</div><div class="font-bold text-blue-300">Column B</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Row A</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">✓</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">×</div>
<div class="flex items-center justify-end pr-2 font-bold text-teal-300">Row B</div><div border="2 solid red-800" bg="red-800/20" rounded-lg p-5 class="text-2xl font-bold">×</div><div border="2 solid teal-800" bg="teal-800/20" rounded-lg p-5 class="text-2xl font-bold">✓</div>
</div>
</div>`
}

function renderSlide(slide, seed) {
  const notes = `<!--\n${slide.notes}\n-->`
  const heading = `---\nglowSeed: ${seed}\n---\n\n# ${slide.title}\n`

  if (slide.kind === 'summary') {
    return `${heading}\n<div class="mt-8">${itemCards(slide.items, 3)}</div>\n\n<div v-click class="mt-10 text-center text-lg" border="2 solid white/10" bg="white/5" rounded-lg px-6 py-4>${escapeHtml(slide.next)}</div>\n\n${notes}`
  }
  if (slide.kind === 'cards' || slide.kind === 'compare') {
    const columns = slide.items.length === 3 ? 3 : 2
    return `${heading}\n${itemCards(slide.items, columns)}\n${formulaBlock(slide.formula)}\n\n${notes}`
  }
  if (slide.kind === 'code') {
    return `${heading}\n${itemCards(slide.items, 2)}\n\n\`\`\`python\n${slide.code}\n\`\`\`\n\n${notes}`
  }

  let visual = ''
  if (slide.kind === 'flow') visual = flowVisual(slide.nodes)
  else if (slide.kind === 'network') visual = networkVisual(slide.title)
  else if (slide.kind === 'chart') visual = chartVisual(slide)
  else if (slide.kind === 'matrix') visual = matrixVisual(slide.title)

  return `${heading}\n<div class="grid grid-cols-2 gap-8 items-start">\n<div>\n${compactItems(slide.items)}\n</div>\n<div>\n${visual || formulaBlock(slide.formula)}\n${visual ? formulaBlock(slide.formula) : ''}\n</div>\n</div>\n\n${notes}`
}

function renderDeck(deck) {
  const title = deck.displayTitle || deck.title
  const headmatter = `---
theme: default
highlighter: shiki
css: unocss
colorSchema: dark
title: '${title.replaceAll("'", "''")}'
info: |
  ## ${title}
  ${deck.subtitle}
class: text-center
transition: fade-out
lineNumbers: false
drawings:
  persist: false
mdc: true
vite:
  server:
    fs:
      strict: false
glowSeed: ${deck.seed}
---

# ${title}

### ${deck.subtitle}

<div class="pt-8 opacity-80 text-lg">${deck.subject} · Foundations of Machine Learning</div>

<div class="mt-14 flex justify-center gap-4" aria-hidden="true">
<div class="w-28 h-3 rounded-full bg-teal-400/70"></div>
<div class="w-20 h-3 rounded-full bg-blue-400/60"></div>
<div class="w-14 h-3 rounded-full bg-violet-400/50"></div>
</div>

<!--
Introduce the topic, connect it to the preceding unit, and preview the progression of ideas in this deck.
-->`

  return [headmatter, ...deck.slides.map((slide, index) => renderSlide(slide, deck.seed + index + 1))].join('\n\n') + '\n'
}

function slug(value) {
  return value.toLowerCase().replaceAll('&', 'and').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

function writeDeck(deck) {
  const root = join(deck.subject, 'Presentations', deck.title)
  mkdirSync(join(deck.subject, 'assignments'), { recursive: true })
  mkdirSync(join(root, 'setup'), { recursive: true })

  writeFileSync(join(root, 'slides.md'), renderDeck(deck))
  writeFileSync(join(root, 'package.json'), `${JSON.stringify({
    name: slug(deck.title),
    type: 'module',
    private: true,
    scripts: {
      dev: 'PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev --open',
      build: 'PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev build',
      export: 'PATH=/opt/homebrew/opt/node@20/bin:$PATH ../../../slidev_template/node_modules/.bin/slidev export',
    },
  }, null, 2)}\n`)
  writeFileSync(join(root, 'global-bottom.vue'), `<script setup lang="ts">\nimport TemplateBottom from '../../../slidev_template/global-bottom.vue'\n</script>\n\n<template>\n  <TemplateBottom />\n</template>\n`)
  writeFileSync(join(root, 'style.css'), `@import '../../../slidev_template/style.css';\n`)
  writeFileSync(join(root, 'uno.config.ts'), `export { default } from '../../../slidev_template/uno.config'\n`)
  writeFileSync(join(root, 'setup', 'main.ts'), `export { default } from '../../../../slidev_template/setup/main'\n`)
  writeFileSync(join(root, 'vite.config.ts'), `import { fileURLToPath } from 'node:url'\n\nconst deckRoot = fileURLToPath(new URL('.', import.meta.url))\nconst templateRoot = fileURLToPath(new URL('../../../slidev_template', import.meta.url))\n\nexport default {\n  server: {\n    fs: { allow: [deckRoot, templateRoot] },\n  },\n}\n`)
  return root
}

for (const deck of decks)
  console.log(writeDeck(deck))

console.log(`Generated ${decks.length} decks.`)
