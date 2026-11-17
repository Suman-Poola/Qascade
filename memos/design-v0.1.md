# Qascade v0.1 design

This is the build specification for the first release. It fixes module boundaries and public
interfaces so that parts can be built and tested independently. Anything not fixed here is the
implementer's call, logged in `DECISIONS.md`.

## 1. What the package is

Friedman-style functional gradient boosting where each weak learner is a small parameterised
quantum circuit, by default a few-qubit quantum convolutional neural network (QCNN):

```
F_0(x)   = argmin_c  sum_i L(y_i, c)
r_i      = -dL(y_i, F)/dF  at F = F_{m-1}(x_i)          pseudo-residuals
h_m      = weak learner fitted to (x_i, r_i) by least squares, on a row and feature subsample
gamma_m  = argmin_g  sum_i L(y_i, F_{m-1}(x_i) + g * h_m(x_i))   line search
F_m(x)   = F_{m-1}(x) + nu * gamma_m * h_m(x)
```

Five lines for a new user:

```python
from qascade import BoostedQCNNClassifier
from sklearn.datasets import make_moons
X, y = make_moons(200, noise=0.2, random_state=0)
model = BoostedQCNNClassifier(n_estimators=10, random_state=0).fit(X, y)
print(model.score(X, y))
```

## 2. What is new here (keep these intact)

1. **Loss-driven gradient boosting of circuits.** Pseudo-residuals for squared, absolute, Huber,
   logistic, multinomial and user-defined losses. Prior quantum work uses AdaBoost reweighting or
   squared-error residuals only.
2. **Bounded-output handling.** An expectation value lies in [-1, 1]; residuals do not. Each
   learner standardises its target, and fits a closed-form affine readout; the booster then does a
   per-stage line search.
3. **Random feature subspaces.** A q-qubit learner sees a random subset of at most q features per
   stage, so a d-feature problem never needs d qubits. This also gives `feature_importances_`.
4. **Zero-cost corrective step.** Learner outputs on the training rows are cached, so all stage
   weights can be re-optimised jointly on a classical computer with no further circuit executions.
5. **Budget accounting.** Every expectation value and gradient is counted in hardware-equivalent
   circuit executions; `max_circuit_executions` stops boosting when a budget is spent.
6. **A fast exact engine and a primitives engine behind one interface.** A built-in NumPy
   statevector simulator with adjoint gradients for development speed; any Qiskit
   `BaseEstimatorV2` (reference, Aer, fake-backend noise, IBM Runtime) for everything else.

## 3. Layout

```
src/qascade/
  __init__.py        public API re-exports
  _version.py
  exceptions.py      QascadeError, NotSupportedError, BudgetExceededError (plain subclasses)
  losses.py          loss functions                                   (pure NumPy/SciPy)
  optimizers.py      Adam, SPSA, SciPy wrapper                        (pure NumPy/SciPy)
  circuits.py        feature maps, QCNN ansatz, observables           (Qiskit only)
  execution/
    __init__.py      re-exports
    _base.py         ExpectationEngine, CompiledCircuit, ResourceUsage
    _analysis.py     circuit analysis shared by both engines (gate -> affine angle map)
    _statevector.py  StatevectorEngine (built-in NumPy simulator, adjoint gradients)
    _primitive.py    PrimitiveEngine (BaseEstimatorV2, batched parameter shift)
  learners.py        CircuitRegressor, QCNNRegressor (sklearn regressors)
  boosting.py        BoostedQCNNRegressor, BoostedQCNNClassifier
  serialization.py   save_model, load_model
tests/               mirrors the modules: test_losses.py, test_optimizers.py, ...
```

Dependencies: `numpy`, `scipy`, `scikit-learn>=1.6`, `joblib`, `qiskit>=2.0`. `qiskit-aer` and
`qiskit-ibm-runtime` are optional extras and must only be imported inside tests or lazily.

## 4. `qascade.execution`

