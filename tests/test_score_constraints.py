"""
test_score_constraints.py
--------------------------
Unit tests for risk_score and overall_score upper-bound constraints.
Issue #71 — database/models.py
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.models._base import Base
from database.models.interview_session import InterviewSession


@pytest.fixture(scope="module")
def db_session():
    """Create in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    # SQLite needs this to enforce CHECK constraints
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(conn, _):
        conn.execute("PRAGMA integrity_check")

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def make_session(session_id, risk_score=None, overall_score=None):
    """Helper to create InterviewSession object."""
    return InterviewSession(
        session_id=session_id,
        candidate_id="candidate-test-001",
        status="pending",
        risk_score=risk_score,
        overall_score=overall_score,
    )


# ── Valid cases ────────────────────────────────────────────────

def test_valid_scores_within_range(db_session):
    """Scores between 0-100 should be accepted."""
    s = make_session("s001", risk_score=75.0, overall_score=80.0)
    db_session.add(s)
    db_session.commit()


def test_zero_scores_accepted(db_session):
    """Zero scores should be accepted — boundary value."""
    s = make_session("s002", risk_score=0.0, overall_score=0.0)
    db_session.add(s)
    db_session.commit()


def test_hundred_scores_accepted(db_session):
    """Score of exactly 100 should be accepted — upper boundary."""
    s = make_session("s003", risk_score=100.0, overall_score=100.0)
    db_session.add(s)
    db_session.commit()


def test_null_scores_accepted(db_session):
    """NULL scores should be accepted — incomplete sessions."""
    s = make_session("s004", risk_score=None, overall_score=None)
    db_session.add(s)
    db_session.commit()


# ── Invalid cases ──────────────────────────────────────────────

def test_risk_score_above_100_rejected(db_session):
    """risk_score > 100 should raise IntegrityError."""
    s = make_session("s005", risk_score=150.0, overall_score=50.0)
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_overall_score_above_100_rejected(db_session):
    """overall_score > 100 should raise IntegrityError."""
    s = make_session("s006", risk_score=50.0, overall_score=999.0)
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_risk_score_negative_rejected(db_session):
    """Negative risk_score should raise IntegrityError."""
    s = make_session("s007", risk_score=-1.0, overall_score=50.0)
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_overall_score_negative_rejected(db_session):
    """Negative overall_score should raise IntegrityError."""
    s = make_session("s008", risk_score=50.0, overall_score=-5.0)
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_both_scores_out_of_range_rejected(db_session):
    """Both scores out of range should raise IntegrityError."""
    s = make_session("s009", risk_score=200.0, overall_score=300.0)
    db_session.add(s)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()