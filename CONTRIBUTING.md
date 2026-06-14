# Contributing To Pseudonymity

Pseudonymity is a v1 privacy engineering toolkit. Contributions should keep a clear distinction between implemented guarantees, design intent and future roadmap.

## Development Setup

```powershell
bash scripts/check.sh
```

Optional Go component:

```powershell
bash scripts/build-go-risk.sh
```

## Contribution Guidelines

- Keep transformations profile-driven where possible.
- Do not add cryptographic primitives from scratch when mature libraries are available.
- Document the threat model for each new technique.
- Add tests for new CLI behaviour and library APIs.
- Do not commit real personal data, secrets, vaults or production profiles.
- Be explicit about whether a technique is reversible, linkable, deterministic or lossy.

## Adding A Technique

1. Add the implementation to `pseudonymity.techniques`.
2. Add profile syntax documentation in `docs/profile_schema.md`.
3. Add tests covering happy path and invalid configuration.
4. Update the README technique table.
5. Update the manifest output if the technique needs new metadata.
