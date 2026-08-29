app.include_router(create_candidate_routes(candidate_manager=candidate_manager))
app.include_router(create_analytics_routes())
app.include_router(practice_sessions_router)
app.include_router(create_schedule_routes())
app.include_router(create_question_routes(question_bank=question_bank))
app.include_router(create_settings_routes())
app.include_router(create_attendance_routes())
app.include_router(risk_router)
app.include_router(engine_router)
@app.get("/dashboard")
async def get_dashboard():
    """
    Serve the monitoring dashboard HTML

    Returns:
        HTML content of the dashboard
    """
    try:
        from anyio import Path
        from fastapi.responses import HTMLResponse

        dashboard_path = Path(__file__).parent / ".." / "monitoring" / "dashboard.html"

        if await dashboard_path.exists():
            html_content = await dashboard_path.read_text(encoding="utf-8")
            return HTMLResponse(content=html_content)
        raise HTTPException(status_code=404, detail="Dashboard HTML not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving dashboard: {e!s}")
        raise HTTPException(status_code=500, detail=f"Error serving dashboard: {e!s}")