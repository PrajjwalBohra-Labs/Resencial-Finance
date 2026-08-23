# Resencial Finance — Advanced Master Project Checklist

> **Purpose:** Durable project roadmap for building Resencial Finance into a robust, production-grade Indian financial research platform.
>
> **Current verified backend baseline:** **283 passed**
>
> **Current verified research milestone:** **Phase 16.6.24 complete**

---

# 0. Project Operating Rules

- [ ] Keep this checklist in the project repository root.
- [ ] Every phase has an entry condition, implementation scope, tests, and exit condition.
- [ ] Do not delete or weaken tests to make a new change pass.
- [ ] Preserve behavior unless a migration is intentional and documented.
- [ ] Record the full backend test count after every major phase.
- [ ] Keep external provider implementations behind typed contracts.
- [ ] Normalize external data before it reaches domain/evidence models.
- [ ] Preserve evidence provenance through the entire research pipeline.
- [ ] Keep deterministic calculations in backend code, not inside the LLM.
- [ ] Never invent missing evidence.
- [ ] Never expose secrets in logs, prompts, tests, or API responses.
- [ ] Keep deterministic test doubles separate from production provider integrations.

---

# 1. Current Verified State

## 1.1 Backend foundation

- [x] Backend application structure established.
- [x] Domain models established.
- [x] Pydantic validation established.
- [x] Core exception hierarchy established.
- [x] Provider abstraction/base contracts established.
- [x] Market provider/service foundation established.
- [x] Fundamentals provider/service foundation established.
- [x] Backend test infrastructure established.

## 1.2 Research domain

- [x] `ResearchRequest`
- [x] `ResearchContext`
- [x] `ResearchAnswer`
- [x] `ResearchFocus`
- [x] `ResearchSourceRecord`
- [x] `NewsRecord`
- [x] `FilingRecord`
- [x] `MacroObservation`
- [x] `BondRecord`
- [x] `BondYieldRecord`

## 1.3 Evidence architecture

- [x] `Evidence`
- [x] `EvidenceSource`
- [x] `EvidenceType`
- [x] Evidence factory
- [x] Market evidence
- [x] Fundamental evidence
- [x] News evidence
- [x] Filing evidence
- [x] Regulatory evidence
- [x] Macro evidence
- [x] Bond evidence
- [x] Bond-yield evidence

## 1.4 Evidence ports/adapters

- [x] Market evidence port
- [x] News evidence port
- [x] Filing evidence port
- [x] Macro evidence port
- [x] Bond evidence port
- [x] Market adapter
- [x] Fundamental adapter
- [x] News adapter
- [x] Filing adapter
- [x] Macro adapter
- [x] Bond adapter

## 1.5 Research assembly/retrieval

- [x] Focus routing
- [x] Multi-source evidence assembly
- [x] Benchmark evidence handling
- [x] Analytical findings
- [x] Evidence retrieval
- [x] Retrieval ranking
- [x] Retrieval filtering
- [x] Retrieval context construction
- [x] Context deduplication
- [x] Context budget
- [x] Contextual evidence preservation
- [x] Orchestrator retrieval integration

## 1.6 LLM research pipeline

- [x] Research prompt builder
- [x] Research engine
- [x] Answer validator
- [x] Correction prompt
- [x] Validation result
- [x] API integration
- [x] Integration regression coverage

## 1.7 Current verification

- [x] Full backend suite green
- [x] Current baseline: **283 passed**
- [x] Phase 16.6.24 builder export consistency verified
- [x] No application TODO/FIXME findings in current scan

---

# 2. Phase 16 — Research System Completion

## 2.1 Advanced evidence contracts

- [x] Typed provider contracts
- [x] In-memory research provider
- [x] Evidence ports
- [x] Evidence adapters
- [x] Focus-based routing
- [x] Application composition

## 2.2 Retrieval and context architecture

