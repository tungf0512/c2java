# Weekly Report

**Subject:** [LAB]Norm2Proof_Weekly Report_Week 24 (June 16-June 22, 2026)  
**Sent to:** Mentor(s)  
**Cc:** KhuongND6, HieuDD12, TuyetDTA1

## Content

**Week:** Week 24 (June 16-June 22, 2026)

### 1. Research Objectives & Key Metrics

**Research Objective:** Consolidate the security benchmark direction by validating the current CoEST audit results, analyzing a concrete authentication-error case in depth, and converting dynamic-analysis blockers into actionable implementation strategies.

This week focused less on adding a large new component and more on making the evaluation direction concrete and defensible. The main new result is a refreshed dataset-level problem-class audit with explicit dynamic strategy counts. This helps decide which classes should be handled by method-level harnesses, service-level harnesses with DB stubs, implementation search, boundary recovery, or full UI/application instrumentation.

| Metrics | Current Status | Target | Blockers |
|---|---|---|---|
| CoEST security benchmark size | Revalidated: 464 deduplicated artifacts, 80 direct-security, 109 broad-security | Use as benchmark population | Human validation still needed |
| Authentication/authorization pilot | 33 unique use cases defined | Use as first coding-agent baseline subset | Authorization remains underrepresented |
| eTour problem-class audit | Re-run on 56 instances / 259 flow steps | Use to choose dynamic strategies | Many steps require DB stubs or UI/full-app context |
| Dynamic strategy planning | New counts generated | Prioritize service harness and boundary recovery | Only 5 steps are directly method-level runnable |
| UC36 case study | Expanded with full artifact-level analysis | Use as concrete running example | Gold links cover traceability, not full behavioral correctness |
| Regression tests | 73/73 tests passed | Keep prototype stable while adding evaluation | No runtime/dynamic harness yet |

### 2. Completed Tasks

#### 2.1. Revalidated the CoEST Security Benchmark

The CoEST security audit was re-run and reproduced the benchmark-level counts:

| Scope | Count |
|---|---:|
| Deduplicated requirement/use-case artifacts | 464 |
| Directly security-related artifacts | 80 (17.2%) |
| Broad security-related artifacts | 109 (23.5%) |
| Raw artifacts including duplicated iTrustFull | 595 |
| Raw direct-security artifacts including iTrustFull | 95 |
| Raw broad-security artifacts including iTrustFull | 125 |

The interpretation remains:

- the 33 authentication/authorization use cases are suitable for a pilot;
- the 80 direct-security artifacts are a better main evaluation pool;
- LibEST should be reported separately because it contains protocol-level requirements rather than use-case flow requirements;
- iTrustFull should not be counted as new requirements because its requirement files duplicate iTrust.

#### 2.2. Re-ran the eTour Problem-Class Audit with Week-24 Outputs

Generated a fresh audit artifact:

```text
artifacts/problem_class_audit_week24/
```

Main result:

| Metric | Value |
|---|---:|
| Instances parsed | 56 |
| Flow steps parsed | 259 |
| Mean boundary confidence | 0.518 |
| Mean predicate coverage estimate | 0.474 |

Manual feasibility:

| Manual feasibility | Count |
|---|---:|
| high | 67 |
| medium | 100 |
| low | 92 |

Dynamic feasibility:

| Dynamic feasibility | Count |
|---|---:|
| partially runnable with mocks | 122 |
| not runnable, no boundary | 65 |
| full app required | 44 |
| not runnable, interface only | 23 |
| method-level runnable | 5 |

This result confirms the current bottleneck: most steps are not impossible, but they are not immediately runnable either. The largest useful class is `partially_runnable_with_mocks`, which suggests that the next practical implementation path should be service-level harnesses with DB/UI/auth stubs rather than full dynamic execution from the start.

#### 2.3. Added Dynamic Strategy Counts

The new week-24 audit makes the dynamic direction more concrete by assigning each step to a recommended strategy:

| Dynamic strategy | Count |
|---|---:|
| service harness with DB stub | 111 |
| boundary recovery first | 65 |
| UI or full-app instrumentation | 40 |
| implementation search first | 23 |
| service harness with mocks | 11 |
| method harness | 5 |
| full-app or integration harness | 4 |

Key interpretation:

- `service_harness_with_db_stub` is the largest feasible path and should be the first dynamic-analysis target.
- `boundary_recovery_first` is still a major blocker, which supports the current research focus on `StepBoundary`.
- `implementation_search_first` mostly corresponds to cases where gold links expose interfaces or contracts but not concrete implementations.
- `method_harness` is too small to be the main evaluation direction, but useful for smoke tests.
- UI/full-app instrumentation should be deferred until service-level verification is stable.

#### 2.4. Analyzed Boundary Failure Reasons

The audit also gives a clearer picture of why dynamic verification is blocked:

| Failure reason | Count |
|---|---:|
| requires database | 185 |
| no call path | 70 |
| missing UI boundary | 66 |
| no candidate boundary | 65 |
| generic helper only | 47 |
| requires full app | 44 |
| interface only | 23 |
| missing concrete implementation | 23 |
| missing state boundary | 14 |