```python
@dataclass
class ResourceUsage:
    expectation_evaluations: int = 0   # (parameter set, observable) values requested
    gradient_evaluations: int = 0      # per-sample gradients requested
    circuit_executions: int = 0        # hardware-equivalent: expectations + 2 * shifted gates per gradient sample
    def __add__ / __iadd__ / copy / as_dict

class CompiledCircuit(ABC):
    """One circuit + one observable, ready for repeated evaluation."""
    parameters: tuple[Parameter, ...]          # column order of `values`
    num_parameters: int
    usage: ResourceUsage                       # running total for this object
    def expectation(self, values: NDArray[float64]) -> NDArray[float64]:
        """values: (n, P) -> (n,) expectation values."""
    def value_and_gradient(self, values, wrt: Sequence[int]) -> tuple[NDArray, NDArray]:
        """values: (n, P) -> ((n,), (n, len(wrt))): d<O>/d(parameter column) for the columns in `wrt`."""
    supports_gradient: bool

class ExpectationEngine(ABC):
    def compile(self, circuit: QuantumCircuit, observable: SparsePauliOp,
                parameters: Sequence[Parameter] | None = None) -> CompiledCircuit: ...
    exact: bool            # True when results carry no sampling or device noise
```

`circuit_executions` is defined the same way for both engines, so budgets are comparable across
backends: one per expectation value, plus two per shifted gate occurrence per sample for a
gradient (what the parameter-shift rule needs on hardware).

### 4.1 Circuit analysis (`_analysis.py`)

Both engines need to know, for every parameterised gate occurrence, its angle as an affine
function of one user parameter: `angle = a * p + b`. Extract `a` with
`ParameterExpression.gradient(p)` and `b` by binding `p = 0`. A gate qualifies for gradients when
it is a Pauli rotation (`rx, ry, rz, p, rxx, ryy, rzz, rzx`; `p` has the same shift rule as `rz`)
whose angle is affine in exactly one parameter. A parameter may appear in many gates (weight
sharing): the gradient is the sum over occurrences, scaled by `a`. Anything else raises
`NotSupportedError` with a message that says which gate and what to do (use the SPSA optimiser,
or decompose the gate).

### 4.2 `StatevectorEngine`

- Exact, noiseless, NumPy only. Default when the user passes no estimator.
- Batched over samples: state array of shape `(n, 2, ..., 2)`.
- Fixed gates: use `gate.to_matrix()` once (any gate with no free parameters, up to 3 qubits is
  enough). Parameterised gates: the Pauli rotations of 4.1.
- Observable: any `SparsePauliOp`.
- Gradients by the adjoint method (one forward pass, one backward pass), batched.
- Qiskit is little-endian: qubit 0 is the least significant bit. Tests must compare against
  `qiskit.quantum_info.Statevector` on random circuits, including non-symmetric observables.
- Raises `NotSupportedError` for mid-circuit measurement, resets, control flow, or more qubits
  than a configurable `max_qubits` (default 20).

### 4.3 `PrimitiveEngine`

```python
PrimitiveEngine(estimator: BaseEstimatorV2, *, pass_manager=None, precision: float | None = None,
                max_batch_size: int | None = None)
```

- Written against `qiskit.primitives.BaseEstimatorV2` only. No import of Aer or IBM Runtime.
- `compile` runs `pass_manager.run(circuit)` once if a pass manager is given and applies
  `observable.apply_layout(isa.layout)`. The transpiled circuit is cached on the compiled object.
- `expectation` sends one PUB `(circuit, observable, values_chunk)` per chunk of
  `max_batch_size` rows and reads `result[0].data.evs`. `precision` is passed as the run-level
  `precision=` argument only (never per PUB; IBM Runtime 0.52 forbids mixing).
- `value_and_gradient` uses the parameter-shift rule, with all shifted parameter sets of a batch
  packed into the same broadcast PUBs. For shared parameters each gate occurrence is shifted
  separately; implement this by rewriting the circuit once so that every gate occurrence has its
  own internal parameter, and mapping user values to internal values with the affine map of 4.1.
- `exact` is False unless the estimator is a `StatevectorEstimator` with zero precision.
- Parameter order after transpilation must be handled explicitly (bind by name, not by position).

## 5. `qascade.circuits`

