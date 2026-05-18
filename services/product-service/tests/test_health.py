import asyncio
import importlib
import json


def _call_health(mod):
    fn = getattr(mod, "health", None)
    if fn:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(fn())
        finally:
            asyncio.set_event_loop(None)
            loop.close()

        if hasattr(res, "body"):
            body = json.loads(res.body)
        elif isinstance(res, dict):
            body = res
        else:
            body = None
        assert body and body.get("status") == "ok"
    else:
        assert hasattr(mod, "app")


def test_health():
    mod = importlib.import_module("app.main")
    _call_health(mod)
