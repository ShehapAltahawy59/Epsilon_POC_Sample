# Lean Hub Technical Decision Rationale

This document explains why each major architecture and delivery decision was made for Lean Hub, from the first strategic choice (cloud vs on-premises) through runtime, security, deployment, and observability.

The goal is not to describe "how to run commands," but to justify the design from an engineering, operations, security, and cost perspective.

## 1) Why We Did Not Choose On-Premises

On-premises infrastructure was intentionally rejected because the system requirements favor elasticity, managed control planes, and rapid iteration over static capacity and infrastructure ownership.

Key technical reasons:

- Elasticity mismatch: request load and service activity are bursty. On-prem requires overprovisioning for peak, causing persistent idle capacity.
- GPU lifecycle burden: RAG workloads need accelerators that are expensive to procure, difficult to refresh, and operationally heavy to schedule efficiently on-prem.
- Control-plane complexity: secure ingress, API management, identity federation, certificate lifecycle, and distributed routing all require additional platform components when self-hosted.
- Reliability engineering overhead: patching, kernel hardening, node replacement, storage redundancy, and disaster recovery become first-class platform work.
- Observability stack ownership: distributed tracing, centralized logs, metrics indexing, retention policies, and alerting pipelines require separate systems and operational staff.
- Slower delivery velocity: every environment and capability (networking, IAM, monitoring, scaling) must be built and operated before application features can ship.
- Cost profile misalignment: fixed-capex + ongoing-ops does not fit a POC that benefits from scale-to-zero and pay-for-use.

Conclusion: on-prem would shift effort from product engineering to platform engineering without providing proportional value for this architecture.

## 2) Why Google Cloud Platform (GCP)

GCP was selected as a managed execution and operations substrate, minimizing undifferentiated infrastructure work.

Core selection drivers:

- Managed serverless runtime (Cloud Run) for fast deployment and automatic scaling.
- Native API Gateway for centralized auth, routing, and policy enforcement.
- Firebase Auth for token issuance/validation with strong client ecosystem support.
- Unified observability stack (Cloud Logging, Cloud Trace, Cloud Monitoring) with low integration friction.
- Strong IAM model for least-privilege service identity and controlled automation.
- Artifact Registry for immutable image storage and deployment traceability.
- Consistent API-driven automation surface compatible with GitHub Actions.

This combination supports independent service delivery while preserving operational consistency.

## 3) Why Microservices Instead of a Single Monolith

The workload naturally partitions into separate domains (simple API services and RAG service with different resource profile). Microservices were chosen for operational independence.

Benefits:

- Independent scaling per workload type.
- Fault isolation between services.
- Independent deployment cadence and rollback scope.
- Different runtime envelopes (memory/CPU/GPU profile) per service.
- Clear service ownership boundaries.

Trade-off accepted: distributed-system complexity is higher, so automation and observability are mandatory, not optional.

## 4) Why a Single API Gateway Entry Point

A single gateway was chosen to separate client-facing concerns from service internals.

Technical advantages:

- Centralized authentication and token validation.
- Stable public API surface even when backend revisions or URLs change.
- Consistent routing policy and versioning strategy.
- Reduced direct exposure of backend services.
- Single place to enforce traffic controls and policy.

This also decouples client integrations from backend deployment churn.

## 5) Why Cloud Run for Service Runtime

Cloud Run was selected over VM-centric or cluster-centric models for this stage.

Reasons:

- Stateless container deployment with minimal platform operations.
- Automatic horizontal scaling and scale-to-zero.
- Revision-based rollout model for safer updates.
- Integrated request/latency telemetry and platform logs.
- Fast build-to-live cycle with straightforward CI/CD integration.

Cloud Run provides the best time-to-operational-production ratio for this architecture.

## 5.1) Why Cloud Run + Docker Instead of Kubernetes

Kubernetes was evaluated, but not selected for this phase because the platform goals prioritize delivery speed, operational simplicity, and low idle cost over maximum orchestration flexibility.

Why Cloud Run + Docker was chosen:

- Container portability retained: Docker images provide the same packaging, immutability, and dependency isolation benefits regardless of runtime target.
- No cluster control-plane management: no node pools, scheduler tuning, upgrades, CNI policy management, or cluster lifecycle operations.
- Lower operational surface area: fewer failure domains to diagnose compared to pods/nodes/controllers/ingress stacks.
- Faster release cycle: build and deploy path is shorter (image -> revision) without Kubernetes manifests, Helm/Kustomize layering, or admission policy orchestration.
- Native scale-to-zero economics: Cloud Run minimizes idle spend automatically for intermittent workloads.
- Simpler security model for this scope: service IAM + gateway policy is sufficient without introducing full Kubernetes RBAC/network-policy/service-mesh complexity.
- Team efficiency: engineering time is spent on service behavior and observability rather than platform administration.

