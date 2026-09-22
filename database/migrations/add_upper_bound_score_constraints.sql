-- Migration: Add upper-bound CHECK constraints for risk_score and overall_score
-- Issue #71

ALTER TABLE interview_sessions
    DROP CONSTRAINT IF EXISTS ck_risk_score_non_negative;

ALTER TABLE interview_sessions
    ADD CONSTRAINT ck_risk_score_non_negative
    CHECK (risk_score IS NULL OR (risk_score >= 0 AND risk_score <= 100));

ALTER TABLE interview_sessions
    DROP CONSTRAINT IF EXISTS ck_overall_score_non_negative;

ALTER TABLE interview_sessions
    ADD CONSTRAINT ck_overall_score_non_negative
    CHECK (overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100));