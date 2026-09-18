from app.models.user import UserOut
from app.providers.fake import FakeUserProvider


def test_fetch_users_success(make_client) -> None:
    provider = FakeUserProvider(
        {
            1: UserOut(id=1, name="Leanne Graham"),
            2: UserOut(id=2, name="Ervin Howell"),
            3: UserOut(id=3, name="Clementine Bauch"),
        }
    )

    with make_client(provider) as client:
        response = client.post("/api/users/fetch", json={"user_ids": [1, 2, 3]})

    assert response.status_code == 200
    body = response.json()
    assert [user["id"] for user in body["users"]] == [1, 2, 3]
    assert body["failed"] == []
    assert body["errors"] == []
    assert {user["name"] for user in body["users"]} == {
        "Leanne Graham",
        "Ervin Howell",
        "Clementine Bauch",
    }


def test_fetch_users_partial_failure(make_client) -> None:
    provider = FakeUserProvider(
        {
            1: UserOut(id=1, name="Leanne Graham"),
            2: UserOut(id=2, name="Ervin Howell"),
        },
        not_found_ids={3},
    )

    with make_client(provider) as client:
        response = client.post("/api/users/fetch", json={"user_ids": [1, 2, 3]})

    assert response.status_code == 200
    body = response.json()
    assert sorted(user["id"] for user in body["users"]) == [1, 2]
    assert body["failed"] == [3]
    assert body["errors"] == [{"id": 3, "reason": "not_found"}]


def test_fetch_users_uses_cache_on_second_call(make_client) -> None:
    provider = FakeUserProvider({1: UserOut(id=1, name="Leanne Graham")})

    with make_client(provider) as client:
        first = client.post("/api/users/fetch", json={"user_ids": [1]})
        second = client.post("/api/users/fetch", json={"user_ids": [1]})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert provider.calls == [1]


def test_fetch_users_deduplicates_ids(make_client) -> None:
    provider = FakeUserProvider({1: UserOut(id=1, name="Leanne Graham")})

    with make_client(provider) as client:
        response = client.post("/api/users/fetch", json={"user_ids": [1, 1, 1]})

    assert response.status_code == 200
    assert response.json()["failed"] == []
    assert response.json()["errors"] == []
    assert provider.calls == [1]


def test_fetch_users_rejects_invalid_payload(make_client) -> None:
    with make_client(FakeUserProvider()) as client:
        for payload in (
            {"user_ids": []},
            {"user_ids": [0]},
            {"user_ids": [-1]},
            {},
        ):
            response = client.post("/api/users/fetch", json=payload)
            assert response.status_code == 422, payload
