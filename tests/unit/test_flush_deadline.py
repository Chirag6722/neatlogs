import sys
import threading
import time

import neatlogs

init_module = sys.modules["neatlogs.init"]


class _BlockingProcessor:
    def __init__(self):
        self.release = threading.Event()

    def force_flush(self, timeout_millis=30000):
        self.release.wait(5)
        return True


def test_default_flush_returns_false_at_its_deadline(monkeypatch):
    blocker = _BlockingProcessor()
    monkeypatch.setattr(init_module, "_transport_span_processors", [blocker])
    monkeypatch.setattr(init_module, "_log_provider", None)

    started = time.monotonic()
    ok = neatlogs.flush(timeout_millis=200)
    elapsed = time.monotonic() - started
    blocker.release.set()

    assert ok is False
    assert elapsed < 2


def test_default_flush_still_returns_true_when_fast(monkeypatch):
    class Fast:
        def force_flush(self, timeout_millis=30000):
            return True

    monkeypatch.setattr(init_module, "_transport_span_processors", [Fast()])
    monkeypatch.setattr(init_module, "_log_provider", None)
    assert neatlogs.flush(timeout_millis=1000) is True