```python
angle_feature_map(n_qubits: int, n_features: int | None = None, *, axes: Sequence[str] = ("ry",),
                  parameter_prefix: str = "x") -> QuantumCircuit
```
Feature `j` is encoded on qubit `j % n_qubits` with rotation `axes[j // n_qubits]`. If
`n_features < n_qubits` the remaining qubits repeat the features cyclically. Raises if
`n_features > len(axes) * n_qubits`. The circuit's parameters are a `ParameterVector` of length
`n_features`.

```python
qcnn_ansatz(n_qubits: int, *, depth: int | None = None, conv_reps: int = 1,
            share_weights: bool = True, parameter_prefix: str = "w") -> QuantumCircuit
```
- A level is `conv_reps` convolution layers followed by one pooling layer.
- Convolution layer: the two-qubit block below on neighbouring active qubits, even pairs then odd
  pairs, with a wrap-around pair when more than two qubits are active.
- Pooling layer: active qubits are paired (source, sink); the pool block is applied and the
  source is dropped from the active set. An unpaired qubit stays active.
- `depth=None` means pool until one qubit is active. Any `n_qubits >= 2` must work, not only
  powers of two.
- `share_weights=True` uses one parameter set per layer (translation invariance); False gives
  every block its own parameters.
- Blocks use only CX and single-qubit `rz`/`ry` rotations so that the two-term parameter-shift
  rule applies:
  - conv block on (a, b), 3 parameters: `rz(-pi/2, b); cx(b, a); rz(t0, a); ry(t1, b); cx(a, b);
    ry(t2, b); cx(b, a); rz(pi/2, a)`
  - pool block on (source, sink), 2 parameters: `rz(-pi/2, sink); cx(sink, source);
    ry(t0, sink); cx(source, sink); ry(t1, sink)`. (The usual third parameter, an `rz` on the
    source before it acts as a control and is discarded, cannot change the readout, so it is left
    out: every parameter costs two circuit executions per sample under parameter shift.)
- The active qubits after the last level are stored in `circuit.metadata["readout_qubits"]`.

```python
readout_observable(n_qubits: int, qubits: Sequence[int]) -> SparsePauliOp   # mean of Z on `qubits`
build_qcnn(n_qubits, n_features, **options) -> tuple[QuantumCircuit, ParameterVector, list[Parameter], SparsePauliOp]
```
`build_qcnn` composes feature map and ansatz and returns the feature parameters, the weight
parameters and the readout observable.

## 6. `qascade.losses`

Pure NumPy. Raw predictions have shape `(n, K)`; `K = 1` except for the multinomial loss.

```python
class BaseLoss(ABC):
    n_outputs: int = 1                       # set from data for multinomial
    is_classification: bool = False
    def init_raw_prediction(self, y, sample_weight) -> NDArray        # (K,)
    def loss(self, y, raw, sample_weight=None) -> float               # weighted mean
    def negative_gradient(self, y, raw) -> NDArray                    # (n, K)
    def line_search(self, y, raw, direction, sample_weight=None) -> NDArray   # (K,) step per output
    def hessian(self, y, raw) -> NDArray | None                       # optional, for Newton line search
```

- `SquaredError`, `AbsoluteError`, `HuberLoss(delta=1.35 quantile-style alpha=0.9 as in sklearn)`,
  `LogLoss` (binary, `y` in {0, 1}, raw = log-odds), `MultinomialLoss` (softmax, `y` as integer
  class indices).
- `line_search` default: closed form for squared error; otherwise a safeguarded 1-D minimisation
  per output (Newton steps with a bracketing fallback, or `scipy.optimize.minimize_scalar`). It
  must never return a non-finite step, and must return 0 when the direction is all zeros.
- `CustomLoss(loss_fn, gradient_fn, init_fn=None)` wraps user callables.
- `get_loss(name_or_instance, *, classification: bool) -> BaseLoss` with clear errors for
  unknown names. Names: `"squared_error"`, `"absolute_error"`, `"huber"`, `"log_loss"`.
- Numerically stable (`scipy.special.expit`, `logsumexp`, `xlogy`).

## 7. `qascade.optimizers`

```python
class OptimizerResult: x, fun, n_iter, n_function_evaluations, n_gradient_evaluations, converged, history
class BaseOptimizer(ABC):
    requires_gradient: bool
    def minimize(self, fun, x0, *, value_and_gradient=None, rng=None, callback=None) -> OptimizerResult
```
- `fun(x) -> float`; `value_and_gradient(x) -> (float, grad)`. Both may be stochastic
  (mini-batches are drawn by the caller inside the closure).
