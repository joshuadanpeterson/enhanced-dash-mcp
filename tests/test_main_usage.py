import importlib.util
import inspect
import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_async_stdio_server_used():
    """Ensure the async server runner wires `server.run` with stdio_server."""
    content = FILE_PATH.read_text()
    assert "stdio_server" in content, "stdio_server not referenced"
    assert "server.create_initialization_options()" in content
    assert "async def amain()" in content, "async server runner missing"
    pattern = re.compile(
        r"server\.run\(\s*read_stream\s*,\s*write_stream\s*,\s*init_options\s*\)"
    )
    assert pattern.search(content), "server.run call with init_options missing"


def test_asyncio_run_invocation():
    """Ensure the console entry point starts the async server runner."""
    content = FILE_PATH.read_text()
    pattern = re.compile(
        r"def main\(\) -> None:\s+"
        r'"""Console script entry point\."""\s+'
        r"asyncio\.run\(amain\(\)\)"
    )
    assert pattern.search(content), "console entry point should run amain"
    assert "asyncio.run(main())" not in content


def test_console_entrypoint_is_sync(stub_modules):
    """Project scripts call `main` directly, so it must not be async."""
    spec = importlib.util.spec_from_file_location("enhanced_dash_server", FILE_PATH)
    assert spec and spec.loader
    srv_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(srv_mod)

    assert not inspect.iscoroutinefunction(srv_mod.main)
    assert inspect.iscoroutinefunction(srv_mod.amain)
