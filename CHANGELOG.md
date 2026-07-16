# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed

- Claude live-evaluation cases now include marker hardening from observed
  responses, conceptual case isolation, UML calibration guidance, and an adapter
  non-narration rule for internal skill/reference wording
- Claude live-evaluation hardening now rejects confidence-before-percentage
  false passes, strengthens UML evidence-gate workflow ordering from reproduced
  live behavior, and documents the pre-dispatch adapter governance limitation
- Claude live-evaluation response contracts now correct the UML missing-evidence
  marker false negative, add a PFE operational confidence gate, detect narrow
  internal adapter narration, and distinguish pre-dispatch governance from
  post-dispatch instruction adherence
- Claude live-evaluation baseline work now records the first complete matrix,
  hardens UML alternative-validity and direct named-skill narration detection,
  and adds missing-artifact case metadata and response-boundary markers
- Claude adapter evaluation now enforces an explicit UTF-8 subprocess boundary,
  covers the Windows cp1252 crash regression, and configures diagnostic streams
  for UTF-8 where Python supports it
- Claude Code adapter evaluation now observes public stream-json events,
  plugin load state, invocation duration, and diacritic-insensitive markers
- Structured routing decisions expose structural status and ambiguity candidates
- Structured routing no longer adds domain-only supporting capabilities
- Capability registry yield relationships are contextual rules rather than bare capability edges

### Added

- Offline Claude adapter multi-run analytics for JSON live reports, including
  infrastructure classification, run usability, per-case stability summaries,
  text/JSON reporting, and synthetic regression fixtures
- Claude Code adapter evaluation harness for live dispatch and response-contract checks
- Reusable Claude live-evaluation serializer and optional UTF-8 report output
- Missing-lifecycle-evidence UML live regression case for association versus
  composition calibration
- Claude Code reference plugin with five ARF academic skills
- Unified benchmark orchestration API and CLI for routing and conformance suites
- Structural conformance benchmark foundation for implemented ARF object invariants
- Routing regression benchmark foundation for interpretation-to-routing collision scenarios
- Interpretation ontology primitives for RFC-0006 state, provenance, subtasks, and routing conversion
- RFC-0006 request interpretation model for producing structured routing signals
- Structured routing engine for deterministic RFC-0005 ownership decisions
- Capability registry foundation for RFC-0005 ownership and boundary data
- Core ontology primitives for RFC-backed evidence, feedback, confidence, and routing structures
- RFC-0005 routing model for capability selection and skill-collision handling
- RFC-0004 confidence model for qualitative support labels and uncertainty
- RFC-0003 feedback contract for externally reviewable feedback artifacts
- RFC-0002 evidence model for claim support and evidence handling
- RFC-0001 reasoning model for academic and software-engineering analysis
- Repository foundation and governance
- RFC template and writing conventions
- Initial CI workflows
- Project roadmap and architecture
