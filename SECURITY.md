# CRE Kernel — Security Policy

This document explains how security issues should be reported,
how they are handled, and what guarantees CRE Kernel provides.

CRE Kernel treats security as a **first-class design constraint**, not an afterthought.

---

## 1. Supported Versions

The following versions receive security consideration:

- **Main branch (cre-kernel-lab)** — Active development
- Tagged releases marked **STABLE**

Experimental branches may change rapidly and are not guaranteed stable,
but **security issues should still be reported**.

---

## 2. What Counts as a Security Issue

Please report any issue involving:

- Authentication or identity bypass
- Signature verification flaws
- Trust manipulation or escalation
- Audit log tampering
- Unauthorized overrides
- Data corruption or loss
- Privilege escalation
- Kernel invariant violations
- Any bypass of governance or safety rules

If you are unsure, **report it anyway**.

---

## 3. What Is *Not* a Security Issue

The following are not considered security vulnerabilities:

- Missing features
- Performance limitations
- Experimental design choices
- Disagreements with architectural philosophy
- AI model hallucinations outside the kernel

---

## 4. Reporting a Vulnerability (Responsible Disclosure)

### ⚠️ DO NOT open a public issue for security vulnerabilities.

Instead, report privately.

### Preferred method:
- Contact the maintainer directly via GitHub profile contact details

Include:
1. Clear description of the issue
2. Affected files / components
3. Reproduction steps (minimal)
4. Expected vs actual behavior
5. Potential impact
6. Any proof-of-concept (optional)

---

## 5. Response Process

When a report is received:

1. Acknowledgement within reasonable time
2. Issue triaged for severity
3. Reproduction and validation
4. Fix designed and reviewed
5. Patch applied
6. Disclosure handled responsibly

There is **no guaranteed timeline**, but issues are handled deliberately and carefully.

---

## 6. Security Guarantees (Design-Level)

CRE Kernel provides the following guarantees by design:

- Kernel logic is isolated from agents and models
- Trust changes are explicit and auditable
- Overrides require cryptographic authorization
- Memory is append-only and inspectable
- Consensus decisions are explainable
- No hidden authority paths exist

These guarantees are enforced at the **kernel layer**, not in prompts or adapters.

---

## 7. Known Limitations

CRE Kernel is **not**:

- A sandbox
- A secure enclave
- A replacement for OS-level security
- A network firewall

It assumes:
- a trusted execution environment
- secure key storage
- correct deployment practices

---

## 8. AI-Assisted Code

Some code may be authored or reviewed with AI assistance.

Security policy:
- AI suggestions are never trusted blindly
- All changes require human review
- AI has no authority to approve fixes
- Responsibility remains human

---

## 9. Disclosure & Credit

Responsible disclosure is appreciated.

If you wish to be credited for a report:
- indicate this clearly in your message

Anonymous reports are also accepted.

---

## 10. Summary

- Security issues should be reported privately
- Trust integrity is non-negotiable
- Safety outweighs convenience
- AI assists, humans decide
- Kernel invariants are enforced

---

Maintainer:
Vishal  
CRE Kernel Project