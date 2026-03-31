from __future__ import annotations


def test_search_round_trip_and_library_save(client) -> None:
    response = client.post(
        "/api/search",
        json={
            "query": "ai creator hooks",
            "platforms": ["tiktok", "youtube_shorts"],
            "timeframe": "7d",
            "minimum_virality_score": 20.0,
            "result_limit": 5,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"completed", "partial"}
    assert body["results"]

    search_id = body["search_id"]
    stored = client.get(f"/api/search/{search_id}")
    assert stored.status_code == 200
    stored_body = stored.json()
    assert stored_body["search_id"] == search_id
    assert stored_body["results"]

    content_dna_id = stored_body["results"][0]["content_dna"]["id"]
    save_response = client.post("/api/library/items", json={"content_dna_id": content_dna_id, "note": "save"})
    assert save_response.status_code == 200
    saved_body = save_response.json()
    assert saved_body["content_dna_id"] == content_dna_id

    library_response = client.get("/api/library/items")
    assert library_response.status_code == 200
    library_items = library_response.json()
    assert len(library_items) == 1
    assert library_items[0]["content_dna_id"] == content_dna_id


def test_health_endpoint(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