- [x] Evidence retriever
- [x] Retrieval query model
- [x] Evidence chunk model
- [x] Retrieval result model
- [x] Context builder
- [x] Ranking tests
- [x] Deduplication tests
- [x] Budget tests
- [x] Benchmark/context preservation
- [x] Public package export consistency

## 2.3 Prompt / validation path

- [x] Mixed-evidence prompt coverage
- [x] Mixed-evidence validator coverage
- [x] Research engine regression
- [x] Correction prompt coverage
- [ ] Claim-level evidence attribution
- [ ] Evidence-aware answer citation format
- [ ] Structured unsupported-claim reporting
- [ ] Evidence conflict detection
- [ ] Evidence confidence propagation into validation
- [ ] Source freshness handling in answer generation

## 2.4 Research API

- [x] Request validation
- [x] Research endpoint
- [x] Response model
- [x] Dependency composition
- [x] API tests
- [x] Integration tests
- [ ] Production-grade dependency factory
- [ ] Real external providers
- [ ] Request correlation IDs
- [ ] API rate limiting
- [ ] API observability
- [ ] API authentication/authorization
- [ ] API versioning strategy

---

# 3. Real External Data Providers — Major Remaining Area

> The current advanced research API composition uses `InMemoryResearchProvider`. Replace this only after real provider implementations are complete and contract-tested.

## 3.1 News

- [ ] Select production-grade news provider(s).
- [ ] Implement `NewsProvider`.
- [ ] Company-news retrieval.
- [ ] Search-news retrieval.
- [ ] Date filtering.
- [ ] Deduplication.
- [ ] Published timestamp normalization.
- [ ] Source URL normalization.
- [ ] Provider error handling.
- [ ] Retry/timeout handling.
- [ ] Rate-limit handling.
- [ ] Contract tests.
- [ ] Integration tests.
- [ ] Fallback provider strategy.

## 3.2 Filings

- [ ] Select authoritative filing source(s).
- [ ] Implement `FilingsProvider`.
- [ ] Latest filing retrieval.
- [ ] Filing search.
- [ ] Filing-type normalization.
- [ ] Filing-date normalization.
- [ ] Filing URL provenance.
- [ ] Filing source reliability checks.
- [ ] Retry/timeout handling.
- [ ] Contract tests.
- [ ] Integration tests.
- [ ] Fallback behavior.

## 3.3 Macro

- [ ] Select authoritative Indian macro source(s).
- [ ] Implement `MacroDataProvider`.
- [ ] Series retrieval.
- [ ] Latest observation.
- [ ] Frequency normalization.
- [ ] Unit normalization.
- [ ] Observation-date normalization.
- [ ] Missing-data handling.
- [ ] Retry/timeout handling.
- [ ] Contract tests.
- [ ] Integration tests.
- [ ] Fallback strategy.

## 3.4 Bonds / fixed income

- [ ] Select authoritative Indian fixed-income source(s).
- [ ] Implement `BondDataProvider`.
- [ ] Bond search.
- [ ] Bond details.
- [ ] Bond yield retrieval.
- [ ] Yield observation normalization.
- [ ] Maturity normalization.
- [ ] Coupon normalization.
- [ ] Credit-rating normalization.
- [ ] Retry/timeout handling.
- [ ] Contract tests.
- [ ] Integration tests.
- [ ] Fallback strategy.

---

# 4. Production Provider Composition

- [ ] Environment-aware provider factory.
- [ ] Separate test/dev/prod providers.
- [ ] Provider selection configuration.
- [ ] API credential management.
- [ ] Secret rotation strategy.
- [ ] Provider health checks.
- [ ] Provider capability registry.
- [ ] Provider fallback priority.
- [ ] Provider circuit breakers.
- [ ] Provider rate-limit awareness.
- [ ] Provider request metrics.
- [ ] Provider response metrics.
- [ ] Provider failure metrics.
- [ ] Provider data freshness monitoring.

---

# 5. Evidence Quality and Provenance

## 5.1 Evidence identity

