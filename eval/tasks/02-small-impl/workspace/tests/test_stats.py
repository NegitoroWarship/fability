from stats import compute


def test_compute():
    s = compute([10.0, 20.0, 30.0, 40.0])
    assert s == {"count": 4, "mean": 25.0, "min": 10.0, "max": 40.0}