Why Kubernetes was deferred (not rejected permanently):

- Kubernetes is strongest when workloads require advanced orchestration primitives (daemonsets, statefulsets, custom controllers, complex intra-cluster networking, sidecar/service-mesh patterns at scale).
- Current Lean Hub workloads are stateless HTTP services with straightforward routing and managed dependencies, which do not justify early Kubernetes overhead.
- Introducing Kubernetes too early would increase cognitive and operational load without proportional reliability or performance gains for current traffic and architecture complexity.

Decision boundary:

- If requirements evolve toward multi-region active-active cluster orchestration, dense bin-packing of heterogeneous workloads, deep mesh policy control, or extensive custom operators, Kubernetes can become the next-step platform.
- Until that threshold is reached, Cloud Run + Docker remains the most cost-effective and technically appropriate runtime choice.

## 6) Why Monorepo + Surgical CI/CD

A monorepo was chosen to keep shared contracts, services, and infrastructure in one transactional change space.

Surgical deployment logic (path-scoped workflows) was chosen to avoid unnecessary rebuilds and reduce risk.

Impact:

- Smaller deployment blast radius.
- Lower build minutes and faster pipeline completion.
- Better developer feedback loop.
- Easier change audit across services and shared components.

## 7) Why Shared Library Version Pinning (Not "Always Latest")

The shared library is versioned and pinned per service to guarantee reproducibility and controlled adoption.

Why this matters:

- Prevents accidental runtime drift when shared utilities change.
- Enables canary-style adoption at service granularity.
- Supports deterministic rollback to known-good dependency sets.
- Preserves release safety across independently deployed services.

This is essential for multi-service systems where "latest" can become an unbounded operational risk.

## 8) Why Git Tag-Based Immutable Shared Library Releases

Git tags were chosen as immutable version anchors for shared library snapshots.

Technical rationale:

- Immutable reference model for builds.
- Clear provenance between deployed service revision and library state.
- Traceable release boundaries for incident forensics.
- Works natively with existing GitHub/Git workflows and CI automation.

Per-project version files define intent; tags define immutable artifact identity.

## 9) Why Secrets in GitHub Actions Secrets (and Not in Repo)

Secret material is intentionally kept outside source control and injected at runtime.

Reasons:

- Prevents credential leakage via repository history.
- Supports rotation without code changes.
- Maintains environment isolation and least exposure.
- Aligns with CI identity model for ephemeral execution contexts.

Service-account scope and role assignment are explicitly constrained to deployment needs.

## 10) Why Defense-in-Depth Security

Security is layered rather than relying on a single control.

Layers:

- Identity and access control via IAM roles and service identities.
- Gateway-level token validation and centralized auth policy.
- Runtime invocation controls on backend services.
- Secret isolation and non-persistent credential handling in automation.
- Audit logging of privileged operations.

This design reduces the impact of single-point failures in authentication, networking, or automation.

## 11) Why Structured JSON Logging

Structured logging was chosen because distributed debugging requires queryable fields, not free-form text.

Operational value:

- Field-level filtering (service, endpoint, request metadata).
- Consistent schema across services.
- Easier automation for log-based metrics and alerts.
- Better incident triage and root-cause acceleration.

Free-form logs were considered insufficient for cross-service diagnostics.

## 12) Why Trace + Correlation ID Together

Trace and correlation are complementary, not redundant.

- Trace ID: request-lifecycle timing and span topology within tracing systems.
- Correlation ID: cross-boundary business transaction key across logs, async edges, and service hops.

Using both enables:

- Topology/timing analysis in tracing tools.
- End-to-end forensic reconstruction in logging tools.

This dual model is particularly important as the architecture evolves toward asynchronous or multi-step workflows.

## 13) Why a Centralized Monitoring Dashboard

A single dashboard was chosen to expose system health across services in one place.

Benefits:

- Fast operator situational awareness.
- Uniform SLI visibility across service boundaries.
- Easier handoff between development and operations.
- Reduced mean time to detect anomalies.

Dashboard standardization also improves onboarding and reduces diagnostic variance between engineers.

## 14) Why the Delivery Process Is Sequenced the Way It Is

The implementation process follows a dependency-safe order:

1. Establish cloud foundation and IAM first to prevent blocked automation.
2. Configure secrets before CI execution to avoid failed deploy loops.
3. Deploy services before gateway finalization so route targets are resolvable.
4. Apply observability after runtime availability so telemetry has signal.
5. Version and pin shared dependencies before broad rollout to preserve determinism.

This sequence minimizes rework, avoids circular dependencies, and improves first-pass success rate.

## 15) Trade-Offs We Intentionally Accepted

