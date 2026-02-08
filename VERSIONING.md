# CRE Kernel — Versioning Policy

This document defines how CRE Kernel versions are assigned,
what guarantees each version provides, and how breaking changes are handled.

The goal is **stability at the kernel layer** and **freedom to evolve safely**.

---

## 1. Versioning Scheme

CRE Kernel follows a **semantic-style versioning** model:

MAJOR.MINOR.PATCH

Example:
- `v1.0.0`
- `v1.1.0`
- `v1.1.3`
- `v2.0.0`

---

## 2. Meaning of Each Version Level

### 🔴 MAJOR version (v1 → v2)

Incremented when:
- Kernel invariants change
- Core trust model changes
- Ledger semantics change
- Consensus rules change
- Backward compatibility is broken

Guarantee:
- **MAJOR versions may break adapters**
- Migration docs will be provided when possible

Example:

v1.x → v2.0

---

### 🟠 MINOR version (v1.0 → v1.1)

Incremented when:
- New features are added
- New APIs are introduced
- New adapters are supported
- Kernel internals expand without breaking existing behavior

Guarantee:
- **Backward compatible**
- Existing adapters should continue to work

Example:

v1.0 → v1.1

---

### 🟢 PATCH version (v1.1.0 → v1.1.1)

Incremented when:
- Bug fixes
- Security patches
- Performance improvements
- Documentation fixes

Guarantee:
- **No behavior changes**
- Safe to upgrade immediately

Example:

v1.1.0 → v1.1.1

---

## 3. Kernel Stability Rules

The following are considered **kernel invariants** and change only in MAJOR versions:

- Canonical `KernelMessage` structure
- Trust calculation semantics
- Ledger append-only guarantees
- Override authority rules
- Consensus resolution logic
- Adapter interface contracts

Adapters and APIs may evolve faster than the kernel.

---

## 4. Adapter Compatibility Policy

- Adapters target a **kernel major version**
- Minor kernel upgrades should not break adapters
- Adapter breaking changes require a new adapter version
- Kernel does not auto-migrate adapters

Example:

Adapter v1 → works with Kernel v1.x Adapter v2 → required for Kernel v2.x

---

## 5. Experimental vs Stable

### Stable
- Tagged releases (e.g. `v1.0.0`)
- Intended for real use
- Backward compatibility respected

### Experimental
- `main` branch during active development
- `cre-kernel-lab`
- May change rapidly
- Used for AI-assisted experiments (Codex, Jules)

---

## 6. Security Fixes & Versioning

- Critical security fixes:
  - Applied to the active MAJOR version
  - Released as PATCH versions when possible
- Severe issues may justify a MINOR bump

Security fixes do **not** change versioning guarantees lightly.

---

## 7. Deprecation Policy

- Deprecated behavior is:
  - Documented clearly
  - Maintained for at least one MINOR version
- Removal happens only in MAJOR versions

No silent removals.

---

## 8. Version Tags

Official releases are tagged:

v1.0.0 v1.1.0 v1.1.1

Tags represent:
- Reviewed state
- Tested kernel
- Stable interface expectations

---

## 9. Summary

- MAJOR = breaking kernel changes
- MINOR = backward-compatible features
- PATCH = fixes only
- Kernel changes slowly by design
- Adapters evolve faster than the kernel
- Stability > speed

---

CRE Kernel Versioning Policy  
Maintainer: Vishal


---

