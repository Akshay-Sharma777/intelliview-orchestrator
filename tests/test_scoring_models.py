from workers.scoring_models import ExperimentalRiskModel


def test_scoring_output_ranges(monkeypatch):
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine.calculate_video_risk",
        lambda _: 0.2,
    )
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine.calculate_audio_risk",
        lambda _: 0.4,
    )
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine.calculate_evaluation_risk",
        lambda _: 0.6,
    )
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine.classify_risk",
        lambda _: "medium",
    )
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine._identify_risk_factors",
        lambda *_: [],
    )
    monkeypatch.setattr(
        "workers.scoring_models.RiskScoringEngine._generate_recommendation",
        lambda _: "Review required",
    )

    model = ExperimentalRiskModel()

    report = model.generate_report(
        session_id="test-session",
        video_result={},
        audio_result={},
        evaluation_result={},
    )

    score = report["final_risk_score"]

    assert 0.0 <= score <= 1.0
