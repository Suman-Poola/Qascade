# Decision log

Each entry is one decision with a one-line rationale. Newest entries go at the bottom.

| # | Date | Decision | Rationale |
|---|------|----------|-----------|
| 1 | 2026-11-16 | The package is named **Qascade** (PyPI and import name `qascade`). | Chosen by the maintainer; replaces the working name `boostqcnn`. Availability on PyPI is checked in the Phase 0 memo. |
| 2 | 2026-11-16 | All work lives in the public repository `Suman-Poola/Qascade`, pushed after each working step. | Maintainer's instruction; keeps history open and reviewable for JOSS. |
| 3 | 2026-11-16 | Work proceeds in phases with three approval checkpoints: after the novelty memo, before the real PyPI release, and before writing the paper. | Maintainer's instruction; nothing irreversible (PyPI name, paper claims) happens without sign-off. |
| 4 | 2026-11-16 | The novelty memo is written before any package code. | If the core idea is already published, the package scope and the paper's angle both change. |
| 5 | 2026-11-16 | The Phase 0 memo lives at `memos/phase0-novelty-memo.md`. | Keeps research memos separate from the future `docs/` site. |
| 6 | 2026-11-16 | Every citation is tagged as checked against a primary record or as reported by a survey only; the second kind is re-verified before it enters a paper. | The brief forbids invented references; a survey summary is not a primary source. |
| 7 | 2026-11-16 | The method is not called "QBoost" anywhere. | QBoost is an established, different algorithm (Neven et al., arXiv:0811.0416). |
| 8 | 2026-11-16 | Paper angle: a training-method study with no quantum-advantage claim; the classical surrogate and a jointly trained sum of circuits are mandatory baselines. | Approved by the maintainer after the Phase 0 memo; these are the objections an expert reviewer raises first. |
| 9 | 2026-11-16 | Licence: Apache-2.0. | Same as Qiskit and scikit-learn-adjacent projects; includes an explicit patent grant. |
| 10 | 2026-11-16 | Supported Python: 3.11 to 3.14. | 3.10 reached end of life in October 2026 and scikit-learn 1.9 requires 3.11. |
| 11 | 2026-11-16 | Required dependencies are only NumPy, SciPy, scikit-learn, joblib and Qiskit; Aer and IBM Runtime are optional extras. | Keeps installation light and avoids depending on libraries whose maintenance status is uncertain. |
| 12 | 2026-11-16 | Code is written against `qiskit.primitives.BaseEstimatorV2`, never against a concrete Aer or IBM class. | IBM Runtime deprecated and replaced its concrete primitive classes in 0.50 to 0.52; the abstract interface is the stable contract. |
| 13 | 2026-11-16 | Gradients are implemented in the package (parameter shift on primitives, adjoint method in the built-in simulator). | Core Qiskit has no gradient module, and qiskit-machine-learning is not a dependency. |
| 14 | 2026-11-16 | The default engine is a built-in NumPy statevector simulator; passing any V2 Estimator switches to Qiskit primitives. | Parameter-shift through a primitive costs two circuits per gate per sample, too slow for development and for sklearn's estimator checks; both engines are tested against each other. |
| 15 | 2026-11-16 | The booster's weak-learner argument is `weak_learner`; `estimator` always means a Qiskit Estimator primitive. | "Estimator" means different things in scikit-learn and Qiskit; one meaning per name avoids confusion. |
| 16 | 2026-11-16 | Any scikit-learn regressor can be the weak learner, including classical ones. | Makes the booster testable without quantum code and gives users a like-for-like classical control. |
| 17 | 2026-11-16 | Each stage trains on a random feature subset no larger than the learner's qubit capacity. | Lets few-qubit learners handle many-feature data without a mandatory PCA step, and yields feature importances. |
| 18 | 2026-11-16 | Circuit cost is reported in hardware-equivalent circuit executions, defined identically for both engines. | The paper's matched-budget comparisons need one backend-independent unit. |
| 19 | 2026-11-16 | The corrective step re-optimises stage weights only, on cached learner outputs. | It answers the known weakness of greedy boosting at zero quantum cost; re-training circuit parameters jointly would multiply circuit executions. |
| 20 | 2026-11-16 | Cloning an estimator shares the Qiskit primitive by reference; saving a model never writes it. | A backend connection is a shared resource that may not be copyable or serialisable. |
| 21 | 2026-11-16 | Build backend is hatchling with the version in `src/qascade/_version.py`. | Simple, standard, and has no dependency on git tags at build time. |
| 22 | 2026-11-16 | The development environment uses Python 3.11, the oldest supported version. | Catches use of newer-only syntax and APIs before CI does. |
