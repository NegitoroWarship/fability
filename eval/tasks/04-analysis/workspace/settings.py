class Settings:
    """Per-service configuration. Each service constructs its own instance."""

    def __init__(self, overrides={}):
        self.values = overrides
        self.values.setdefault("timeout", 30)

    def set(self, key, value):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)
