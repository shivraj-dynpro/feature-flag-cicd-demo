import pytest

from app.flags import NEW_UI_DEFAULT, FlagStore, default_store


def test_default_store_has_new_ui():
    store = default_store()
    assert store.get("NEW_UI") == NEW_UI_DEFAULT


def test_set_flag():
    store = FlagStore(NEW_UI=False)
    assert store.set("NEW_UI", True) is True
    assert store.get("NEW_UI") is True


def test_toggle_flag():
    store = FlagStore(NEW_UI=False)
    assert store.toggle("NEW_UI") is True
    assert store.toggle("NEW_UI") is False


def test_get_unknown_flag_raises():
    store = FlagStore(NEW_UI=False)
    with pytest.raises(KeyError):
        store.get("MISSING")


def test_set_unknown_flag_raises():
    store = FlagStore(NEW_UI=False)
    with pytest.raises(KeyError):
        store.set("MISSING", True)


def test_all_returns_a_copy():
    store = FlagStore(NEW_UI=False)
    snapshot = store.all()
    snapshot["NEW_UI"] = True
    assert store.get("NEW_UI") is False