- [ ] Stable evidence IDs independent of list position.
- [ ] Provenance versioning.
- [ ] Source fingerprinting.
- [ ] Duplicate-source detection.
- [ ] Duplicate-content detection.

## 5.2 Provenance

- [x] Provider recorded.
- [x] Source name recorded.
- [x] Retrieval time recorded.
- [x] Published time supported.
- [x] URL supported.
- [ ] Source reliability score.
- [ ] Freshness score.
- [ ] Evidence freshness policy.
- [ ] Evidence expiration policy.
- [ ] Evidence lineage from provider → adapter → answer.

## 5.3 Claim-to-evidence linkage

- [ ] Stable evidence references in generated answers.
- [ ] Claim → evidence mapping.
- [ ] Validation of referenced evidence IDs.
- [ ] API response citation metadata.
- [ ] UI-ready provenance structure.

---

# 6. Research Answer Quality

## 6.1 Numerical correctness

- [x] Daily percentage validation.
- [x] Fundamental number validation.
- [x] Valuation-claim validation.
- [x] Unsupported causal-claim validation.
- [ ] Macro numerical consistency validation.
- [ ] Bond-yield numerical consistency validation.
- [ ] Filing numerical consistency validation.
- [ ] Cross-source numerical conflict validation.

## 6.2 Reasoning quality

- [ ] Fact vs interpretation enforcement.
- [ ] Observation vs causal inference enforcement.
- [ ] Unsupported forward-looking statement detection.
- [ ] Unsupported risk-claim detection.
- [ ] Unsupported valuation-conclusion detection.
- [ ] Unsupported macro causality detection.
- [ ] Unsupported bond-market conclusions.
- [ ] Stale evidence detection.
- [ ] Conflicting-source detection.

## 6.3 Answer correction

- [x] Correction prompt.
- [x] Re-generation path.
- [x] Re-validation.
- [ ] Maximum correction attempts.
- [ ] Correction failure fallback.
- [ ] Validation failure telemetry.
- [ ] Structured validation diagnostics.

---

# 7. Research Focus Completion

## 7.1 General

- [x] General routing.
- [x] Multi-source evidence.
- [ ] General evidence prioritization.
- [ ] General answer-quality benchmark.

## 7.2 Fundamental

- [x] Fundamentals evidence.
- [x] Fundamental validation.
- [ ] Peer-aware fundamentals.
- [ ] Historical fundamental comparison.
- [ ] Fundamental trend detection.

## 7.3 Valuation

- [x] Valuation focus exists.
- [x] Valuation metrics available.
- [ ] Relative valuation.
- [ ] Historical valuation.
- [ ] Peer valuation.
- [ ] Valuation scenario analysis.
- [ ] Valuation-specific validation.

## 7.4 Market

- [x] Market data.
- [x] Benchmark.
- [x] Market analytics.
- [x] Relationship findings.
- [ ] Volatility analytics.
- [ ] Drawdown analytics.
- [ ] Relative-strength analytics.
- [ ] Event-window analysis.

## 7.5 Risk

- [x] Risk focus exists.
- [ ] Risk-factor model.
- [ ] Downside analytics.
- [ ] Concentration analysis.
- [ ] Volatility risk.
- [ ] Liquidity risk.
- [ ] Regulatory/news risk synthesis.

## 7.6 Macro

- [x] Macro focus.
- [x] Macro evidence architecture.
- [ ] Real macro provider.
- [ ] Macro trend analysis.
- [ ] Macro-to-company linkage.
- [ ] Policy transmission analysis.
- [ ] Macro scenario analysis.

## 7.7 Fixed income

- [x] Fixed-income focus.
- [x] Bond evidence.
- [x] Yield evidence.
- [ ] Real bond provider.
- [ ] Yield curve.
- [ ] Duration.
- [ ] Convexity.
- [ ] Spread analysis.
- [ ] Credit risk.
- [ ] Fixed-income scenario analysis.

## 7.8 Comparison

