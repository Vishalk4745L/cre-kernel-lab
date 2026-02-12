# kernel/core/error_review.py
"""
v0.17 – Error Review Agent (WEIGHTED & EXPLAINABLE)

Responsibilities:
- Record detected errors
- Support multiple reviewers
- Apply severity-weighted trust penalties
- Log explainable penalty reasons (Grafana / Audit)
- Stay extensible for future error types
"""

import time
from typing import Optional

from kernel.core.memory_db import get_connection
from kernel.core.trust import penalize_agent
from kernel.core.error_weights import get_error_weight


# =================================================
# Error Review Ingestion
# =================================================

def add_error_review(
    reviewer_agent: str,
    target_agent: str,
    entity: str,
    observed_value: str,
    expected_value: str,
    error_type: str,
    confidence: float,
    evidence: Optional[str] = None,
) -> None:
    """
    Store an error review into SQLite.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO error_reviews (
            reviewer_agent,
            target_agent,
            entity,
            observed_value,
            expected_value,
            error_type,
            confidence,
            evidence,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reviewer_agent,
            target_agent,
            entity,
            observed_value,
            expected_value,
            error_type,
            float(confidence),
            evidence,
            time.time(),
        ),
    )

    conn.commit()
    conn.close()


def record_error_review(
    reviewer_agent: str,
    target_agent: str,
    entity: str,
    observed_value: str,
    expected_value: str,
    error_type: str,
    confidence: float,
    evidence: Optional[str] = None,
    timestamp: Optional[float] = None,
) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO error_reviews (
            reviewer_agent,
            target_agent,
            entity,
            observed_value,
            expected_value,
            error_type,
            confidence,
            evidence,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reviewer_agent,
            target_agent,
            entity,
            observed_value,
            expected_value,
            error_type,
            float(confidence),
            evidence,
            float(timestamp if timestamp is not None else time.time()),
        ),
    )
    conn.commit()
    conn.close()


# =================================================
# Helper – Fetch reviews for an entity
# =================================================

def get_error_reviews_for_entity(entity: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT *
        FROM error_reviews
        WHERE entity = ?
        """,
        (entity,),
    )

    rows = cur.fetchall()
    conn.close()
    return rows


# =================================================
# Error → Trust Penalty Bridge (WEIGHTED & LOGGED)
# =================================================

def apply_error_penalties(
    entity: str,
    min_reviews: int = 2,
    min_confidence: float = 0.6,
) -> None:
    """
    Apply severity-weighted trust penalties if enough reviewers agree.

    Penalty strength =
        error_type_weight × average_confidence

    Also persists penalty events for:
    - Grafana dashboards
    - Human audit
    - Explainability
    """

    conn = get_connection()
    cur = conn.cursor()

    # Aggregate reviews by (target_agent, error_type)
    cur.execute(
        """
        SELECT
            target_agent,
            error_type,
            COUNT(*) AS review_count,
            AVG(confidence) AS avg_conf
        FROM error_reviews
        WHERE entity = ?
        GROUP BY target_agent, error_type
        """,
        (entity,),
    )

    rows = cur.fetchall()

    for row in rows:
        agent = row["target_agent"]
        error_type = row["error_type"]
        review_count = row["review_count"]
        avg_conf = float(row["avg_conf"])

        if review_count < min_reviews or avg_conf < min_confidence:
            continue

        # -------------------------------------------------
        # Severity weighting
        # -------------------------------------------------
        weight = get_error_weight(error_type)
        final_penalty_strength = round(avg_conf * weight, 4)

        # -------------------------------------------------
        # Apply trust penalty (ONCE per agent+entity+type)
        # -------------------------------------------------
        penalize_agent(
            agent=agent,
            confidence=final_penalty_strength,
        )

        # -------------------------------------------------
        # Persist penalty event (Grafana / Audit)
        # -------------------------------------------------
        cur.execute(
            """
            INSERT INTO error_penalty_events (
                agent,
                entity,
                error_type,
                weight,
                confidence,
                final_penalty_strength,
                reason,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                agent,
                entity,
                error_type,
                weight,
                avg_conf,
                final_penalty_strength,
                "error_review_penalty",
                time.time(),
            ),
        )

    conn.commit()
    conn.close()