- `Adam(learning_rate=0.1, max_iter=50, beta1=0.9, beta2=0.999, tol=0.0, n_iter_no_change=10)`
- `SPSA(max_iter=100, learning_rate=None, perturbation=None, ...)` with the standard gain
  schedules and a simple calibration of the first step size; two function values per iteration.
- `ScipyOptimizer(method="COBYLA", max_iter=..., options=None)`; uses the gradient when the
  method accepts one.
- `get_optimizer(name_or_instance, **overrides)`; names `"adam"`, `"spsa"`, `"cobyla"`,
  `"lbfgs"`.
- All three follow sklearn parameter conventions (`get_params`/`set_params` through
  `BaseEstimator`) so they clone and pickle.

## 8. `qascade.learners`

```python
class CircuitRegressor(RegressorMixin, BaseEstimator):
    def __init__(self, circuit, feature_parameters, weight_parameters, observable=None, *,
                 input_scaling="minmax", optimizer="adam", max_iter=50, learning_rate=0.1,
                 batch_size=None, initial_weights=None, estimator=None, pass_manager=None,
                 precision=None, random_state=None): ...
class QCNNRegressor(CircuitRegressor-like):
    def __init__(self, n_qubits=4, *, depth=None, conv_reps=1, share_weights=True,
                 feature_map="angle", ansatz="qcnn", observable=None, <same training options>): ...
```
- `fit(X, y, sample_weight=None)`, `predict(X)`.
- Input scaling `"minmax"` maps each feature to `[0, pi]` using the training rows (constant
  features map to 0); `None` passes values through as angles.
- Target handling: `t = (y - mean) / scale` with `scale = max|y - mean|` (1 if zero). Train the
  weights to minimise weighted mean squared error between `<O>` and `t`. After training fit an
  affine readout `a * <O> + b` to `y` by weighted least squares. `predict` returns `a * <O> + b`.
- `estimator`: `None` -> `StatevectorEngine`; a `BaseEstimatorV2` -> `PrimitiveEngine`; an
  `ExpectationEngine` is used as is.
- Gradient-based optimisers use `value_and_gradient`; if the engine or circuit cannot give
  gradients the error says to use `optimizer="spsa"`.
- `feature_map` / `ansatz` accept a name or a callable `(n_qubits, n_features) -> QuantumCircuit`
  / `(n_qubits) -> QuantumCircuit`.
- Fitted attributes: `weights_`, `readout_` (a, b), `n_iter_`, `loss_curve_`, `usage_`
  (`ResourceUsage`), `n_features_in_`, `feature_capacity` (class-level property: how many features
  the learner can encode).
- `__sklearn_clone__` copies parameters but shares `estimator` and `pass_manager` by reference
  (a backend connection is a shared resource and may not be deep-copyable).
- `__getstate__` drops `estimator`, `pass_manager` and compiled caches. `attach(estimator=...,
  pass_manager=...)` re-attaches after loading.

## 9. `qascade.boosting`

```python
class BoostedQCNNRegressor(RegressorMixin, _BaseBoostedQCNN)
class BoostedQCNNClassifier(ClassifierMixin, _BaseBoostedQCNN)

__init__(self, *, loss=..., n_estimators=20, learning_rate=0.3, subsample=1.0, max_features=None,
         weak_learner=None, n_qubits=4, depth=None, conv_reps=1, share_weights=True,
         feature_map="angle", ansatz="qcnn", optimizer="adam", max_iter=50,
         estimator=None, pass_manager=None, precision=None,
         line_search=True, corrective=False, corrective_l2=1e-6,
         validation_fraction=0.1, n_iter_no_change=None, tol=1e-4,
         max_circuit_executions=None, warm_start=False, n_jobs=None, random_state=None, verbose=0)
```

- `weak_learner`: any scikit-learn regressor (`fit(X, y[, sample_weight])`, `predict(X)`). When
  `None`, a `QCNNRegressor` is built from `n_qubits ... precision`. When given, those convenience
  parameters are ignored. The booster must work with a classical regressor such as
  `DecisionTreeRegressor(max_depth=1)`: this is how it is tested without quantum code, and it lets
  users compare against a classical weak learner under identical boosting logic.
