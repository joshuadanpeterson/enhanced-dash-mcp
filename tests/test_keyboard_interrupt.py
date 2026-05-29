import asyncio
import functools
import importlib.util
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


class DummyServer:
    def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        pass

    async def run(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
        while True:
            await asyncio.sleep(0.1)

    def list_tools(self) -> Any:  # pragma: no cover - stub
        def decorator(func: Any) -> Any:
            return func

        return decorator

    def call_tool(self) -> Any:  # pragma: no cover - stub
        def decorator(func: Any) -> Any:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

            return wrapper

        return decorator


@asynccontextmanager
async def dummy_stdio_server(raise_interrupt: bool = False):  # pragma: no cover - stub
    class DummyStream:
        async def send(self, _data: bytes) -> None:  # type: ignore[empty-body]
            pass

        async def receive(self) -> bytes:
            await asyncio.sleep(0.1)
            return b""

    if raise_interrupt:
        raise KeyboardInterrupt
    yield DummyStream(), DummyStream()


@pytest.mark.asyncio
async def test_amain_handles_cancelled(monkeypatch, stub_modules) -> None:
    """The async server runner should exit cleanly when cancelled."""
    stub_server = stub_modules["mcp.server"]
    stub_server.Server = DummyServer  # type: ignore[attr-defined]

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    srv_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srv_mod)
    amain = srv_mod.amain

    monkeypatch.setattr(srv_mod, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(srv_mod, "server", type("dummy", (), {"run": DummyServer().run})())

    task = asyncio.create_task(amain())
    await asyncio.sleep(0.1)
    task.cancel()
    result = await task
    assert result is None
