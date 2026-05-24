import sys
import types
from typing import Any

import pytest


@pytest.fixture
def stub_modules(monkeypatch):
    """Provide minimal MCP and third-party stubs for tests."""
    stub_mcp = types.ModuleType("mcp")
    stub_server = types.ModuleType("server")
    # Provide decorators expected by enhanced_dash_server

    def list_tools() -> Any:
        def decorator(func: Any) -> Any:
            return func
        return decorator

    def call_tool() -> Any:
        def decorator(func: Any) -> Any:
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                return await func(*args, **kwargs)

            return wrapper
        return decorator

    stub_server.list_tools = list_tools  # type: ignore[attr-defined]
    stub_server.call_tool = call_tool  # type: ignore[attr-defined]
    stub_stdio = types.ModuleType("stdio")
    stub_types = types.ModuleType("types")

    class Tool:  # pragma: no cover - stub
        def __init__(self, **kwargs: Any) -> None:
            self.__dict__.update(kwargs)

    class TextContent:  # pragma: no cover - stub
        def __init__(self, **kwargs: Any) -> None:
            self.__dict__.update(kwargs)

    class Server:  # pragma: no cover - stub
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            pass

        def list_tools(self) -> Any:
            return list_tools()

        def call_tool(self) -> Any:
            return call_tool()

        def get_capabilities(self) -> dict[str, Any]:
            return {}

        def create_initialization_options(self) -> dict[str, Any]:
            return {}

        async def run(self, *_args: Any, **_kwargs: Any) -> None:
            pass

    stub_types.Tool = Tool  # type: ignore[attr-defined]
    stub_types.TextContent = TextContent  # type: ignore[attr-defined]
    stub_server.Server = Server  # type: ignore[attr-defined]

    async def _stdio():  # pragma: no cover - stub
        return ""

    stub_stdio.stdio_server = _stdio  # type: ignore[attr-defined]
    modules = {
        "mcp": stub_mcp,
        "mcp.server": stub_server,
        "mcp.server.stdio": stub_stdio,
        "mcp.types": stub_types,
    }

    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)

    yield modules

    for name in modules:
        monkeypatch.delitem(sys.modules, name, raising=False)
