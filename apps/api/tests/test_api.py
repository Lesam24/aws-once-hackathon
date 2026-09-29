PNG_BYTES = (
    bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000080000000808020000004b6d29dc"
    )
    + b"\x00" * 64
)


def _create(client, mode="blind"):
    return client.post(
        "/api/v1/analyses",
        files={"image": ("board.png", PNG_BYTES, "image/png")},
        data={"mode": mode},
    )


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_analysis_completes(client):
    r = _create(client)
    assert r.status_code == 200
    analysis = r.json()["analysis"]
    assert analysis["status"] == "completed"
    # stub recognizer -> 32 piezas de la posición inicial
    assert len(analysis["board_state"]["pieces"]) == 32
    assert analysis["pipeline_version"].startswith("vision-pipeline@")


def test_get_analysis_and_transcription(client):
    analysis_id = _create(client).json()["analysis"]["id"]

    r = client.get(f"/api/v1/analyses/{analysis_id}")
    assert r.status_code == 200

    r = client.get(f"/api/v1/analyses/{analysis_id}/transcription")
    assert r.status_code == 200
    t = r.json()["transcription"]
    assert len(t["white_lines"]) == 16
    assert len(t["black_lines"]) == 16
    # token braille del rey blanco Re1
    assert any(line["text"] == "Re\u2802" for line in t["white_lines"])


def test_get_missing_analysis_404(client):
    assert client.get("/api/v1/analyses/does-not-exist").status_code == 404


def test_empty_image_rejected(client):
    r = client.post(
        "/api/v1/analyses",
        files={"image": ("x.png", b"", "image/png")},
        data={"mode": "blind"},
    )
    assert r.status_code == 422


def test_invalid_mode_rejected(client):
    r = _create(client, mode="banana")
    assert r.status_code == 422


def test_correction_preserves_original(client):
    analysis_id = _create(client).json()["analysis"]["id"]
    corrected = {
        "orientation": "white-at-bottom",
        "pieces": [
            {"color": "white", "type": "king", "square": "e1", "confidence": 1.0},
            {"color": "black", "type": "king", "square": "e8", "confidence": 1.0},
        ],
    }
    r = client.post(
        f"/api/v1/analyses/{analysis_id}/correction",
        json={"corrected_board_state": corrected, "user_id": "u1"},
    )
    assert r.status_code == 200
    event = r.json()["event"]
    assert event["feedback_type"] == "correction"
    assert event["review_status"] == "pending"
    # la predicción original (32 piezas) se conserva intacta
    assert len(event["original_board_state"]["pieces"]) == 32
    assert len(event["corrected_board_state"]["pieces"]) == 2


def test_confirm_feedback(client):
    analysis_id = _create(client).json()["analysis"]["id"]
    r = client.post(
        f"/api/v1/analyses/{analysis_id}/feedback/confirm",
        json={"user_id": "u1"},
    )
    assert r.status_code == 200
    assert r.json()["event"]["feedback_type"] == "confirm"


def test_history_lists_analyses(client):
    _create(client)
    _create(client)
    r = client.get("/api/v1/history")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 2
    assert all(item["status"] == "completed" for item in items)


def test_correction_on_missing_analysis_404(client):
    r = client.post(
        "/api/v1/analyses/nope/correction",
        json={"corrected_board_state": {"pieces": []}},
    )
    assert r.status_code == 404
