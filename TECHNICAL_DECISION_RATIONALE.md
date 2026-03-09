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