No architecture is free of trade-offs. The chosen model accepts:

- Greater distributed complexity in exchange for service independence.
- CI/CD workflow complexity in exchange for safer, smaller deployments.
- Version management overhead in exchange for deterministic releases.
- Additional observability components in exchange for faster failure isolation.

These trade-offs are deliberate and aligned with reliability and release goals.

## 16) Decision Summary

The architecture choices are optimized for:

- Fast and safe iteration.
- Reproducible deployments.
- Strong operational visibility.
- Controlled security posture.
- Cost efficiency under variable load.

In short: the platform is intentionally designed to maximize engineering throughput while reducing operational and security risk in a multi-service cloud environment.

## 17) Slide-Ready Presentation Structure

This section is a deck blueprint you can copy directly into presentation slides.

### Slide 1: Title and Context

**Title:** Lean Hub Architecture Decisions  
**Subtitle:** Why this platform design was chosen, what trade-offs were accepted, and how it scales.

**Key message:**
- The architecture is intentionally optimized for speed, reliability, security, and cost efficiency in a multi-service cloud model.

**Suggested visual:**
- One high-level architecture diagram (gateway, three services, shared libs, observability stack).

### Slide 2: Problem Statement

**Title:** What We Needed to Solve

**Key message:**
- Deliver independent services quickly without sacrificing observability, security, or operational control.

**Technical drivers:**
- Heterogeneous workloads (simple APIs + heavier RAG service).
- Need for independent deployment and rollback.
- Need for stable external API despite backend change.
- Need for strong production telemetry from day one.

**Suggested visual:**
- Four requirement pillars: Delivery Speed, Isolation, Security, Observability.

### Slide 3: Why Not On-Premises

**Title:** Rejected Option: On-Prem

**Key message:**
- On-prem introduces platform-heavy work that slows product delivery.

**Technical reasons:**
- Capacity planning must cover peak demand (idle waste).
- Accelerator lifecycle (GPU procurement, scheduling, replacement) is heavy.
- Extra control planes required for ingress, auth, certs, and routing.
- Full ownership of reliability stack (patching, HA, DR, node lifecycle).
- Full ownership of telemetry stack and retention governance.

**Suggested visual:**
- "Engineering focus split" chart: Product vs Platform effort.

### Slide 4: Why GCP

**Title:** Cloud Platform Selection Rationale

**Key message:**
- GCP gave managed primitives aligned with our architecture boundaries.

**Technical fit:**
- Cloud Run: stateless service runtime with autoscaling.
- API Gateway: centralized auth/routing policy.
- Firebase Auth: token ecosystem + gateway validation support.
- Logging/Trace/Monitoring: unified operational telemetry.
- IAM + service accounts: least-privilege automation model.
- Artifact Registry: immutable image provenance.

**Suggested visual:**
- Capability-to-requirement matrix.

### Slide 5: Why Microservices

**Title:** Service Decomposition Strategy

**Key message:**
- Workload and release independence justified service separation.

**Benefits:**
- Independent scaling envelopes.
- Smaller rollback blast radius.
- Fault containment between domains.
- Team and release autonomy.

**Trade-off:**
- Higher distributed-system complexity accepted and mitigated via automation + observability.

### Slide 6: Why API Gateway

**Title:** Single Entry Point Design

**Key message:**
- Gateway centralizes identity, routing, and policy while decoupling clients from backend churn.

**Technical outcomes:**
- Stable external contract.
- Centralized JWT validation.
- Path-based backend routing.
- Easier service URL rotation handling.

**Suggested visual:**
- Before/after diagram: direct service exposure vs gateway front-door.

### Slide 7: Why Cloud Run + Docker (Not Kubernetes)

**Title:** Runtime Decision Boundary

**Key message:**
- Cloud Run + Docker provides container immutability and portability without Kubernetes control-plane overhead.

**Why now:**
- Faster build-to-live path.
- No cluster ops (node pools/upgrades/scheduler networking complexity).
- Scale-to-zero cost profile.
- Lower SRE cognitive load for current requirements.

**When to revisit Kubernetes:**
- Advanced orchestration needs (custom controllers, deep mesh policy, dense heterogeneous scheduling, complex stateful operational model).

### Slide 8: Why Monorepo + Surgical CI/CD

**Title:** Delivery Pipeline Strategy

**Key message:**
- Keep shared contracts and services in one change graph while deploying only what changed.

**Technical mechanism:**
- Path-scoped workflow triggers.
- Service-specific rebuild/deploy.
- Reduced pipeline duration and lower deployment risk.

**Operational effect:**
- Faster feedback loops.
- Fewer unnecessary deployments.
- Better forensic traceability of cross-service changes.

### Slide 9: Why Shared Library Pinning

**Title:** Dependency Stability Model

