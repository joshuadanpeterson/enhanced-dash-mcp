import importlib.util
import logging
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_configure_logging_creates_file(tmp_path, stub_modules):
    class DummyServer:
        def __init__(self, *_args, **_kwargs) -> None:  # pragma: no cover - stub
            pass

        def list_tools(self):  # pragma: no cover - stub
            def decorator(func):
                return func

            return decorator

        def call_tool(self):  # pragma: no cover - stub
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                return wrapper

            return decorator

    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]
    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    log_file = tmp_path / "server.log"
    server_mod.configure_logging(logging.INFO, str(log_file))
    server_mod.logger.info("hello")
    logging.shutdown()
    assert log_file.exists()
    assert "hello" in log_file.read_text()


@pytest.mark.asyncio
async def test_amain_logs_startup_message(tmp_path, monkeypatch, stub_modules):
    """The async server runner should record a startup message to the log file."""

    class DummyServer:
        async def run(self, *_args, **_kwargs) -> None:
            return

        def list_tools(self):
            def decorator(func):
                return func

            return decorator

        def call_tool(self):
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                return wrapper

            return decorator

    stub_modules["mcp.server"].Server = DummyServer  # type: ignore[attr-defined]

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    log_file = tmp_path / "server.log"
    server_mod.LOG_FILE = str(log_file)
    server_mod.configure_logging(logging.INFO, str(log_file))

    async def dummy_stdio_server():
        class DummyStream:
            async def send(self, _data: bytes) -> None:
                pass

            async def receive(self) -> bytes:
                return b""

        yield DummyStream(), DummyStream()

    monkeypatch.setattr(server_mod, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(server_mod, "server", DummyServer())

    await server_mod.amain()
    logging.shutdown()
    assert log_file.exists()
    content = log_file.read_text()
    assert "server starting" in content.lower()
    assert "server stopped" in content.lower()


@pytest.mark.asyncio
async def test_amain_logs_error(tmp_path, monkeypatch, stub_modules):
    """The async server runner should log an error when server.run fails."""

    class FailingServer:
        async def run(self, *_args, **_kwargs) -> None:
            raise RuntimeError("boom")

        def list_tools(self):
            def decorator(func):
                return func

            return decorator

        def call_tool(self):
            def decorator(func):
                async def wrapper(*args, **kwargs):
                    return await func(*args, **kwargs)

                return wrapper

            return decorator

    stub_modules["mcp.server"].Server = FailingServer  # type: ignore[attr-defined]

    spec = importlib.util.spec_from_file_location("enhanced_dash_server", MODULE_PATH)
    assert spec and spec.loader
    server_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(server_mod)

    log_file = tmp_path / "server.log"
    server_mod.LOG_FILE = str(log_file)
    server_mod.configure_logging(logging.INFO, str(log_file))

    async def dummy_stdio_server():
        class DummyStream:
            async def send(self, _data: bytes) -> None:
                pass

            async def receive(self) -> bytes:
                return b""

        yield DummyStream(), DummyStream()

    monkeypatch.setattr(server_mod, "stdio_server", dummy_stdio_server)
    monkeypatch.setattr(server_mod, "server", FailingServer())

    with pytest.raises(RuntimeError):
        await server_mod.amain()
    logging.shutdown()
    content = log_file.read_text()
    assert "error running server" in content.lower()
