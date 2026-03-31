def test_library_save_and_list_flow(client):
    search_response = client.post(
        "/api/search",
        json={
            "query": "ugc skincare",
            "platforms": ["tiktok"],
            "timeframe": "24h",
            "virality_threshold": 10,
        },
    )
    clip = search_response.json()["results"][0]

    save_response = client.post(
        "/api/library/items",
        json={
            "search_id": search_response.json()["search_id"],
            "clip": clip,
            "saved_note": "Worth reusing for hook analysis",
        },
    )

    assert save_response.status_code == 200

    list_response = client.get("/api/library/items")

    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["content_dna"]["clip_id"] == clip["content_dna"]["clip_id"]
