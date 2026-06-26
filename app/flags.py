"""Feature flag store.

The whole demo revolves around a single flag: ``NEW_UI``.

To demo a developer change, flip ``NEW_UI_DEFAULT`` below — it is the one
obvious place that controls the flag's default value.
"""

# 👇 The one line a developer changes during the demo.
NEW_UI_DEFAULT = False


class FlagStore:
    """A tiny in-memory feature flag store (no database, on purpose)."""

    def __init__(self, **defaults: bool) -> None:
        self._flags: dict[str, bool] = dict(defaults)

    def all(self) -> dict[str, bool]:
        """Return a copy of all flags and their state."""
        return dict(self._flags)

    def get(self, name: str) -> bool:
        """Return a flag's state. Raises ``KeyError`` if unknown."""
        if name not in self._flags:
            raise KeyError(name)
        return self._flags[name]

    def set(self, name: str, enabled: bool) -> bool:
        """Set a flag to an explicit value and return it."""
        if name not in self._flags:
            raise KeyError(name)
        self._flags[name] = enabled
        return self._flags[name]

    def toggle(self, name: str) -> bool:
        """Flip a flag and return the new value."""
        self._flags[name] = not self.get(name)
        return self._flags[name]


def default_store() -> FlagStore:
    """Build the store the app starts with."""
    return FlagStore(NEW_UI=NEW_UI_DEFAULT)