- [x] Comparison focus.
- [x] Multi-symbol support.
- [x] Shared benchmark.
- [x] Relationship findings.
- [ ] Structured peer scorecard.
- [ ] Comparative fundamentals.
- [ ] Comparative valuation.
- [ ] Comparative risk.
- [ ] Comparison ranking.

---

# 8. Research Performance

- [ ] Benchmark request latency.
- [ ] Provider latency.
- [ ] Retrieval latency.
- [ ] Context-building latency.
- [ ] Prompt construction latency.
- [ ] LLM latency.
- [ ] Validation latency.
- [ ] End-to-end latency.
- [ ] Concurrent request testing.
- [ ] High-evidence-volume testing.
- [ ] Large-prompt testing.
- [ ] Timeout budget per pipeline stage.
- [ ] Performance regression suite.

---

# 9. Caching and Persistence

## 9.1 Cache

- [ ] Market-data cache.
- [ ] Fundamentals cache.
- [ ] News cache.
- [ ] Filing cache.
- [ ] Macro cache.
- [ ] Bond cache.
- [ ] Evidence cache.
- [ ] Retrieval cache where useful.

## 9.2 Cache policy

- [ ] TTL per data class.
- [ ] Staleness rules.
- [ ] Cache invalidation.
- [ ] Cache stampede protection.
- [ ] Negative-result caching.
- [ ] Provider-outage behavior.

## 9.3 Persistence

- [ ] Research request persistence.
- [ ] Research answer persistence.
- [ ] Evidence persistence.
- [ ] Analytical finding persistence.
- [ ] Validation-result persistence.
- [ ] Research history.
- [ ] Reproducible historical research snapshots.

---

# 10. Security

- [ ] Authentication.
- [ ] Authorization.
- [ ] Role model.
- [ ] API key security.
- [ ] Secret management.
- [ ] Secret rotation.
- [ ] Input-size limits.
- [ ] Request-rate limiting.
- [ ] SSRF protection for provider URLs.
- [ ] URL allowlisting where needed.
- [ ] Prompt-injection defenses for external evidence.
- [ ] Malicious-content isolation.
- [ ] Sensitive-data redaction.
- [ ] Secure logging.
- [ ] Dependency vulnerability scanning.
- [ ] Security regression tests.

---

# 11. Observability

- [ ] Structured logging.
- [ ] Request ID.
- [ ] Correlation ID.
- [ ] Provider request metrics.
- [ ] Provider failure metrics.
- [ ] Retrieval metrics.
- [ ] Evidence counts.
- [ ] Prompt-size metrics.
- [ ] LLM latency metrics.
- [ ] LLM token usage.
- [ ] Validation failure rate.
- [ ] Correction rate.
- [ ] End-to-end latency.
- [ ] Error rate.
- [ ] Data freshness metrics.
- [ ] Health dashboard.
- [ ] Alerting.

---

# 12. Reliability

- [ ] Provider timeouts.
- [ ] Provider retries.
- [ ] Exponential backoff.
- [ ] Circuit breakers.
- [ ] Fallback providers.
- [ ] Partial-evidence behavior.
- [ ] Partial-provider failure handling.
- [ ] LLM unavailable handling.
- [ ] Validation failure handling.
- [ ] Graceful degradation.
- [ ] Service restart recovery.
- [ ] Idempotent research requests.
- [ ] Recovery jobs where appropriate.

---

# 13. API Maturity

- [x] Research endpoint.
- [x] Request schema.
- [x] Response schema.
- [ ] API versioning.
- [ ] Pagination where needed.
- [ ] Async research jobs for long-running requests.
- [ ] Job status endpoint.
- [ ] Result retrieval endpoint.
- [ ] Request cancellation.
- [ ] Rate limits.
- [ ] Authentication.
- [ ] Authorization.
- [ ] OpenAPI quality review.
- [ ] API error-code standardization.

---

# 14. Data Governance