These results are important because they turn the vague problem "dynamic run is hard" into concrete engineering tasks:

- build DB stubs for DAO/service methods;
- improve call-path discovery;
- recover UI event handlers only when needed;
- map interfaces to concrete implementations;
- prune generic helper methods from predicted boundaries.

#### 2.5. Expanded UC36 as a Running Authentication-Error Case Study

The UC36 analysis file was updated:

```text
CoEST_analyse/etour_uc36_full_instance_analysis_vi.md
```

UC36 is:

```text
Use case: LoginError
Description: The data supplied for the login is incorrect.
Flow:
  1. The system notices invalid login data and asks for confirmation.
  2. The user confirms the reading of the notification.
  3. The system recovers the previous state.
```

Gold-linked artifacts:

```text
IAuthentication.java
ControlData.java
```

Technical interpretation:

- `IAuthentication.java` is a contract boundary for login behavior.
- `ControlData.java` is a validation/helper boundary for checking input strings and data.
- Together they are good traceability evidence for authentication and input validation.
- However, they do not prove the full UC36 behavior.

Missing behavioral evidence:

- concrete implementation of `IAuthentication.login(...)`;
- login failure branch;
- UI notification or confirmation dialog;
- state restoration after the notification is acknowledged;
- connected call path from UI login action to authentication service and validation helper.

This case is useful for explaining the core novelty of Norm2Proof:

```text
Traceability link recovery can say which files are related.
StepBoundary inference must say which code region implements each flow step.
Compliance verification must then check whether the behavior is actually correct.
```

UC36 therefore shows why a coding agent or traceability baseline may overclaim correctness if it only sees `login(...)` and `checkString(...)`.

#### 2.6. Stabilized the Prototype with Regression Tests

The current test suite was run successfully:

```text
73 passed in 5.35s
```

This verifies that the current codebase remains stable after the recent additions around:

- step-boundary inference;
- boundary metrics;
- gold/silver boundary support;
- problem-class audit;
- security-use-case audit;
- query synthesis and normalization tests.

### 3. Current Technical Status

The current pipeline now supports:

- CoEST security-use-case audit;
- authentication/authorization subset extraction;
- eTour flow-step problem-class audit;
- manual feasibility estimation;
- dynamic feasibility estimation;
- dynamic strategy assignment;
- boundary failure taxonomy;
- UC36 artifact-level traceability analysis;
- regression tests for the existing prototype.

The most important new technical conclusion is:

```text
The next dynamic-analysis stage should not start from full application execution.
It should start from service-level boundaries with DB stubs, while improving boundary recovery and implementation search.
```

### 4. Results Summary

The week-24 results support the following evaluation plan:

1. Use the 33 authentication/authorization use cases as a small pilot.
2. Use the 80 direct-security artifacts as the main security benchmark.
3. Use eTour problem classes to select dynamic-analysis targets.
4. Start dynamic verification from service-level harnesses with DB stubs.
5. Keep UC36 as the running example for explaining why traceability is not enough.

The strongest quantitative signal is that 122/259 eTour steps are partially runnable with mocks, and 111/259 are assigned to `service_harness_with_db_stub`. This means dynamic analysis is feasible, but only if boundary inference and test harness generation are designed around partial execution rather than full-system execution.

### 5. Challenges

- Only 5/259 eTour steps are immediately method-level runnable.
- 185/259 steps require database-related handling, so DB stubbing is unavoidable.
- 70 steps still lack a reliable call path.
- 65 steps have no candidate boundary, meaning static retrieval is still incomplete.
- UC36 shows that gold-linked files may be relevant but still insufficient for correctness verification.
- Coding-agent baselines may produce plausible explanations without enough evidence, so unsupported-claim rate must be measured.

### 6. Lessons Learned

- Dynamic analysis should be staged: method harness first for smoke tests, then service harness with DB stubs, then full-app/UI instrumentation.
- Boundary recovery is not only an implementation detail; it is the central research problem.
- Authentication-error cases such as UC36 require multi-layer evidence: contract, validation, concrete login implementation, UI confirmation, and state recovery.
- The benchmark should distinguish related code, executable boundary, implemented behavior, and correctly implemented behavior.
- Reporting failure reasons is useful because it tells the mentor exactly what engineering component is needed next.

### 7. Next Steps

- Implement `RepoContextIndex` to improve boundary recovery:

```text
interface -> implementation mapping
caller/callee graph
layer tagging
UI/service/DAO classification
generic-helper pruning
```

- Implement the first service-level dynamic harness path:

```text
StepBoundary
  -> selected service/DAO methods
  -> generated DB stub or mock
  -> runtime trace
  -> predicate verdict
```

- Start with cases from the largest feasible strategy group:

```text
service_harness_with_db_stub: 111 steps
```

- Keep UC36 as a hard authentication example and select one easier data-access case as a runnable smoke test.
- Create a small human-reviewed gold set for the 33 authentication/authorization pilot.
- Run baseline comparisons using the same output schema for:

```text
direct LLM
generic coding agent
traceability-only baseline
Norm2Proof
```

- Report not only accuracy/F1, but also evidence precision and unsupported-claim rate.