**Key message:**
- Service-level pinning prevents accidental dependency drift.

**Technical benefits:**
- Reproducible builds.
- Controlled adoption by service.
- Deterministic rollback.
- Safer canary adoption patterns for shared utilities.

**Important caveat:**
- Service code and pinned shared version must be compatible; new imports require pin bumps.

### Slide 10: Why Git Tags for Shared Library Releases

**Title:** Immutable Release Anchors

**Key message:**
- Tags provide immutable references that map deployed images to exact dependency state.

**Technical advantages:**
- Provenance and auditability.
- Repeatable rebuild behavior.
- Clear release boundaries for incident analysis.

### Slide 11: Security Architecture

**Title:** Defense-in-Depth Controls

**Key message:**
- Security posture is layered so no single control is a hard dependency.

**Layers:**
- IAM service identity and least privilege.
- Gateway-level authentication policy.
- Runtime invocation controls.
- Secret isolation in CI.
- Audit logs for privileged operations.

**Suggested visual:**
- Layered shield diagram.

### Slide 12: Observability Strategy

**Title:** Logs, Traces, Metrics — Complementary Roles

**Key message:**
- Telemetry is designed for both rapid detection and deep diagnosis.

**Roles:**
- Logs: semantic event evidence and context.
- Traces: latency topology and critical path.
- Metrics: aggregate trend and SLO health.

**Correlation model:**
- Trace ID for request-span topology.
- Correlation ID for cross-boundary transaction stitching.

### Slide 13: Why Correlation ID + Trace ID

**Title:** Non-Redundant Identifiers

**Key message:**
- Trace IDs and correlation IDs solve different observability problems.

**Trace ID is best for:**
- Span timing analysis within traced request graphs.

**Correlation ID is best for:**
- Reconstructing end-to-end business workflows across multiple requests/asynchronous boundaries.

### Slide 14: Monitoring Dashboard Design

**Title:** Operational Visibility at a Glance

**Key message:**
- Dashboard standardization reduces time-to-detect and accelerates incident triage.

**What operators need first:**
- Traffic level and error profile.
- Latency behavior.
- Runtime capacity indicators.
- Resource utilization and cost signals.

### Slide 15: Delivery Sequence Rationale

**Title:** Why the Rollout Order Matters

**Key message:**
- Sequence is designed to eliminate dependency deadlocks and reduce rework.

**Order and reason:**
1. Foundation + IAM first (enables all automation).
2. Secrets before CI execution (avoid auth failures).
3. Services before gateway finalization (valid route targets).
4. Observability after runtime signal exists.
5. Version pinning before broad shared-lib rollout.

### Slide 16: Trade-Offs and Risk Register

**Title:** What We Accepted Deliberately

**Accepted trade-offs:**
- More distributed complexity for better service independence.
- More pipeline logic for lower release risk.
- More version governance for deterministic builds.

**Risk controls:**
- Automation guardrails.
- Immutable tagging.
- Structured telemetry and auditability.

### Slide 17: Measurable Outcomes

**Title:** Expected Engineering and Operations Outcomes

**Outcomes to highlight:**
- Reduced deployment blast radius.
- Faster mean time to detect and isolate issues.
- Stronger release reproducibility.
- Improved developer throughput.
- Better idle-cost profile for bursty workloads.

### Slide 18: Future Evolution Path

**Title:** Architecture Decision Horizon

**Near-term focus:**
- Harden SLOs/alerts and incident playbooks.
- Expand tracing depth and async propagation coverage.
- Improve dependency release governance.

**Potential platform pivot triggers:**
- Need for advanced orchestration primitives.
- Multi-region active-active complexity.
- Mesh-level policy requirements at larger scale.

### Slide 19: Executive Conclusion

**Title:** Why This Architecture Is the Right Fit Now

**Final message:**
- The platform balances speed, safety, and cost with strong technical controls.
- It is intentionally pragmatic: managed where possible, explicit where critical.
- It preserves a clean migration path to more complex orchestration only when justified by scale and requirement complexity.

## 18) Presenter Notes (Concise Talking Script)

Use this as a short verbal script while presenting:

- "We chose cloud over on-prem to avoid spending engineering cycles on platform plumbing instead of product delivery."
- "We chose managed components that map directly to our boundaries: runtime, gateway, identity, artifacts, and telemetry."
- "Microservices were selected for operational independence, and we deliberately paid that complexity cost by investing in CI/CD and observability."
- "Cloud Run + Docker gave us immutable containers without cluster operations overhead."
- "Shared library pinning and tag immutability are central to deterministic releases and safe selective upgrades."
- "Trace IDs and correlation IDs are both required because they answer different operational questions."
- "This architecture is intentionally designed for current scale and includes a clear threshold for when Kubernetes becomes justified."
