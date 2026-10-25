import pytest
from app import fraud

needs_model = pytest.mark.skipif(fraud.artifact is None, reason="Run ml/train_final.py first")


@needs_model
def test_normal_transaction_low_score():
    result = fraud.score_transaction(450, 14, 0, 2)
    assert result["fraud_score"] < 0.1
    assert result["flagged"] is False


@needs_model
def test_risky_transaction_flagged():
    result = fraud.score_transaction(9000, 2, 1, 8)
    assert result["flagged"] is True
    assert len(result["reasons"]) > 0