# kernel/core/error_weights.py

"""
Defines severity weight for each error type.
Higher weight = higher trust penalty.
Extensible for future domains.
"""

ERROR_WEIGHTS = {
    # 🔥 Critical errors
    "FACT_ERROR": 1.0,
    "HALLUCINATION": 0.9,
    "LOGIC_ERROR": 0.8,

    # 🧠 Technical errors
    "CODE_ERROR": 0.7,

    # ✍️ Surface-level errors
    "FORMAT_ERROR": 0.3,
    "SPELLING_ERROR": 0.1,
}


def get_error_weight(error_type: str) -> float:
    """
    Return severity weight for error type.
    Unknown errors get medium penalty.
    """
    return ERROR_WEIGHTS.get(error_type, 0.5)