# Phase 0 novelty memo: gradient boosting of small QCNNs

Date: 2026-11-16. Status: **awaiting maintainer approval (checkpoint 1)**. No package code has been written.

## 1. Verdict

**The general idea is partly published. The specific idea appears to be open, but it is narrower than the original pitch, and two of its three claims need reframing.**

- **Published already:** boosting small variational circuits and QCNNs with *AdaBoost* (theory, simulation and superconducting hardware), bagging and AdaBoost of shallow circuits as noise mitigation, and one 2026 preprint that fits quantum circuits stagewise to residuals for 1-D synthetic regression.
- **Not found anywhere:** Friedman-style functional gradient boosting (pseudo-residuals of a general loss, shrinkage, subsampling, early stopping) with QCNN weak learners, compared at a strictly matched budget against one deeper QCNN, with a noise study.
- **Claims that will not survive review as originally stated:**
  - *"Less barren-plateau behaviour."* QCNNs are already proven free of barren plateaus, so the single deeper QCNN is not hard to train in that sense.
  - *"More robust to noise because shallow."* Shallow, noise-tolerant circuits are also the ones that are classically simulable, and QCNNs specifically have been simulated classically at up to 1024 qubits.
- **No quantum-advantage claim is defensible.** The honest paper is a study of a training method, with the classical surrogate of the same model shipped as a baseline.

Search confidence, as estimated by the survey subagent: about 85–90% that no prior paper does Friedman gradient boosting with QCNN weak learners, and about 70% that the 2026 residual-fitting preprint is the only one of its kind (the terminology varies: "multi-stage", "cascade", "residual learning"). One lead is unresolved; see section 9.

## 2. How this memo was checked

Four Opus 5.5 subagents ran the surveys. Their reports were then reviewed, and the claims this memo relies on were re-checked against primary sources.

- **[A]** = checked directly for this memo: arXiv API record (ID, title, authors, journal reference), Crossref DOI record, PyPI JSON API, or the official page.
- **[S]** = opened by a subagent, not re-checked. These must be re-verified before they go into a paper.

Every arXiv ID in sections 3 and 4 is [A] unless marked otherwise. What each paper *did* (beyond title, authors and abstract) comes from the subagents' reading of the full text unless the abstract is quoted.

## 3. Closest prior work, ranked by overlap

| # | Paper | What it did | What it did not do |
|---|-------|-------------|--------------------|
| 1 | Daskin, *Mitigating Frequency Learning Bias in Quantum Models via Multi-Stage Residual Learning*, arXiv:2603.10083 (v2, 2026) | "Iteratively training additional quantum modules on the residuals of previous stages" (abstract). This is squared-loss boosting in all but name. Synthetic 1-D frequency benchmark. | No shrinkage, no losses other than squared error, no classification, no QCNN, no noise or hardware, no comparison with a deeper circuit (baseline is one stage trained for the same epochs). |
| 2 | Wang, Wang, Qi, Dong, *Supervised Learning Guarantee for Quantum AdaBoost*, Phys. Rev. Applied 22, 054001 (2024), arXiv:2402.02376 | Proves a risk bound for AdaBoost over variational weak learners; under noise the boosted model "can also surpass the ideally noiseless but unboosted primitive classifier" (abstract). Subagent reports from the full text that the weak learners are QCNNs (6 and 8 qubits). | AdaBoost reweighting, not pseudo-residuals. Classification only. No matched-budget deep baseline. |
| 3 | Chen, Wu, Yang, Xu et al., *Quantum ensemble learning with a programmable superconducting processor*, npj Quantum Inf. 11, 83 (2025), arXiv:2503.11047 | AdaBoost.Q on real hardware, "including quantum neural networks and quantum convolutional neural networks"; 100% on a quantum feature recognition task over 1,564 test samples (abstract). | AdaBoost variant, classification only. |
| 4 | Li, Huang, Hou, Li, Wang, Bayat, *Ensemble-learning error mitigation for variational quantum shallow-circuit classifiers*, Phys. Rev. Research 6, 013027 (2024), arXiv:2301.12707 | Bagging and AdaBoost that "combine several weak classifiers, each implemented on a shallow noisy quantum circuit" (abstract), on digits and SPT phase discrimination. | AdaBoost and bagging only. Matched on depth, not on a full budget. |
| 5 | Incudini, Grossi, Ceschini, Mandarino et al., *Resource Saving via Ensemble Techniques for Quantum Neural Networks*, Quantum Mach. Intell. 5 (2023), arXiv:2303.11283 | Bagging and AdaBoost (regression and classification) of QNNs, including noisy simulation and hardware [S]. | Sample reweighting, not residual targets. |
| 6 | Friedrich, Maziero, *Quantum neural network with ensemble learning to mitigate barren plateaus and cost function concentration*, arXiv:2402.06026 | "Simultaneous deployment of multiple quantum circuits with a depth equal to 1" in place of one depth-L circuit (abstract). Closest to the trainability hypothesis. | Trained jointly, not stagewise. No boosting. |
| 7 | Wang, Wang, Wu, *Towards Ultimate Accuracy in Quantum Multi-Class Classification: A Trace-Distance Binary Tree AdaBoost Classifier*, arXiv:2602.02120 | Many small submodels in place of one deep circuit, argued to mitigate barren plateaus [S for content]. | AdaBoost. |
| 8 | Rhrissorrakrai, Hamilton, Bangalore Parthsarathy et al., *Quantum Ensembling Methods for Healthcare and Life Science*, arXiv:2506.02213 | Mentions gradient boosting as an option for variational ensembles but only runs AdaBoost [S for content]. | No gradient boosting experiments. |

