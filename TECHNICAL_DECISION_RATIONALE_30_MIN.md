# Lean Hub Technical Decisions — 30 Minute Presentation Guide

This file is a ready-to-present 30-minute version of the architecture rationale.
It includes timing, what to say, what to show, and key technical messages.

## 0) Session Goal (0:00 - 1:00)

### Objective
- Explain why Lean Hub chose this architecture.
- Show trade-offs and risk controls.
- Show why Cloud Run + Docker is the right fit now (and when Kubernetes becomes appropriate).

### Opening line
- "This is a deliberate architecture: optimized for delivery speed, operational safety, and cost efficiency under variable load."

---

## 1) Problem and Constraints (1:00 - 4:00)

### Slide: Problem Statement

### Say
- We needed independent service delivery with centralized security and observability.
- We had mixed workloads (light APIs + heavier RAG service profile).
- We needed reproducibility and controlled rollout of shared dependencies.

### Show
- Requirement pillars: speed, isolation, security, observability, cost.

### Key technical takeaway
- This is not just app design; it is runtime + release + operations design.

---

## 2) Why Not On-Premises (4:00 - 7:00)

### Slide: Rejected Option — On-Prem

### Say
- On-prem shifts effort from product engineering to platform operations too early.
- Capacity must be sized for peak; idle cost remains high.
- GPU lifecycle and infra maintenance overhead are disproportionate for this stage.

### Technical points
- Control-plane burden: ingress/auth/certs/routing.
- Reliability burden: patching, HA/DR, node lifecycle.
- Observability burden: full stack ownership and governance.

### Key takeaway
- On-prem is valid at scale for some orgs, but not optimal for this platform phase.

---

## 3) Why GCP (7:00 - 10:00)

### Slide: Platform Fit

### Say
- We selected managed components that map directly to our boundaries.

### Component mapping
- Cloud Run: stateless service runtime.
- API Gateway: centralized auth + routing.
- Firebase Auth: token ecosystem.
- Cloud Logging/Trace/Monitoring: unified telemetry.
- IAM + service accounts: least-privilege automation.
- Artifact Registry: immutable image provenance.

### Key takeaway
- GCP reduced undifferentiated platform work while preserving control where needed.

---

## 4) Why Microservices + API Gateway (10:00 - 14:00)

### Slide: Service Decomposition + Entry Point

### Say
- We split by workload boundary and deployment boundary, not by arbitrary team preference.
- Gateway decouples client contract from backend runtime churn.

### Technical benefits
- Independent scaling and rollback.
- Fault isolation.
- Stable public interface despite internal revision changes.
- Centralized policy enforcement.

### Trade-off
- Distributed complexity increases; must be offset by strong CI/CD and telemetry.

---

## 5) Why Cloud Run + Docker, Not Kubernetes (14:00 - 18:00)

### Slide: Runtime Decision Boundary

### Say
- We keep Docker benefits (immutability, portability) without Kubernetes control-plane overhead.
- Cloud Run gives fast build-to-live and native scale-to-zero economics.

### Why not Kubernetes now
- Kubernetes adds operational and cognitive load: cluster lifecycle, networking policy, scheduling, add-on stack management.
- Current workloads are stateless HTTP services that do not need advanced orchestration primitives yet.

### When Kubernetes becomes justified
- Complex mesh policy, custom controllers, dense heterogeneous scheduling, advanced stateful orchestration, multi-region active-active cluster operations.

### Key takeaway
- Deferred, not rejected: Kubernetes is a future option behind a clear decision threshold.

---

## 6) Delivery Strategy: Monorepo + Surgical CI/CD (18:00 - 21:00)

### Slide: Deployment Model

### Say
- Monorepo keeps shared contracts + services + infrastructure in one change graph.
- Path-based workflows deploy only what changed.

### Technical outcomes
- Reduced blast radius.
- Faster pipelines.
- Better change traceability.
- Less rebuild waste.

### Key takeaway
- Delivery architecture is a first-class reliability mechanism.

---

## 7) Shared Library Governance: Pinning + Tags (21:00 - 24:00)

### Slide: Deterministic Dependency Model

### Say
- Each service pins a shared-lib version.
- Build resolves shared_libs from immutable tag, not mutable branch state.

### Benefits
- Reproducible builds.
- Controlled service-by-service adoption.
- Deterministic rollback.
- Forensic traceability from runtime to exact shared-lib release.

### Important caveat
- Service code must match pinned shared-lib API surface (new imports require pin bump).

---

## 8) Security and Observability (24:00 - 28:00)

### Slide: Defense-in-Depth + Three Pillars

### Security points
- Least-privilege IAM.
- Gateway auth policy.
- Runtime invocation controls.
- Secret isolation in CI.
- Audit logging for privileged activity.

### Observability points
- Structured JSON logs for queryability.
- Traces for latency topology and critical path.
- Metrics for trend/SLO visibility.

### Trace ID vs Correlation ID
- Trace ID: span topology and timing.
- Correlation ID: transaction stitching across boundaries and multi-step flows.

### Key takeaway
- Reliability depends on both prevention (security controls) and diagnosis (telemetry quality).

---

## 9) Conclusion and Q&A (28:00 - 30:00)

### Slide: Executive Summary

### Say
- This architecture is intentionally pragmatic: managed where possible, explicit where critical.
- It maximizes engineering throughput while controlling operational risk.
- It preserves a clean evolution path toward more complex orchestration when the workload truly requires it.

### Final close
- "We optimized for the current reality and kept the future migration path open."

---

## Appendix A: Suggested Slide List (19 Slides)

1. Title and context  
2. Problem statement  
3. Constraints and non-functional requirements  
4. Why not on-prem  
5. Why GCP  
6. High-level architecture  
7. Why microservices  
8. Why API Gateway  
9. Why Cloud Run + Docker  
10. Why not Kubernetes (yet)  
11. Monorepo + surgical CI/CD  
12. Shared library pinning  
13. Git tag immutability model  
14. Security layers  
15. Logs / traces / metrics model  
16. Correlation ID vs Trace ID  
17. Dashboard and operations visibility  
18. Trade-offs and risk controls  
19. Executive conclusion

## Appendix B: Presenter Tips

- Keep each slide to one technical thesis.
- Use one architecture diagram repeatedly; highlight different layers instead of switching diagrams.
- For every decision slide, state: "Decision", "Why", "Trade-off", "Boundary for re-evaluation."
- Keep Kubernetes discussion factual and threshold-based, not ideological.

