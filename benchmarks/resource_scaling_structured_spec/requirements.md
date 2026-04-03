# Resource Scaling Structured-Spec Requirements

This bundle is the front-half-first counterpart to the existing
`resource_scaling` benchmark.

The structured-spec input should support a generated system that:

1. produces one scaling decision for each metrics snapshot
2. keeps threshold logic explicit and reviewable
3. preserves compliance blocking rules instead of hiding them in prompts
4. records the final decision entry and rolling decision store deterministically
5. remains decomposable into bounded packets rather than one opaque whole-task module

The reference back-half evaluation assets remain in `../resource_scaling/`.