**Work that shares the word "boosting" but is a different thing, and must be cited and distinguished:**

- **QBoost.** Neven, Denchev, Rose, Macready, *Training a Binary Classifier with the Quantum Adiabatic Algorithm*, arXiv:0811.0416. A quantum annealer solves an optimisation problem that *selects classical* weak classifiers. There are no quantum learners and no gradient steps. Do not call this project's method "QBoost".
- **Fault-tolerant quantum boosting.** Arunachalam & Maity, *Quantum Boosting*, ICML 2020, arXiv:2002.05056; Izdebski & de Wolf, *Improved Quantum Boosting*, arXiv:2009.08360; Bera et al., Quantum Mach. Intell. 5, 33 (2023), arXiv:2110.12793; Abbas et al., *QuantumBoost*, arXiv:2510.05089. These speed up the boosting *algorithm* on a fault-tolerant machine. They do not train circuits as weak learners.
- **Layerwise training.** Skolik et al., *Layerwise learning for quantum neural networks*, Quantum Mach. Intell. 3, 5 (2021), arXiv:2006.14904 grows one circuit layer by layer. Campos, Nasrallah, Biamonte, Phys. Rev. A 103, 032607 (2021), arXiv:2010.09720 prove the "layer-wise trainability conjecture" false. A reviewer will ask why stagewise boosting escapes that result. (Short answer to develop: boosting adds terms to a *sum of outputs*, each trained against a fresh target, and does not freeze layers inside one circuit. That needs to be argued, not assumed.)
- **A review states the gap.** Herman et al., *Quantum computing for finance*, Nat. Rev. Phys. (2023), arXiv:2307.11230. Subagent quotes it: "Currently, there does not appear to be any quantization of gradient boosting" [S for the quote].

## 4. Threats to the hypothesis

These are the objections a NeurIPS reviewer is most likely to raise. Each one changes what the paper should claim.

### 4.1 Classical simulability (the critical one)

- Cerezo et al., *Does provable absence of barren plateaus imply classical simulability?*, Nat. Commun. 16, 7907 (2025), arXiv:2312.09121, argue that models provably free of barren plateaus usually live in a small subspace that a classical computer can handle.
- Bermejo et al., *Quantum Convolutional Neural Networks are Effectively Classically Simulable*, PRX Quantum 7, 020304 (2026), arXiv:2408.12739, simulate QCNNs for phase classification at up to 1024 qubits. Coverage of the paper reports the classical surrogate matched or beat the QCNN on every benchmark [S].
- Mele et al., *Noise-induced shallow circuits and absence of barren plateaus*, Nat. Phys. 22, 751 (2026), arXiv:2403.13927: noise makes circuits effectively shallow, and effectively shallow circuits can be estimated classically.
- A 4–8 qubit learner can be simulated exactly by brute force in any case.

**The span argument (reasoning for this memo, not from a paper; simple enough to prove in the paper).** If every weak learner encodes the input once with the same feature map, each learner's output is `Tr(ρ(x) O_m)`: linear in the encoded state `ρ(x)`. The boosted ensemble is then `Tr(ρ(x) Σ γ_m O_m)`, the expectation of *one* observable. Consequences:

- Boosting cannot add anything outside the linear span of what single learners can express. On classical data the Fourier frequencies are fixed by the encoding (Schuld, Sweke, Meyer, Phys. Rev. A 103, 032430 (2021), arXiv:2008.08605); summing learners adds none.
- What boosting *does* change is which points in that span are reachable. One shallow circuit reaches a thin curved set of coefficient vectors; a sum of many reaches towards the whole span. That is the real expressivity gain, and it is the same reason boosting stumps works classically.
- The best possible model in that span is a linear (ridge or kernel) fit on the features of `ρ(x)`, which for a few qubits a laptop computes exactly. **The boosted ensemble cannot beat that baseline on training loss. Whether it generalises as well, with less tuning or fewer circuit runs, is the open empirical question.**
- This does not hold as stated for data re-uploading circuits, where the Fourier view still applies but the model is not linear in one fixed state.

**You need to understand this section deeply.** It is the first thing an expert reviewer will raise, and the paper is only credible if it raises it first.

### 4.2 The barren-plateau comparison is a straw man

- Pesah et al., *Absence of Barren Plateaus in Quantum Convolutional Neural Networks*, Phys. Rev. X 11, 041011 (2021), arXiv:2011.02966, prove QCNN gradient variance vanishes at most polynomially with qubit count.
- Barren plateaus are an asymptotic effect. At 4–16 qubits there is little to escape.
- A better trainability question: local minima. Anschuetz & Kiani, *Beyond Barren Plateaus: Quantum Variational Algorithms Are Swamped With Traps*, Nat. Commun. 13, 7760 (2022), arXiv:2205.05786, show shallow models without barren plateaus can still be hard to train because of poor local minima. Stagewise fitting of small problems may or may not help with that; it is testable.
- The gradient-variance experiment in the original plan should still be run, but expect it to show little difference at these sizes, and say so.

### 4.3 Ensembles for noise are not new, and the shot budget cuts both ways

- Items 2–5 in section 3 already show shallow ensembles beating deeper circuits under noise, with AdaBoost and bagging.
- Splitting a fixed shot budget over M learners raises the variance of each learner's estimate, and the ensemble sums those errors. "Equal budget" has to count shots, not just qubits and parameters.
- A subagent proposed a lemma that the per-stage step size cancels depolarizing shrinkage. That is weaker than it sounds: a single deep circuit can be given a trainable output scale too. The honest version is a variance trade-off (signal lost to noise against shots split over learners) that the paper should derive and then measure.

### 4.4 Benchmarks

- Bowles, Ahmed, Schuld, *Better than classical? The subtle art of benchmarking quantum machine learning models*, arXiv:2403.07059: out-of-the-box classical models beat the quantum models tested, and removing entanglement often did not hurt [S for the findings]. Code: `XanaduAI/qml-benchmarks` [S].
- Gil-Fuster, Eisert, Bravo-Prieto, *Understanding quantum machine learning also requires rethinking generalization*, Nat. Commun. 15, 2277 (2024), arXiv:2306.13461: QCNNs can fit random labels, so uniform generalisation bounds say little. Caro et al., Nat. Commun. 13, 4919 (2022), arXiv:2111.05292, give bounds that scale with the number of trainable gates, which is the same for M small learners as for one large circuit of equal size.
- Expect to lose to XGBoost on tabular data. Plan for that result and report it.

### 4.5 Lessons from classical boosting of neural networks

- Badirli et al., *Gradient Boosting Neural Networks: GrowNet*, arXiv:2002.07971, report that greedy stagewise boosting of small networks stalls without a "corrective step" that re-trains all learners jointly [S for the finding].
- With that step the model is close to a jointly trained sum of circuits. **A jointly trained sum of QCNNs of identical total size is therefore the key control.** Without it the paper cannot separate "boosting helps" from "width helps".

## 5. Recommended angle

Keep the method. Change what is claimed.

**Working thesis:** *functional gradient boosting is a better way to train a sum of small circuits than the alternatives, at a matched and fully counted budget, and its benefit comes from optimisation and regularisation, not from quantum advantage.*

Claims to test, each of which can fail informatively:

1. **Optimisation.** At equal total circuit executions, boosted shallow QCNNs reach lower test loss than (a) one deeper QCNN, (b) the same learners trained jointly, (c) AdaBoost and bagging of the same learners.
2. **Noise.** Under realistic device noise models the boosted ensemble degrades less than the deep circuit, with shots counted.
3. **Honest ceiling.** The classical surrogate (linear or kernel model on the same feature space; shadow-based surrogate for phase tasks) is reported next to every quantum result. Expect it to match or win.
4. **Regularisation.** Shrinkage and early stopping give a usable accuracy-versus-budget dial that a single circuit does not have (`staged_predict` makes this cheap to measure).

