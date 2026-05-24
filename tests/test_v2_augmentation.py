import asyncio
import importlib.util
import json
import os
import plistlib
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any
from uuid import uuid4


MODULE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def load_module(monkeypatch, stub_modules, tmp_path):
    monkeypatch.setenv("DASH_MCP_INDEX_PATH", str(tmp_path / "docset-index.json"))
    module_name = f"enhanced_dash_server_test_{uuid4().hex}"
    spec = importlib.util.spec_from_file_location(module_name, MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def create_docset(root: Path, name: str, display_name: str | None = None) -> Path:
    resources = root / f"{name}.docset" / "Contents" / "Resources"
    resources.mkdir(parents=True)
    (resources / "Documents").mkdir()
    db_path = resources / "docSet.dsidx"
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE searchIndex(name TEXT, type TEXT, path TEXT)")
    conn.commit()
    conn.close()

    info_path = root / f"{name}.docset" / "Contents" / "Info.plist"
    with info_path.open("wb") as file_obj:
        plistlib.dump(
            {
                "CFBundleName": display_name or name,
                "CFBundleIdentifier": f"com.example.{name.lower()}",
                "DocSetPlatformFamily": name.lower(),
            },
            file_obj,
        )
    return root / f"{name}.docset"


def call_json(module: Any, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    response = asyncio.run(module.call_tool(name, arguments))
    assert len(response) == 1
    return json.loads(response[0].text)


def test_tool_surface_is_v2_only(monkeypatch, stub_modules, tmp_path) -> None:
    module = load_module(monkeypatch, stub_modules, tmp_path)

    tools = asyncio.run(module.list_tools())
    names = [tool.name for tool in tools]

    assert names == [
        "analyze_project_docs_context",
        "recommend_dash_docsets",
        "plan_dash_searches",
        "rank_dash_results",
        "summarize_docset_coverage",
        "suggest_offline_docs_for_repo",
        "explain_missing_docsets",
    ]
    assert len(names) == len(set(names))
    assert "search_dash_docs" not in names
    assert "list_docsets" not in names
    assert "get_doc_content" not in names
    assert not hasattr(module.DashMCPServer, "search_docset")


def test_recommendations_attach_official_identifiers(
    monkeypatch,
    stub_modules,
    tmp_path,
) -> None:
    dash_root = tmp_path / "Dash" / "DocSets"
    create_docset(dash_root, "FastAPI")
    create_docset(dash_root, "Pydantic")
    monkeypatch.setenv("DASH_DOCSETS_PATH", str(dash_root))
    module = load_module(monkeypatch, stub_modules, tmp_path)

    official = {
        "docsets": [
            {
                "name": "FastAPI",
                "identifier": "fastapi-id",
                "platform": "fastapi",
                "full_text_search": "enabled",
            }
        ]
    }
    payload = call_json(
        module,
        "recommend_dash_docsets",
        {
            "context": {
                "languages": ["python"],
                "frameworks": ["fastapi"],
                "dependencies": ["pydantic"],
            },
            "official_docsets": official,
        },
    )

    docsets = payload["official_handoff"]["docsets"]
    fastapi = next(item for item in docsets if item["name"] == "FastAPI")
    assert fastapi["official_identifier"] == "fastapi-id"
    assert fastapi["coverage_status"] == "matched"
    assert any(
        item["name"] == "Pydantic"
        for item in payload["local_cache_candidates"]
    )


def test_recommendations_without_snapshot_do_not_invent_ids(
    monkeypatch,
    stub_modules,
    tmp_path,
) -> None:
    module = load_module(monkeypatch, stub_modules, tmp_path)
    payload = call_json(
        module,
        "recommend_dash_docsets",
        {"context": {"languages": ["python"], "frameworks": ["fastapi"]}},
    )

    assert payload["schema_version"] == "dash-augmentation/v1"
    assert all(
        item["official_identifier"] is None
        for item in payload["official_handoff"]["docsets"]
    )
    assert payload["local_cache_candidates"] == []
    assert any("No official Dash docset snapshot" in item for item in payload["warnings"])


def test_docset_index_reuses_cache_and_invalidates_on_mtime(
    monkeypatch,
    stub_modules,
    tmp_path,
) -> None:
    dash_root = tmp_path / "Dash" / "DocSets"
    docset_path = create_docset(dash_root, "FastAPI")
    monkeypatch.setenv("DASH_DOCSETS_PATH", str(dash_root))
    module = load_module(monkeypatch, stub_modules, tmp_path)
    dash_server = module.DashMCPServer()

    first = asyncio.run(dash_server.get_available_docsets())
    assert first[0]["name"] == "FastAPI"
    assert dash_server.index_path.exists()

    def fail_discovery():
        raise AssertionError("cache was not reused")

    monkeypatch.setattr(dash_server, "_discover_docsets", fail_discovery)
    second = asyncio.run(dash_server.get_available_docsets())
    assert second[0]["name"] == "FastAPI"

    info_path = docset_path / "Contents" / "Info.plist"
    new_mtime = time.time() + 10
    os.utime(info_path, (new_mtime, new_mtime))
    called = []

    original = module.DashMCPServer._discover_docsets

    def wrapped_discovery():
        called.append(True)
        return original(dash_server)

    monkeypatch.setattr(dash_server, "_discover_docsets", wrapped_discovery)
    third = asyncio.run(dash_server.get_available_docsets())
    assert called
    assert third[0]["schema_hints"]["tables"] == ["searchIndex"]


def test_project_context_detects_common_repo_types(
    monkeypatch,
    stub_modules,
    tmp_path,
) -> None:
    module = load_module(monkeypatch, stub_modules, tmp_path)
    cases = [
        ("js", "package.json", '{"dependencies":{"react":"latest","next":"latest"}}', "nextjs"),
        ("python", "pyproject.toml", '[project]\ndependencies=["fastapi"]\n', "fastapi"),
        ("rust", "Cargo.toml", "[dependencies]\nserde = \"1\"\n", "rust"),
        ("go", "go.mod", "module x\nrequire github.com/gin-gonic/gin v1.0.0\n", "go"),
        ("ruby", "Gemfile", "gem \"rails\"\n", "rails"),
        ("java", "build.gradle", "implementation 'org.slf4j:slf4j-api:1.0'\n", "java"),
    ]

    for folder, manifest_name, content, expected in cases:
        project = tmp_path / folder
        project.mkdir()
        (project / manifest_name).write_text(content)
        context = asyncio.run(
            module.augmentation_server.analyze_project_docs_context(str(project))
        )
        detected = set(context.languages) | set(context.frameworks)
        assert expected in detected


def test_coverage_gap_summary(monkeypatch, stub_modules, tmp_path) -> None:
    dash_root = tmp_path / "Dash" / "DocSets"
    create_docset(dash_root, "FastAPI")
    create_docset(dash_root, "Pydantic")
    monkeypatch.setenv("DASH_DOCSETS_PATH", str(dash_root))
    module = load_module(monkeypatch, stub_modules, tmp_path)
    official = {
        "docsets": [
            {"name": "FastAPI", "identifier": "fastapi-id", "platform": "fastapi"},
            {"name": "Official Only", "identifier": "official-id", "platform": "only"},
        ]
    }

    payload = call_json(
        module,
        "summarize_docset_coverage",
        {"official_docsets": official, "limit": 20},
    )

    summary = payload["coverage_summary"]
    assert summary["matched"] == 1
    assert summary["local_cache_only"] == 1
    assert summary["official_only"] == 1


def test_rank_dash_results_preserves_load_url(
    monkeypatch,
    stub_modules,
    tmp_path,
) -> None:
    module = load_module(monkeypatch, stub_modules, tmp_path)
    payload = call_json(
        module,
        "rank_dash_results",
        {
            "query": "fastapi dependency injection",
            "official_results": [
                {
                    "name": "Other",
                    "snippet": "unrelated",
                    "load_url": "http://127.0.0.1/other",
                },
                {
                    "name": "Depends",
                    "snippet": "FastAPI dependency injection guide",
                    "load_url": "http://127.0.0.1/depends",
                },
            ],
        },
    )

    ranked = payload["ranked_results"]
    assert ranked[0]["load_url"] == "http://127.0.0.1/depends"
    assert ranked[0]["augmentation_score"] > ranked[1]["augmentation_score"]