- [ ] Source licensing review.
- [ ] Provider terms review.
- [ ] Data retention policy.
- [ ] Evidence retention policy.
- [ ] Audit policy.
- [ ] PII review.
- [ ] User-data handling policy.
- [ ] Source attribution policy.
- [ ] Data freshness SLA.
- [ ] Data correctness SLA.

---

# 15. Testing Maturity

## 15.1 Existing

- [x] Domain unit tests.
- [x] Provider contract tests.
- [x] Adapter tests.
- [x] Assembler tests.
- [x] Retrieval tests.
- [x] Context builder tests.
- [x] Prompt builder tests.
- [x] Validator tests.
- [x] Engine tests.
- [x] Orchestrator tests.
- [x] API tests.
- [x] Integration tests.

## 15.2 Next-level

- [ ] Real-provider contract tests.
- [ ] Failure-injection tests.
- [ ] Timeout tests.
- [ ] Retry tests.
- [ ] Rate-limit tests.
- [ ] Concurrency tests.
- [ ] Load tests.
- [ ] Security tests.
- [ ] Mutation testing.
- [ ] Property-based testing for normalization/retrieval.
- [ ] Prompt snapshot tests where useful.
- [ ] Golden-answer regression suite.
- [ ] Cross-source conflict regression suite.

---

# 16. LLM Evaluation

- [ ] Golden research questions.
- [ ] Expected evidence coverage.
- [ ] Numerical correctness scoring.
- [ ] Citation/provenance scoring.
- [ ] Unsupported-claim scoring.
- [ ] Causal-inference scoring.
- [ ] Completeness scoring.
- [ ] Readability scoring.
- [ ] Focus-specific evaluation sets.
- [ ] Regression evaluation before model/provider changes.
- [ ] Prompt A/B framework.
- [ ] Model comparison framework.

---

# 17. Frontend / User Experience

> Verify actual frontend scope before implementation if it is not yet part of the repository.

- [ ] Research request screen.
- [ ] Symbol selector.
- [ ] Exchange selector.
- [ ] Focus selector.
- [ ] Date range selector.
- [ ] Research progress state.
- [ ] Research answer view.
- [ ] Evidence panel.
- [ ] Evidence source links.
- [ ] Evidence-type filtering.
- [ ] Analytical findings panel.
- [ ] Validation warnings.
- [ ] Limitations display.
- [ ] Research history.
- [ ] Research comparison view.
- [ ] Export/share.
- [ ] Responsive design.
- [ ] Accessibility.
- [ ] Error states.
- [ ] Empty states.

---

# 18. Research User Workflows

- [ ] Single-company research.
- [ ] Multi-company comparison.
- [ ] Fundamental analysis.
- [ ] Valuation analysis.
- [ ] Market analysis.
- [ ] Risk analysis.
- [ ] Macro analysis.
- [ ] Fixed-income analysis.
- [ ] News-driven research.
- [ ] Filing-driven research.
- [ ] Date-bounded historical research.
- [ ] Follow-up question workflow.
- [ ] Saved research.
- [ ] Re-run research.
- [ ] Compare research runs.
- [ ] Research provenance inspection.

---

# 19. Deployment

- [ ] Production Dockerfile.
- [ ] Production environment variables.
- [ ] Secrets integration.
- [ ] Database deployment.
- [ ] Cache deployment.
- [ ] Queue/background worker if needed.
- [ ] API deployment.
- [ ] Frontend deployment.
- [ ] Reverse proxy.
- [ ] TLS.
- [ ] Health checks.
- [ ] Readiness checks.
- [ ] Graceful shutdown.
- [ ] Horizontal scaling.
- [ ] Autoscaling policy.
- [ ] Backups.
- [ ] Restore procedure.
- [ ] Disaster recovery plan.

---

# 20. CI/CD

- [ ] Lint gate.
- [ ] Type-check gate.
- [ ] Unit-test gate.
- [ ] Integration-test gate.
- [ ] Security scan.
- [ ] Dependency scan.
- [ ] Build verification.
- [ ] Migration verification.
- [ ] Container scan.
- [ ] Staging deployment.
- [ ] Smoke tests.
- [ ] Production approval gate.
- [ ] Automated rollback.