Theory targets, kept in three separate boxes as the brief requires:

- **Provable:** the span lemma of section 4.1.
- **Provable under a stated assumption:** convergence of the stagewise procedure to the best loss over the span, adapting Zhang & Yu, *Boosting with early stopping: Convergence and consistency*, Ann. Statist. 33, 1538–1579 (2005), with the weak learner treated as an inexact, finite-shot oracle. The assumption that a QCNN is a good enough weak learner is an assumption, not a result.
- **Conjecture / empirical:** the noise variance trade-off of section 4.3 beyond the simple depolarizing model; any claim about local minima.

**Honest odds.** A NeurIPS main-track acceptance is uncertain for any QML paper without an advantage claim. A careful study with strong classical baselines, the joint-training control and plainly reported negative results is defensible. A paper that hides the surrogate will be rejected by the first expert reviewer.

## 6. The software gap

Findings on existing libraries are from the software survey [S] unless marked.

| Library (version) | sklearn-compatible | QCNN included | Any ensemble or boosting | Staged prediction / early stopping |
|---|---|---|---|---|
| qiskit-machine-learning 0.9.1 [A for version] | No (`TrainableModel` is not a `BaseEstimator`) | No (tutorial only) | No | No |
| sQUlearn 0.12.0 | Yes (not tested against `check_estimator`) | Yes | No | No |
| PennyLane 0.45.1 | No | No (demos only) | No | No |
| TorchQuantum 0.1.8 | No | No | No | No |
| TensorFlow Quantum 0.7.6 | No | Tutorial only | No | No |
| skqulacs 0.5.3 | No | Yes | No | No |

- **scikit-learn itself** cannot do this: `GradientBoostingRegressor` and `GradientBoostingClassifier` hard-code decision trees and accept no custom base estimator.
- **What a short wrapper already gives you:** `BaggingRegressor` or `AdaBoostRegressor` around a sQUlearn QNN should work, judging from the source. Nobody ran it. So bagging and AdaBoost of quantum models is not a contribution.
- **What no library offers, and Qascade would:**
  - loss-driven gradient boosting of circuits (squared, absolute, logistic, custom), with shrinkage, a per-stage step size and subsampling;
  - handling of the fact that a circuit's output is bounded in [-1, 1] while residuals are not;
  - validation-based early stopping and `staged_predict`;
  - a different seed for every ensemble member;
  - batched execution through Qiskit V2 primitives, with shot budgets tracked;
  - documented `check_estimator` compliance;
  - saving and loading a whole ensemble without the backend attached.
- **"Why not contribute this to sQUlearn or qiskit-machine-learning?"** JOSS requires an answer. The draft answer: boosting is a meta-estimator over a pluggable weak learner, sQUlearn's dependency set is very heavy, and qiskit-machine-learning's models are not sklearn estimators. Qascade should depend only on Qiskit, NumPy, SciPy and scikit-learn, and accept those libraries' circuits as weak learners.

**Technical facts that shape the design** (all [A]):

- Current versions: qiskit 2.6.2, qiskit-aer 0.18.2, qiskit-ibm-runtime 0.52.1, scikit-learn 1.9.1 (needs Python ≥ 3.11), numpy 2.5.5.
- qiskit-ibm-runtime 0.50.0 deprecated `EstimatorV2` and `SamplerV2` in favour of new client-side `Estimator` and `Sampler` classes; 0.52.0 removed the ability to mix shots or precision across inputs in one job. Qascade should be written against the abstract `BaseEstimatorV2` / `BaseSamplerV2` interfaces only, so it survives this kind of change.
- Core Qiskit has no gradient module [S], so Qascade implements the parameter-shift rule itself.

## 7. The name

- `qascade` and `boostqcnn` both return 404 on PyPI and TestPyPI [A], so both are free. A PyPI name is only secured by the first real upload.
- GitHub: `Suman-Poola/Qascade` is this repo. Two small unrelated repos use the name [S].
- **Possible clash:** Qascade Ltd, a UK company at Harwell Campus that makes photonic communication hardware and says its systems could support hybrid quantum-computing platforms [A, from the Harwell Campus directory]. It is not a software package and not a QML product, but it is in the quantum space. No trademark database was searched.
- Recommendation: keep Qascade unless that clash worries you. This is your call, and it is not legal advice.

