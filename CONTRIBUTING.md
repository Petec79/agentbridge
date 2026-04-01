# Contributing to agents.json

agents.json is an open standard for agentic commerce. Contributions are welcome from agent developers, e-commerce platform maintainers, and store operators.

## How to Propose Changes

The spec is versioned under [SemVer](https://semver.org/). All changes go through:

1. **Open an issue** — Describe the problem or use case first (don't jump straight to a solution)
2. **Discussion** — The working group discusses. Is this a breaking change? A new endpoint? A schema field?
3. **Pull request** — Propose the spec change with rationale
4. **Adoption** — Reference implementations must be updated alongside the spec
5. **Version bump** — `PATCH` for non-breaking additions, `MINOR` for backward-compatible new features, `MAJOR` for breaking changes

## What Makes a Good Addition

Good additions to agents.json are:
- **Necessary** — Cannot be solved at the application layer with existing fields
- **General** — Applies to all store types, not just one vertical
- **Stable** — We are not adding fields that will change every quarter
- **Implementable** — A store operator should be able to add it without deep technical changes

## CLA

By contributing, you agree that your contributions will be licensed under the Apache 2.0 license.

## Working Group

The agents.json working group meets asynchronously via GitHub issues. All decisions are made in public.

## Contact

- GitHub Issues: https://github.com/agentbridge/agents.json/issues
- Discord: https://discord.gg/agentbridge