---

# 21. Documentation

- [ ] README architecture overview.
- [ ] Local development guide.
- [ ] Environment configuration guide.
- [ ] Provider integration guide.
- [ ] Evidence architecture guide.
- [ ] Retrieval architecture guide.
- [ ] Research pipeline diagram.
- [ ] API documentation.
- [ ] Data-source documentation.
- [ ] Troubleshooting guide.
- [ ] Operations/runbook.
- [ ] Incident-response guide.
- [ ] Deployment guide.
- [ ] Security guide.
- [ ] Contribution guide.
- [ ] Architecture decision records.

---

# 22. Production Readiness Gate

Do not declare the system production-ready until all of the following are checked:

- [ ] Real external providers implemented.
- [ ] Provider fallbacks tested.
- [ ] Secrets secured.
- [ ] Authentication enabled.
- [ ] Authorization enabled.
- [ ] Rate limiting enabled.
- [ ] Structured logging enabled.
- [ ] Metrics and alerts enabled.
- [ ] Persistence implemented.
- [ ] Caching implemented where needed.
- [ ] Performance targets met.
- [ ] Security review complete.
- [ ] Data-source/licensing review complete.
- [ ] Golden LLM evaluation suite green.
- [ ] End-to-end tests green.
- [ ] Disaster recovery tested.
- [ ] Deployment rollback tested.
- [ ] Production smoke tests green.

---

# 23. Recommended Execution Order From Current State

## NOW — 16.6.23 / API hardening

- [x] Research pipeline baseline
- [x] Prompt integration
- [x] Validator integration
- [x] Builder export consistency
- [ ] API mixed-evidence response coverage
- [ ] API validation-response coverage
- [ ] API provenance-response coverage

## NEXT — 16.7 / Real research providers

- [ ] News provider
- [ ] Filings provider
- [ ] Macro provider
- [ ] Bond provider
- [ ] Provider factory
- [ ] Provider configuration
- [ ] Provider reliability
- [ ] Integration suite

## THEN — 17 / Production research quality

- [ ] Provenance
- [ ] Claim/evidence links
- [ ] Advanced validation
- [ ] Evidence conflict handling
- [ ] LLM evaluation
- [ ] Performance
- [ ] Caching

## THEN — 18 / Security + reliability

- [ ] Authentication
- [ ] Authorization
- [ ] Rate limiting
- [ ] Secure secrets
- [ ] Circuit breakers
- [ ] Observability
- [ ] Disaster recovery

## THEN — 19 / Persistence

- [ ] Database
- [ ] Research history
- [ ] Evidence persistence
- [ ] Cache persistence
- [ ] Reproducible research snapshots

## THEN — 20 / Product experience

- [ ] Research UI
- [ ] Evidence UI
- [ ] Source/provenance UX
- [ ] Research history
- [ ] Comparison workflows
- [ ] Export/share

## FINAL — 21 / Production launch

- [ ] CI/CD
- [ ] Staging
- [ ] Production
- [ ] Load testing
- [ ] Security sign-off
- [ ] Data/licensing sign-off
- [ ] Operational runbook
- [ ] Production smoke test
- [ ] Go-live checklist
- [ ] Post-launch monitoring

---

# 24. Current Project Gate

**Verified checkpoint:**

```text
Backend tests: 283 passed
Phase 16.6.24: COMPLETE
Research/retrieval architecture: GREEN
```

**Highest-priority unfinished engineering item:**

```text
Replace deterministic advanced research-provider composition
with real external News / Filings / Macro / Bond providers,
while preserving the existing provider ports, adapters,
retrieval, prompt, validation, and regression contracts.
```

**Roadmap rule:** `[x]` means verified complete; `[ ]` means not yet verified complete. This file intentionally includes future production and product work beyond the current repository state.