## 8. Constraints you need to know about now

### 8.1 JOSS will not accept the repo before about mid-May 2027

From the JOSS submission guide [A, via search of joss.readthedocs.io]:

- The repository needs "at least six months of public history prior to submission, with evidence of releases, public issues and pull requests". This repo was created on 2026-11-16.
- "A repository made public immediately before submission, or one showing development concentrated into a few days or weeks, will not be accepted."
- There must be evidence the software is used for research [S]. The experiments and a preprint supply that.

So the package cannot be built in one burst and left. Development, releases and issues need to be spread over the six months, which the experiment phase will do naturally (each missing feature becomes a new release).

### 8.2 AI use must be disclosed in the JOSS paper

JOSS permits generative AI for code, docs and paper text, but requires an "AI usage disclosure" section naming the tools and where they were used, and a statement that the human authors "reviewed, edited, validated all AI-assisted outputs and made the core design decisions". Leaving it out "may be considered an ethical breach", with desk rejection or withdrawal as possible consequences [A].

- Your instruction not to list Claude as a contributor is being followed: no co-author lines, no contributor entries. That is consistent with JOSS and NeurIPS, where AI tools cannot be authors.
- It does not remove the disclosure requirement. The JOSS paper will have to say this package was built with AI assistance, and you will have to be able to assert, truthfully, that you reviewed it and made the core design decisions.
- NeurIPS: the 2026 policy, as reported, requires disclosure of methodologically significant LLM use [S, the handbook itself was not opened]. The 2027 rules are not published yet and must be checked when they are.

### 8.3 Dates

The NeurIPS 2027 deadline of about 21 May 2027 is your estimate; no official date was found. The earliest JOSS submission date falls in the same week.

## 9. Unresolved leads

- **Hu, Xiao, Yang, Wang et al., *Quantum-enhanced gradient boosting neural networks for optimizing PFOS removal with nanofiltration membranes*, Desalination and Water Treatment 323, 101266 (2025), DOI 10.1016/j.dwt.2025.101266** [A for existence]. The title overlaps with this project. The full text is paywalled and neither the abstract nor search results say how the quantum part works. **Please open it through your institution and check whether the weak learners are quantum circuits trained on residuals.** If they are, it becomes the closest prior work and must be cited as such.
- Not searched: Google Scholar, IEEE QCE proceedings, and GitHub in depth.
- A few venues for cited papers were taken from secondary sources and are marked [S].

## 10. Your existing S&P 500 repository

A subagent read `Suman-Poola/Random-Forrest-s-p500` without running anything; the items below were re-checked against the clone unless marked [S].

- The local QCNN already uses Qiskit 2.x and V2 primitives: 16 qubits, 135 weights, COBYLA with 400 iterations. Saved output: train R² 0.0061, test R² −0.0272, mean IC −0.028. It does not beat predicting zero.
- `results/summary.csv`, chronological split: zero forecast MSE 6.645; linear regression, XGBoost and the LSTM are all within about 0.05 of it. Nothing meaningfully beats the zero forecast.
- The current scripts have no hard look-ahead: features look backward, the target is the next day's return shifted per ticker, the main split is chronological.
- **Survivorship bias:** the universe is today's S&P 500 list applied to past years. This must be fixed (point-in-time membership) before the case study.
- [S] Bugs in the older LSTM notebooks (target off by one day, a shape mismatch in the loss), and a small cross-sectional edge (rank IC about 0.02) in the improved models before trading costs.

**Implication:** the finance case study will most likely be a null result for every model. That is fine for a case study if it is framed that way from the start.

## 11. Decisions needed from you

1. **Angle.** Proceed with the reframed thesis in section 5 (training-method study, surrogate baseline included, no advantage claim)?
2. **Name.** Keep Qascade given Qascade Ltd?
3. **AI disclosure.** Confirm you accept that the JOSS paper must disclose AI assistance, and that you will review the code closely enough to stand behind that statement.
4. **The paywalled paper in section 9.** Can you check it?

Recommended for Phase 1 and to be logged in `DECISIONS.md` unless you object: Apache-2.0 licence (same as Qiskit, includes a patent grant); Python 3.11–3.14; dependencies limited to Qiskit, NumPy, SciPy and scikit-learn, with Aer and IBM Runtime as optional extras.
