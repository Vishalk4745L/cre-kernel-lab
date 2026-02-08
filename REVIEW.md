# Code Review Report: cre-kernel-lab

## 1. Critical Violations (Must-Fix)

### 1.1 Hardcoded DEV_MODE Bypass (FIXED)
**Severity:** Critical
**Location:** `kernel/core/signature.py`
**Description:** The `DEV_MODE` flag was hardcoded to `True`, causing `require_signature` to bypass all cryptographic verification. This allowed any agent to spoof identity and perform unauthorized WRITE actions.
**Status:** **Fixed**. `DEV_MODE` changed to `False`. Verified with `reproduce_dev_mode.py`.

### 1.2 Incomplete Audit Trail (FIXED)
**Severity:** High (Compliance Violation)
**Location:** `kernel/core/ledger.py`, `kernel/core/governance.py`
**Description:** The `DESIGN_v0.7.md` specification requires audit logs to include `identity_id`, `signature_verified`, etc. The original implementation of `add_claim`, `set_override`, and `clear_override` did not accept or log these fields.
**Status:** **Fixed**. Updated function signatures and `log_event` calls to include these fields. Updated `api/main.py` to pass them. Verified with `verify_audit_log.py`.

### 1.3 Missing Trust Decay Implementation
**Severity:** Medium (Correctness/Feature Gap)
**Location:** `kernel/core/trust.py`
**Description:** The `decay_all_agents` function is a stub (`pass`), explicitly marked as "v0.11 stub". However, the `README.md` claims "Trust ledger with decay" as a v1.0 feature.
**Status:** **Open**. Requires implementation of time-based decay logic as per design specs (which are missing detail).

---

## 2. Non-Critical Risks

### 2.1 Dead / Confusing Code (`kernel/core/resolver.py`)
**Description:** `kernel/core/resolver.py` appears to be a legacy, in-memory version of `ledger.py`. It has a file header `# kernel/core/ledger.py` which is confusing. The API uses the actual `kernel/core/ledger.py` (SQLite-backed).
**Recommendation:** Delete or rename `kernel/core/resolver.py` to avoid confusion.

### 2.2 Weak / Placeholder Keys
**Description:** `kernel/core/identity.py` contains placeholder public keys (e.g., "Senior" agent has a key of 32 null bytes).
**Recommendation:** Rotate keys before production deployment.

### 2.3 Architecture Bypass
**Description:** `api/main.py` imports directly from `kernel.core.ledger`, `kernel.core.governance`, etc., bypassing the `Kernel` class in `kernel/core/kernel.py`. The `Kernel` class seems underutilized.
**Recommendation:** Refactor API to route requests through `Kernel` methods if strict adapter pattern is desired.

### 2.4 Unused Rate Limiting
**Description:** `kernel/core/limits.py` implements rate limiting logic but is not invoked by `api/main.py` or core logic.
**Recommendation:** Hook up `limit_allows` in the API layer.

### 2.5 Broken `log_event` Usage (FIXED)
**Description:** `kernel/core/governance.py` was calling `log_event` with keyword arguments (`actor=...`, `action=...`) instead of the expected positional `(event_type, data)`. This would have caused runtime errors.
**Status:** **Fixed** as part of the audit trail update.

---

## 3. Invariant Validation Summary

| Invariant | Status | Notes |
| :--- | :--- | :--- |
| **Kernel–Adapter Separation** | ⚠️ Partial | API bypasses `Kernel` class; imports core internals directly. |
| **No Agent Logic Leaks** | ✅ Pass | Core logic is agnostic of agent internals. |
| **Ledger Persistence** | ✅ Pass | Claims and resolutions are correctly stored in SQLite. |
| **Trust Decay** | ❌ Fail | `decay_all_agents` is a no-op stub. |
| **Consensus Logic** | ✅ Pass | Trust-weighted resolution logic appears sound. |
| **Verifiable Authority** | ✅ Pass | (After Fix) Signatures are now strictly enforced. |

---

## 4. Minimal Patch Suggestions (Applied)

The following patches were applied to resolve Critical Violations 1.1 and 1.2, and the bug in 2.5.

### 4.1 Disable DEV_MODE
**File:** `kernel/core/signature.py`
```python
- DEV_MODE = True
+ DEV_MODE = False
```

### 4.2 Update Ledger for Audit Compliance
**File:** `kernel/core/ledger.py`
- Updated `add_claim` to accept `identity_id: Optional[str]` and `signature_verified: bool`.
- Updated `log_event("CLAIM_ADDED", ...)` to include these fields.

### 4.3 Update Governance for Audit Compliance & Bug Fix
**File:** `kernel/core/governance.py`
- Updated `set_override` and `clear_override` to accept auth fields.
- Fixed incorrect `log_event` call format (changed kwargs to dict).

### 4.4 Update API to Pass Auth Info
**File:** `api/main.py`
- Extracted `identity["id"]` and passed it to core functions along with `signature_verified=True`.