- Each learner gets its own seed drawn from `random_state` (set through `set_params` when the
  learner has a `random_state` parameter).
- `max_features`: `None` -> all features, unless the learner exposes `feature_capacity` smaller
  than the number of features, in which case that capacity; also int, float in (0, 1], `"sqrt"`.
  The subset is redrawn every stage (and for every class in multiclass).
- `subsample < 1`: rows drawn without replacement per stage; out-of-bag improvement recorded in
  `oob_improvement_`.
- Regression losses: `"squared_error"` (default), `"absolute_error"`, `"huber"`, or a `BaseLoss`.
  Classification: `"log_loss"` (binary -> `LogLoss`, more than two classes -> `MultinomialLoss`
  with one learner per class per stage), or a `BaseLoss`.
- `line_search=False` uses step 1.0.
- `corrective=True`: after each stage re-optimise all stage weights jointly on the cached learner
  outputs, minimising the loss plus `corrective_l2 * ||w||^2` (closed form for squared error,
  L-BFGS otherwise). Costs no circuit executions. The weight vector as it stood after each stage
  is stored so that staged prediction stays exact.
- Early stopping as in scikit-learn: active when `n_iter_no_change` is an int; holds out
  `validation_fraction` (stratified for classifiers); stops when the validation loss has not
  improved by `tol` for `n_iter_no_change` stages; keeps the model up to the best stage.
- `max_circuit_executions`: stop before starting a stage once the running total of learner
  `usage_.circuit_executions` reaches the budget (learners without `usage_` count as zero).
- `warm_start=True`: a later `fit` with larger `n_estimators` adds stages.
- `n_jobs`: joblib threads for the per-class learners of one stage and for prediction over stages.
- Methods: `fit(X, y, sample_weight=None)`, `predict`, `staged_predict`, and for the classifier
  `decision_function`, `predict_proba`, `predict_log_proba`, `staged_decision_function`,
  `staged_predict_proba`; `save(path)`.
- Fitted attributes: `estimators_` (list of length `n_estimators_`, each a list of `K` learners),
  `estimator_weights_` (`(n_estimators_, K)`, includes the learning rate), `estimator_features_`,
  `init_raw_prediction_`, `train_score_`, `validation_score_`, `oob_improvement_`,
  `n_estimators_`, `feature_importances_`, `usage_`, `n_circuit_executions_`, `classes_`,
  `n_features_in_`, `feature_names_in_`, `loss_`.
- `feature_importances_`: the training-loss reduction of each stage is split equally among the
  features that stage used, summed and normalised to 1. Document that this is coarse and point to
  `sklearn.inspection.permutation_importance`.
- scikit-learn conventions: no logic in `__init__`; `validate_data`; `__sklearn_tags__`;
  `check_is_fitted`; parameter validation with clear messages; passes `check_estimator`, with any
  check that cannot apply listed in `expected_failed_checks` and explained in the docs.

## 10. `qascade.serialization`

`save_model(model, path)` writes one zip file: `manifest.json` (format version, qascade, qiskit,
scikit-learn, numpy and Python versions, class name, parameters as far as JSON allows) and
`model.joblib`. Backend objects are never written (learners drop them in `__getstate__`).
`load_model(path, *, estimator=None, pass_manager=None)` checks the format version, warns on a
qascade major/minor mismatch, and re-attaches the estimator to every learner. Document that the
file contains a pickle and must only be loaded from a trusted source.

## 11. Quality rules for all code

- Full type hints; `mypy --strict` clean. NumPy-style docstrings on every public object, with a
  short runnable example where it helps. `ruff check` and `ruff format` clean.
- Errors are specific and say what to do next.
- Deterministic given `random_state` on the exact engine. No global NumPy seeding; use
  `numpy.random.Generator` / `sklearn.utils.check_random_state` consistently.
- Tests: pytest, at least 90% branch coverage per module, edge cases, and comparisons against an
  independent reference wherever one exists (Qiskit `Statevector`, scikit-learn's own gradient
  boosting, finite differences).
- No AI tool is named as an author or contributor in any file.
