from settings import Settings


def test_default_timeout():
    s = Settings()
    assert s.get("timeout") == 30


def test_override():
    s = Settings({"timeout": 5})
    assert s.get("timeout") == 5
