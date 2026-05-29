#!/usr/bin/env python3
"""Enhanced Dash MCP Server.

Version 2 makes this server an augmentation layer around the official Dash
MCP. It analyzes projects, recommends docsets, plans searches, ranks official
Dash results, and explains local-vs-official docset coverage. It intentionally
does not expose exact Dash-backed search or page-loading tools; those belong to
the official Dash MCP server.
"""

import asyncio
import contextlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import plistlib
import re
import sqlite3
import sys
import time
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Optional, cast

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool


__version__ = "2.0.0"
HANDOFF_SCHEMA_VERSION = "dash-augmentation/v1"
DEFAULT_MAX_FILES = 200
DEFAULT_INDEX_PATH = Path.home() / ".cache" / "dash-mcp" / "docset-index-v2.json"


def configure_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> None:
    """Configure console and optional file logging."""
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
        )
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers,
        force=True,
    )


LOG_LEVEL = os.getenv("DASH_MCP_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv(
    "DASH_MCP_LOG_FILE",
    str(Path.home() / ".cache" / "dash-mcp" / "server.log"),
)
configure_logging(getattr(logging, LOG_LEVEL, logging.INFO), LOG_FILE)
logger = logging.getLogger(__name__)


def is_interactive_mode() -> bool:
    """Return whether the server appears to be running interactively."""
    ci_env_vars = [
        "CI",
        "CONTINUOUS_INTEGRATION",
        "JENKINS_URL",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "TRAVIS",
        "CIRCLECI",
        "BUILDKITE",
        "DRONE",
        "BITBUCKET_BUILD_NUMBER",
        "AZURE_HTTP_USER_AGENT",
        "CODEBUILD_BUILD_ID",
        "TEAMCITY_VERSION",
        "BAMBOO_BUILD_NUMBER",
        "TF_BUILD",
        "APPVEYOR",
        "WERCKER",
        "CONCOURSE",
        "SEMAPHORE",
        "HUDSON_URL",
        "BUILD_ID",
        "BUILD_NUMBER",
    ]
    automation_env_vars = [
        "AUTOMATION",
        "AUTOMATED",
        "NON_INTERACTIVE",
        "BATCH_MODE",
        "HEADLESS",
        "CRON",
        "SYSTEMD_EXEC_PID",
        "KUBERNETES_SERVICE_HOST",
        "DOCKER_CONTAINER",
        "CONTAINER",
        "AWS_EXECUTION_ENV",
        "LAMBDA_RUNTIME_DIR",
        "GOOGLE_CLOUD_PROJECT",
        "AZURE_FUNCTIONS_ENVIRONMENT",
        "HEROKU_APP_ID",
        "RAILWAY_ENVIRONMENT",
        "VERCEL",
        "NETLIFY",
        "CF_PAGES",
    ]

    for env_var in ci_env_vars + automation_env_vars:
        if os.getenv(env_var):
            logger.info("Non-interactive mode detected: %s is set", env_var)
            return False

    term = os.getenv("TERM", "").lower()
    if term in {"", "dumb", "unknown"}:
        logger.info("Non-interactive mode detected: TERM=%r", term)
        return False

    shell = os.getenv("SHELL", "").lower()
    if "/nologin" in shell or "/false" in shell:
        logger.info("Non-interactive mode detected: shell=%r", shell)
        return False

    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty())
    except (AttributeError, OSError):
        return False


@dataclass
class LocalDocset:
    """Metadata for a Dash cache docset discovered on disk."""

    name: str
    normalized_name: str
    db_path: str
    docs_path: str
    docset_path: str
    has_content: bool
    category: str
    source: str
    display_name: Optional[str] = None
    bundle_identifier: Optional[str] = None
    platform_family: Optional[str] = None
    schema_hints: dict[str, Any] = field(default_factory=dict)
    mtimes: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "normalized_name": self.normalized_name,
            "display_name": self.display_name,
            "bundle_identifier": self.bundle_identifier,
            "platform_family": self.platform_family,
            "db_path": self.db_path,
            "docs_path": self.docs_path,
            "docset_path": self.docset_path,
            "has_content": self.has_content,
            "category": self.category,
            "source": self.source,
            "schema_hints": self.schema_hints,
            "mtimes": self.mtimes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LocalDocset":
        return cls(
            name=str(data.get("name", "")),
            normalized_name=str(data.get("normalized_name", "")),
            display_name=data.get("display_name"),
            bundle_identifier=data.get("bundle_identifier"),
            platform_family=data.get("platform_family"),
            db_path=str(data.get("db_path", "")),
            docs_path=str(data.get("docs_path", "")),
            docset_path=str(data.get("docset_path", "")),
            has_content=bool(data.get("has_content", False)),
            category=str(data.get("category", "")),
            source=str(data.get("source", "")),
            schema_hints=dict(data.get("schema_hints") or {}),
            mtimes=dict(data.get("mtimes") or {}),
        )


@dataclass
class ProjectDocsContext:
    """Project metadata used to recommend Dash docsets and searches."""

    project_path: Optional[str] = None
    languages: list[str] = field(default_factory=list)
    frameworks: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    package_managers: list[str] = field(default_factory=list)
    manifest_files: list[str] = field(default_factory=list)
    current_files: list[str] = field(default_factory=list)
    file_counts: dict[str, int] = field(default_factory=dict)
    recommended_docsets: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_path": self.project_path,
            "languages": self.languages,
            "frameworks": self.frameworks,
            "dependencies": self.dependencies,
            "package_managers": self.package_managers,
            "manifest_files": self.manifest_files,
            "current_files": self.current_files,
            "file_counts": self.file_counts,
            "recommended_docsets": self.recommended_docsets,
        }


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    safe: bool = True

    def to_tool(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema,
            annotations=cast(Any, {
                "safe": self.safe,
                "title": self.name.replace("_", " ").title(),
            }),
        )


def normalize_name(value: str) -> str:
    """Normalize names for local cache and official Dash matching."""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        cleaned = value.strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def strip_json_comments(content: str) -> str:
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return re.sub(r"^\s*//.*$", "", content, flags=re.MULTILINE)


def parse_requirement_name(line: str) -> Optional[str]:
    cleaned = line.strip()
    if not cleaned or cleaned.startswith("#") or cleaned.startswith("-"):
        return None
    cleaned = cleaned.split("#", 1)[0].strip()
    match = re.match(r"([A-Za-z0-9_.-]+)", cleaned)
    return match.group(1) if match else None


def parse_gem_names(content: str) -> list[str]:
    return re.findall(r"^\s*gem\s+['\"]([^'\"]+)['\"]", content, re.MULTILINE)


class DashMCPServer:
    """Internal metadata indexer for Dash docsets on disk."""

    def __init__(self) -> None:
        env_path = os.getenv("DASH_DOCSETS_PATH")
        self.docsets_path = (
            Path(env_path)
            if env_path
            else Path.home() / "Library/Application Support/Dash"
        )
        self.docsets_path = self._adjust_docsets_path(self.docsets_path)
        self.index_path = Path(os.getenv("DASH_MCP_INDEX_PATH", DEFAULT_INDEX_PATH))
        logger.info("Using Dash metadata root %s", self.docsets_path)

    @staticmethod
    def _adjust_docsets_path(path: Path) -> Path:
        adjusted_path = path.expanduser().resolve()
        return adjusted_path

    async def get_available_docsets(
        self,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]]:
        """Return local docset metadata, using the persistent v2 index."""
        docsets = await self.get_local_docsets(force_refresh=force_refresh)
        return [docset.to_dict() for docset in docsets]

    async def get_local_docsets(
        self,
        force_refresh: bool = False,
    ) -> list[LocalDocset]:
        signature = self._build_index_signature()
        if not force_refresh:
            cached = self._read_index(signature)
            if cached is not None:
                return cached

        docsets = self._discover_docsets()
        self._write_index(signature, docsets)
        return docsets

    def _build_index_signature(self) -> dict[str, Any]:
        candidates: list[dict[str, Any]] = []
        if self.docsets_path.exists():
            for docset_dir in sorted(self.docsets_path.rglob("*.docset")):
                db_path = docset_dir / "Contents" / "Resources" / "docSet.dsidx"
                info_path = docset_dir / "Contents" / "Info.plist"
                candidates.append(
                    {
                        "docset_path": str(docset_dir),
                        "docset_mtime": self._mtime(docset_dir),
                        "info_mtime": self._mtime(info_path),
                        "db_mtime": self._mtime(db_path),
                    }
                )
        return {
            "schema_version": 2,
            "root": str(self.docsets_path),
            "env_path": os.getenv("DASH_DOCSETS_PATH"),
            "candidates": candidates,
        }

    @staticmethod
    def _mtime(path: Path) -> float:
        try:
            return path.stat().st_mtime
        except OSError:
            return 0.0

    def _read_index(self, signature: dict[str, Any]) -> Optional[list[LocalDocset]]:
        try:
            payload = json.loads(self.index_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None

        if payload.get("signature") != signature:
            return None

        raw_docsets = payload.get("docsets")
        if not isinstance(raw_docsets, list):
            return None

        logger.debug("Using cached Dash metadata index at %s", self.index_path)
        return [LocalDocset.from_dict(item) for item in raw_docsets]

    def _write_index(
        self,
        signature: dict[str, Any],
        docsets: list[LocalDocset],
    ) -> None:
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 2,
            "generated_at": time.time(),
            "signature": signature,
            "docsets": [docset.to_dict() for docset in docsets],
        }
        self.index_path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def _discover_docsets(self) -> list[LocalDocset]:
        if not self.docsets_path.exists():
            logger.warning("Dash metadata root does not exist: %s", self.docsets_path)
            return []

        discovered: list[LocalDocset] = []
        for docset_dir in sorted(self.docsets_path.rglob("*.docset")):
            db_path = docset_dir / "Contents" / "Resources" / "docSet.dsidx"
            if not db_path.exists():
                continue

            docs_path = docset_dir / "Contents" / "Resources" / "Documents"
            info_path = docset_dir / "Contents" / "Info.plist"
            plist = self._read_info_plist(info_path)
            raw_name = docset_dir.name.removesuffix(".docset")
            display_name = self._plist_string(plist, "CFBundleName")
            platform_family = (
                self._plist_string(plist, "DocSetPlatformFamily")
                or self._plist_string(plist, "DocSetPlatformName")
            )
            source = self._classify_source(docset_dir)

            discovered.append(
                LocalDocset(
                    name=display_name or raw_name,
                    normalized_name=normalize_name(display_name or raw_name),
                    display_name=display_name,
                    bundle_identifier=self._plist_string(plist, "CFBundleIdentifier"),
                    platform_family=platform_family,
                    db_path=str(db_path),
                    docs_path=str(docs_path),
                    docset_path=str(docset_dir),
                    has_content=docs_path.exists(),
                    category=docset_dir.parent.name,
                    source=source,
                    schema_hints=self._schema_hints(db_path),
                    mtimes={
                        "docset": self._mtime(docset_dir),
                        "info_plist": self._mtime(info_path),
                        "docSet_dsidx": self._mtime(db_path),
                    },
                )
            )

        logger.info("Indexed %s local Dash cache docsets", len(discovered))
        return discovered

    @staticmethod
    def _read_info_plist(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            with path.open("rb") as file_obj:
                loaded = plistlib.load(file_obj)
        except Exception as exc:
            logger.debug("Could not read Info.plist %s: %s", path, exc)
            return {}
        return loaded if isinstance(loaded, dict) else {}

    @staticmethod
    def _plist_string(plist: dict[str, Any], key: str) -> Optional[str]:
        value = plist.get(key)
        return str(value) if value else None

    @staticmethod
    def _classify_source(docset_dir: Path) -> str:
        path_text = str(docset_dir)
        if "User Contributed" in path_text:
            return "user_contributed"
        if "DocSets" in path_text:
            return "dash_app"
        if "Downloads" in path_text:
            return "downloaded"
        return "local_cache"

    @staticmethod
    def _schema_hints(db_path: Path) -> dict[str, Any]:
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = sorted(row[0] for row in cursor.fetchall())
            hints: dict[str, Any] = {"tables": tables}
            if "searchIndex" in tables:
                cursor.execute("PRAGMA table_info(searchIndex)")
                hints["searchIndex_columns"] = [row[1] for row in cursor.fetchall()]
            conn.close()
            return hints
        except sqlite3.Error as exc:
            return {"tables": [], "error": str(exc)}


class DashAugmentationServer:
    """Project-aware recommendation and official-MCP handoff logic."""

    def __init__(self, dash_server: DashMCPServer):
        self.dash_server = dash_server

    async def analyze_project_docs_context(
        self,
        project_path: str,
        max_files: int = DEFAULT_MAX_FILES,
    ) -> ProjectDocsContext:
        project_dir = Path(project_path).expanduser().resolve()
        context = ProjectDocsContext(project_path=str(project_dir))

        if not project_dir.exists():
            return context

        self._inspect_manifests(project_dir, context)
        self._inspect_files(project_dir, context, max_files=max_files)
        self._derive_recommendations(context)
        return context

    async def recommend_dash_docsets(
        self,
        project_path: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        official_docsets: Optional[Any] = None,
        include_local_cache: bool = True,
        force_refresh: bool = False,
        limit: int = 20,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        project_context = await self._resolve_context(project_path, context)
        local_docsets = await self.dash_server.get_local_docsets(force_refresh)
        official_index = OfficialDocsetIndex(official_docsets, warnings)
        recommendations = project_context.recommended_docsets
        docsets, local_candidates = self._build_handoff_docsets(
            recommendations,
            local_docsets,
            official_index,
            include_local_cache=include_local_cache,
            limit=limit,
            warnings=warnings,
        )
        return make_envelope(
            warnings=warnings,
            docsets=docsets,
            searches=[],
            local_cache_candidates=local_candidates,
            extra={"project_context": project_context.to_dict()},
        )

    async def plan_dash_searches(
        self,
        task: str,
        project_path: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        official_docsets: Optional[Any] = None,
        max_queries: int = 12,
        search_snippets: bool = True,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        project_context = await self._resolve_context(project_path, context)
        official_index = OfficialDocsetIndex(official_docsets, warnings)
        local_docsets = await self.dash_server.get_local_docsets()

        docsets, local_candidates = self._build_handoff_docsets(
            project_context.recommended_docsets,
            local_docsets,
            official_index,
            include_local_cache=True,
            limit=20,
            warnings=warnings,
        )
        identifiers = [
            item["official_identifier"]
            for item in docsets
            if item.get("official_identifier")
        ]
        queries = build_search_queries(task, project_context, max_queries=max_queries)
        searches = [
            {
                "query": query,
                "docset_identifiers": ",".join(identifiers),
                "search_snippets": bool(search_snippets),
                "max_results": 20,
                "reason": search_reason(query, task, project_context),
            }
            for query in queries
        ]
        if not identifiers:
            warnings.append(
                "No official docset identifiers are available. Pass the "
                "official Dash list_installed_docsets snapshot for exact handoff."
            )

        return make_envelope(
            warnings=warnings,
            docsets=docsets,
            searches=searches,
            local_cache_candidates=local_candidates,
            extra={"project_context": project_context.to_dict()},
        )

    async def rank_dash_results(
        self,
        official_results: Any,
        task: Optional[str] = None,
        query: Optional[str] = None,
        project_path: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        project_context = await self._resolve_context(project_path, context)
        results = extract_official_results(official_results)
        ranked = rank_results(
            results,
            query=query or task or "",
            project_context=project_context,
        )
        return make_envelope(
            warnings=[],
            docsets=[],
            searches=[],
            local_cache_candidates=[],
            extra={"ranked_results": ranked[:limit]},
        )

    async def summarize_docset_coverage(
        self,
        official_docsets: Optional[Any] = None,
        status_filter: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        local_docsets = await self.dash_server.get_local_docsets(force_refresh)
        official_index = OfficialDocsetIndex(official_docsets, warnings)
        coverage = build_coverage_rows(local_docsets, official_index)

        if query:
            query_key = normalize_name(query)
            coverage = [
                row
                for row in coverage
                if query_key in normalize_name(row.get("name", ""))
                or query_key in normalize_name(row.get("platform", ""))
            ]
        if status_filter:
            coverage = [
                row for row in coverage if row.get("coverage_status") == status_filter
            ]

        total = len(coverage)
        page = coverage[offset: offset + limit]
        docsets = [
            row
            for row in page
            if row.get("coverage_status") in {"matched", "official_only"}
        ]
        local_candidates = [
            row for row in page if row.get("coverage_status") == "local_cache_only"
        ]

        return make_envelope(
            warnings=warnings,
            docsets=docsets,
            searches=[],
            local_cache_candidates=local_candidates,
            extra={
                "coverage_summary": summarize_statuses(coverage),
                "pagination": {"total": total, "limit": limit, "offset": offset},
            },
        )

    async def suggest_offline_docs_for_repo(
        self,
        project_path: str,
        official_docsets: Optional[Any] = None,
        limit: int = 20,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        return await self.recommend_dash_docsets(
            project_path=project_path,
            official_docsets=official_docsets,
            include_local_cache=True,
            force_refresh=force_refresh,
            limit=limit,
        )

    async def explain_missing_docsets(
        self,
        requested_docsets: list[Any],
        official_docsets: Optional[Any] = None,
        force_refresh: bool = False,
    ) -> dict[str, Any]:
        warnings: list[str] = []
        local_docsets = await self.dash_server.get_local_docsets(force_refresh)
        official_index = OfficialDocsetIndex(official_docsets, warnings)
        local_index = build_local_index(local_docsets)
        explanations: list[dict[str, Any]] = []
        local_candidates: list[dict[str, Any]] = []

        for requested in requested_docsets:
            name = str(requested)
            local_matches = local_index.get(normalize_name(name), [])
            match = official_index.best_match(name)
            if match.status == "matched":
                explanations.append(
                    {
                        "name": name,
                        "coverage_status": "matched",
                        "reason": "Dash official already exposes this docset.",
                        "official_identifier": match.official.get("identifier"),
                        "platform": match.official.get("platform"),
                    }
                )
            elif local_matches:
                first = local_matches[0]
                explanations.append(
                    {
                        "name": name,
                        "coverage_status": "local_cache_only",
                        "reason": (
                            "A local cache docset exists, but the official Dash "
                            "snapshot did not expose it."
                        ),
                        "candidate_docset_name": first.name,
                        "candidate_source": first.source,
                    }
                )
                local_candidates.append(local_candidate(first, reason=name))
            else:
                explanations.append(
                    {
                        "name": name,
                        "coverage_status": "missing",
                        "reason": (
                            "No matching official docset or valid local cache "
                            "docset was found."
                        ),
                    }
                )

        return make_envelope(
            warnings=warnings,
            docsets=[],
            searches=[],
            local_cache_candidates=local_candidates,
            extra={"missing_docsets": explanations},
        )

    async def _resolve_context(
        self,
        project_path: Optional[str],
        context: Optional[dict[str, Any]],
    ) -> ProjectDocsContext:
        if context:
            project_context = ProjectDocsContext(
                project_path=context.get("project_path"),
                languages=list(context.get("languages") or []),
                frameworks=list(context.get("frameworks") or []),
                dependencies=list(context.get("dependencies") or []),
                package_managers=list(context.get("package_managers") or []),
                manifest_files=list(context.get("manifest_files") or []),
                current_files=list(context.get("current_files") or []),
                file_counts=dict(context.get("file_counts") or {}),
                recommended_docsets=list(context.get("recommended_docsets") or []),
            )
            if not project_context.recommended_docsets:
                self._derive_recommendations(project_context)
            return project_context
        if project_path:
            return await self.analyze_project_docs_context(project_path)
        return ProjectDocsContext()

    def _inspect_manifests(
        self,
        project_dir: Path,
        context: ProjectDocsContext,
    ) -> None:
        package_json = project_dir / "package.json"
        if package_json.exists():
            context.manifest_files.append("package.json")
            context.package_managers.append("npm")
            try:
                data = json.loads(package_json.read_text())
                deps: list[str] = []
                for section in ("dependencies", "devDependencies", "peerDependencies"):
                    deps.extend((data.get(section) or {}).keys())
                context.dependencies.extend(deps)
                context.languages.append("javascript")
            except (OSError, json.JSONDecodeError) as exc:
                logger.debug("Could not parse package.json: %s", exc)

        for deno_name in ("deno.json", "deno.jsonc"):
            deno_file = project_dir / deno_name
            if deno_file.exists():
                context.manifest_files.append(deno_name)
                context.package_managers.append("deno")
                context.languages.extend(["javascript", "typescript"])
                try:
                    data = json.loads(strip_json_comments(deno_file.read_text()))
                    imports = data.get("imports") or {}
                    context.dependencies.extend(imports.keys())
                except (OSError, json.JSONDecodeError):
                    pass

        self._inspect_python(project_dir, context)
        self._inspect_rust(project_dir, context)
        self._inspect_go(project_dir, context)
        self._inspect_php(project_dir, context)
        self._inspect_ruby(project_dir, context)
        self._inspect_java(project_dir, context)

        context.dependencies = dedupe_preserve_order(context.dependencies)
        context.languages = dedupe_preserve_order(context.languages)
        context.package_managers = dedupe_preserve_order(context.package_managers)
        self._derive_frameworks(context)

    def _inspect_python(self, project_dir: Path, context: ProjectDocsContext) -> None:
        pyproject = project_dir / "pyproject.toml"
        if pyproject.exists():
            context.manifest_files.append("pyproject.toml")
            context.package_managers.append("pip")
            context.languages.append("python")
            try:
                data = tomllib.loads(pyproject.read_text())
                project = data.get("project") or {}
                parsed_deps = [
                    name
                    for dep in project.get("dependencies", [])
                    if (name := dependency_name(dep))
                ]
                context.dependencies.extend(parsed_deps)
                poetry = ((data.get("tool") or {}).get("poetry") or {})
                poetry_deps = poetry.get("dependencies") or {}
                context.dependencies.extend(
                    dep for dep in poetry_deps.keys() if dep.lower() != "python"
                )
            except (OSError, tomllib.TOMLDecodeError):
                pass

        for req_file in sorted(project_dir.glob("requirements*.txt")):
            context.manifest_files.append(req_file.name)
            context.package_managers.append("pip")
            context.languages.append("python")
            try:
                context.dependencies.extend(
                    dep
                    for dep in (
                        parse_requirement_name(line)
                        for line in req_file.read_text().splitlines()
                    )
                    if dep
                )
            except OSError:
                pass

    def _inspect_rust(self, project_dir: Path, context: ProjectDocsContext) -> None:
        cargo = project_dir / "Cargo.toml"
        if not cargo.exists():
            return
        context.manifest_files.append("Cargo.toml")
        context.package_managers.append("cargo")
        context.languages.append("rust")
        try:
            data = tomllib.loads(cargo.read_text())
        except (OSError, tomllib.TOMLDecodeError):
            return
        for section in ("dependencies", "dev-dependencies", "build-dependencies"):
            context.dependencies.extend((data.get(section) or {}).keys())

    def _inspect_go(self, project_dir: Path, context: ProjectDocsContext) -> None:
        go_mod = project_dir / "go.mod"
        if not go_mod.exists():
            return
        context.manifest_files.append("go.mod")
        context.package_managers.append("go")
        context.languages.append("go")
        try:
            for line in go_mod.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith("require "):
                    parts = stripped.removeprefix("require ").split()
                    if parts:
                        context.dependencies.append(parts[0])
        except OSError:
            pass

    def _inspect_php(self, project_dir: Path, context: ProjectDocsContext) -> None:
        composer = project_dir / "composer.json"
        if not composer.exists():
            return
        context.manifest_files.append("composer.json")
        context.package_managers.append("composer")
        context.languages.append("php")
        try:
            data = json.loads(composer.read_text())
            context.dependencies.extend((data.get("require") or {}).keys())
            context.dependencies.extend((data.get("require-dev") or {}).keys())
        except (OSError, json.JSONDecodeError):
            pass

    def _inspect_ruby(self, project_dir: Path, context: ProjectDocsContext) -> None:
        gemfile = project_dir / "Gemfile"
        if not gemfile.exists():
            return
        context.manifest_files.append("Gemfile")
        context.package_managers.append("bundler")
        context.languages.append("ruby")
        try:
            context.dependencies.extend(parse_gem_names(gemfile.read_text()))
        except OSError:
            pass

    def _inspect_java(self, project_dir: Path, context: ProjectDocsContext) -> None:
        pom = project_dir / "pom.xml"
        gradle = project_dir / "build.gradle"
        if pom.exists():
            context.manifest_files.append("pom.xml")
            context.package_managers.append("maven")
            context.languages.append("java")
        if gradle.exists():
            context.manifest_files.append("build.gradle")
            context.package_managers.append("gradle")
            context.languages.append("java")
            try:
                content = gradle.read_text()
                context.dependencies.extend(
                    re.findall(r"['\"]([A-Za-z0-9_.-]+:[A-Za-z0-9_.-]+):", content)
                )
            except OSError:
                pass

    def _inspect_files(
        self,
        project_dir: Path,
        context: ProjectDocsContext,
        max_files: int,
    ) -> None:
        extension_to_language = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".rs": "rust",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".java": "java",
            ".kt": "kotlin",
            ".swift": "swift",
            ".lua": "lua",
        }
        files: list[str] = []
        counts: Counter[str] = Counter()
        for path in project_dir.rglob("*"):
            if len(files) >= max_files:
                break
            if not path.is_file() or any(part.startswith(".") for part in path.parts):
                continue
            if any(part in {"node_modules", "dist", "build", "__pycache__"} for part in path.parts):
                continue
            rel_path = str(path.relative_to(project_dir))
            files.append(rel_path)
            suffix = path.suffix.lower()
            if suffix:
                counts[suffix] += 1
                language = extension_to_language.get(suffix)
                if language:
                    context.languages.append(language)
        context.current_files = files
        context.file_counts = dict(sorted(counts.items()))
        context.languages = dedupe_preserve_order(context.languages)

    def _derive_frameworks(self, context: ProjectDocsContext) -> None:
        deps = {dep.lower() for dep in context.dependencies}
        framework_rules = {
            "react": {"react", "@types/react"},
            "nextjs": {"next"},
            "vue": {"vue", "@vue/core"},
            "angular": {"@angular/core", "angular"},
            "express": {"express"},
            "svelte": {"svelte"},
            "fastapi": {"fastapi"},
            "django": {"django"},
            "flask": {"flask"},
            "pydantic": {"pydantic"},
            "pytest": {"pytest"},
            "rails": {"rails"},
            "laravel": {"laravel/framework"},
        }
        frameworks = list(context.frameworks)
        for framework, markers in framework_rules.items():
            if deps & markers:
                frameworks.append(framework)
        if "typescript" in context.languages:
            frameworks.append("typescript")
        context.frameworks = dedupe_preserve_order(frameworks)

    def _derive_recommendations(self, context: ProjectDocsContext) -> None:
        recommendations: list[dict[str, str]] = []

        def add(name: str, reason: str) -> None:
            if normalize_name(name) not in {
                normalize_name(item["name"]) for item in recommendations
            }:
                recommendations.append({"name": name, "reason": reason})

        for language in context.languages:
            docset_name = LANGUAGE_DOCSETS.get(language)
            if docset_name:
                add(docset_name, f"Project uses {language}.")
        for framework in context.frameworks:
            docset_name = FRAMEWORK_DOCSETS.get(framework)
            if docset_name:
                add(docset_name, f"Project uses {framework}.")
        for dependency in context.dependencies[:80]:
            docset_name = DEPENDENCY_DOCSETS.get(dependency.lower())
            if docset_name:
                add(docset_name, f"Project depends on {dependency}.")

        context.recommended_docsets = recommendations

    def _build_handoff_docsets(
        self,
        recommendations: list[dict[str, str]],
        local_docsets: list[LocalDocset],
        official_index: "OfficialDocsetIndex",
        include_local_cache: bool,
        limit: int,
        warnings: list[str],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        local_index = build_local_index(local_docsets)
        docsets: list[dict[str, Any]] = []
        local_candidates: list[dict[str, Any]] = []

        for recommendation in recommendations[:limit]:
            name = recommendation["name"]
            reason = recommendation["reason"]
            match = official_index.best_match(name)
            if match.status == "ambiguous":
                warnings.append(
                    f"Ambiguous official Dash matches for {name}: "
                    + ", ".join(item.get("name", "") for item in match.matches)
                )
                docsets.append(
                    handoff_docset(
                        name=name,
                        reason=reason,
                        coverage_status="ambiguous_official",
                    )
                )
                continue

            if match.status == "matched":
                docsets.append(
                    handoff_docset(
                        name=match.official.get("name", name),
                        reason=reason,
                        coverage_status="matched",
                        official=match.official,
                    )
                )
                continue

            local_matches = local_index.get(normalize_name(name), [])
            if local_matches:
                docsets.append(
                    handoff_docset(
                        name=name,
                        reason=reason,
                        coverage_status="local_cache_only",
                    )
                )
                if include_local_cache and official_index.has_snapshot:
                    local_candidates.append(local_candidate(local_matches[0], reason))
                    warnings.append(
                        f"{name} is available in the local Dash cache, "
                        "but not in the official Dash snapshot."
                    )
                continue

            docsets.append(
                handoff_docset(
                    name=name,
                    reason=reason,
                    coverage_status="missing",
                )
            )

        return docsets, local_candidates


def dependency_name(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    return parse_requirement_name(value)


LANGUAGE_DOCSETS = {
    "python": "Python 3",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "rust": "Rust",
    "go": "Go",
    "ruby": "Ruby",
    "php": "PHP",
    "java": "Java",
    "kotlin": "Kotlin",
    "swift": "Swift",
    "lua": "Lua",
}

FRAMEWORK_DOCSETS = {
    "react": "React",
    "nextjs": "Next.js",
    "vue": "Vue",
    "angular": "Angular",
    "express": "Express",
    "svelte": "Svelte",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "pydantic": "Pydantic",
    "pytest": "pytest",
    "rails": "Ruby on Rails",
    "laravel": "Laravel",
    "typescript": "TypeScript",
}

DEPENDENCY_DOCSETS = {
    "beautifulsoup4": "Beautiful Soup",
    "bs4": "Beautiful Soup",
    "numpy": "NumPy",
    "pandas": "pandas",
    "requests": "Requests",
    "sqlalchemy": "SQLAlchemy",
    "mcp": "Model Context Protocol",
    "pydantic": "Pydantic",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "pytest": "pytest",
    "react": "React",
    "next": "Next.js",
    "express": "Express",
    "lodash": "Lodash",
    "axios": "Axios",
    "zod": "Zod",
    "vue": "Vue",
    "svelte": "Svelte",
    "rails": "Ruby on Rails",
}


@dataclass
class OfficialMatch:
    status: str
    official: dict[str, Any] = field(default_factory=dict)
    matches: list[dict[str, Any]] = field(default_factory=list)


class OfficialDocsetIndex:
    """Optional snapshot of official Dash MCP list_installed_docsets output."""

    def __init__(self, snapshot: Optional[Any], warnings: list[str]):
        self.docsets = coerce_official_docsets(snapshot)
        self.has_snapshot = snapshot is not None
        if snapshot is None:
            warnings.append(
                "No official Dash docset snapshot supplied. Official identifiers "
                "cannot be attached."
            )

    def best_match(self, name: str) -> OfficialMatch:
        if not self.docsets:
            return OfficialMatch(status="missing")

        target_keys = aliases_for_name(name)
        scored: list[tuple[int, dict[str, Any]]] = []
        for docset in self.docsets:
            docset_keys = aliases_for_name(
                " ".join(
                    str(docset.get(key) or "")
                    for key in ("name", "platform", "identifier")
                )
            )
            if target_keys & docset_keys:
                scored.append((100, docset))
                continue
            if any(
                target in candidate or candidate in target
                for target in target_keys
                for candidate in docset_keys
                if len(target) >= 4 and len(candidate) >= 4
            ):
                scored.append((75, docset))

        if not scored:
            return OfficialMatch(status="missing")

        best_score = max(score for score, _docset in scored)
        best = [docset for score, docset in scored if score == best_score]
        if len(best) > 1:
            return OfficialMatch(status="ambiguous", matches=best)
        return OfficialMatch(status="matched", official=best[0], matches=best)


def aliases_for_name(name: str) -> set[str]:
    normalized = normalize_name(name)
    aliases = {normalized}
    substitutions = {
        "python3": "python",
        "nodejs": "node",
        "node": "nodejs",
        "javascript": "js",
        "js": "javascript",
        "typescript": "ts",
        "ts": "typescript",
        "nextjs": "next",
        "beautifulsoup": "bs4",
        "ruby-on-rails": "rails",
    }
    if normalized in substitutions:
        aliases.add(substitutions[normalized])
    return {alias for alias in aliases if alias}


def coerce_official_docsets(snapshot: Optional[Any]) -> list[dict[str, Any]]:
    if snapshot is None:
        return []
    raw_docsets = snapshot.get("docsets") if isinstance(snapshot, dict) else snapshot
    if not isinstance(raw_docsets, list):
        return []
    docsets: list[dict[str, Any]] = []
    for item in raw_docsets:
        if not isinstance(item, dict):
            continue
        docsets.append(
            {
                "name": str(item.get("name") or ""),
                "identifier": item.get("identifier"),
                "platform": item.get("platform"),
                "full_text_search": item.get("full_text_search"),
                "notice": item.get("notice"),
            }
        )
    return docsets


def build_local_index(docsets: list[LocalDocset]) -> dict[str, list[LocalDocset]]:
    index: dict[str, list[LocalDocset]] = defaultdict(list)
    for docset in docsets:
        for value in (
            docset.name,
            docset.display_name,
            docset.platform_family,
            docset.bundle_identifier,
        ):
            if value:
                index[normalize_name(value)].append(docset)
    return index


def handoff_docset(
    name: str,
    reason: str,
    coverage_status: str,
    official: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    official = official or {}
    return {
        "name": name,
        "official_identifier": official.get("identifier"),
        "platform": official.get("platform"),
        "full_text_search": official.get("full_text_search"),
        "coverage_status": coverage_status,
        "reason": reason,
    }


def local_candidate(docset: LocalDocset, reason: str) -> dict[str, Any]:
    return {
        "name": docset.name,
        "display_name": docset.display_name,
        "platform": docset.platform_family,
        "source": docset.source,
        "db_path": docset.db_path,
        "docs_path": docset.docs_path,
        "coverage_status": "local_cache_only",
        "reason": reason,
    }


def build_search_queries(
    task: str,
    context: ProjectDocsContext,
    max_queries: int,
) -> list[str]:
    seeds = [task]
    seeds.extend(f"{framework} {task}" for framework in context.frameworks[:5])
    seeds.extend(f"{language} {task}" for language in context.languages[:5])
    seeds.extend(f"{dependency} {task}" for dependency in context.dependencies[:5])
    if re.search(r"\b(upgrade|migrate|migration|breaking)\b", task, re.I):
        seeds.extend(f"{name} migration guide" for name in context.frameworks[:3])
    return dedupe_preserve_order(seeds)[:max_queries]


def search_reason(
    query: str,
    task: str,
    context: ProjectDocsContext,
) -> str:
    if query == task:
        return "Direct task search."
    for framework in context.frameworks:
        if query.lower().startswith(framework.lower()):
            return f"Project uses {framework}; search task in that context."
    for language in context.languages:
        if query.lower().startswith(language.lower()):
            return f"Project uses {language}; search task in that context."
    return "Dependency-aware search derived from project context."


def extract_official_results(official_results: Any) -> list[dict[str, Any]]:
    if isinstance(official_results, dict):
        for key in ("results", "matches", "items"):
            value = official_results.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if "load_url" in official_results:
            return [official_results]
    if isinstance(official_results, list):
        return [item for item in official_results if isinstance(item, dict)]
    return []


def rank_results(
    results: list[dict[str, Any]],
    query: str,
    project_context: ProjectDocsContext,
) -> list[dict[str, Any]]:
    tokens = {
        token
        for token in re.findall(r"[A-Za-z0-9_]+", query.lower())
        if len(token) >= 3
    }
    tokens.update(framework.lower() for framework in project_context.frameworks)
    tokens.update(language.lower() for language in project_context.languages)
    ranked: list[dict[str, Any]] = []
    for result in results:
        haystack = " ".join(
            str(result.get(key) or "")
            for key in (
                "name",
                "title",
                "docset",
                "docset_name",
                "platform",
                "type",
                "snippet",
                "summary",
                "path",
            )
        ).lower()
        score = sum(10 for token in tokens if token and token in haystack)
        if query and query.lower() in haystack:
            score += 25
        if result.get("load_url"):
            score += 5
        ranked_result = dict(result)
        ranked_result["augmentation_score"] = score
        ranked.append(ranked_result)
    return sorted(ranked, key=lambda item: item["augmentation_score"], reverse=True)


def build_coverage_rows(
    local_docsets: list[LocalDocset],
    official_index: OfficialDocsetIndex,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    matched_official_ids: set[str] = set()
    for local in local_docsets:
        match = official_index.best_match(local.name)
        if match.status == "matched":
            official = match.official
            matched_official_ids.add(str(official.get("identifier")))
            rows.append(
                handoff_docset(
                    name=official.get("name") or local.name,
                    reason=f"Local cache docset matched {local.name}.",
                    coverage_status="matched",
                    official=official,
                )
            )
        elif match.status == "ambiguous":
            rows.append(
                handoff_docset(
                    name=local.name,
                    reason="Multiple official Dash docsets may match this cache docset.",
                    coverage_status="ambiguous_official",
                )
            )
        elif official_index.has_snapshot:
            rows.append(local_candidate(local, reason="Local cache docset only."))
        else:
            rows.append(
                {
                    "name": local.name,
                    "platform": local.platform_family,
                    "coverage_status": "unknown_without_snapshot",
                    "reason": "No official Dash snapshot supplied.",
                }
            )

    for official in official_index.docsets:
        identifier = str(official.get("identifier"))
        if identifier in matched_official_ids:
            continue
        rows.append(
            handoff_docset(
                name=official.get("name") or identifier,
                reason="Official Dash exposes this docset; no local cache match was found.",
                coverage_status="official_only",
                official=official,
            )
        )
    return sorted(rows, key=lambda row: str(row.get("name", "")).lower())


def summarize_statuses(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter(str(row.get("coverage_status")) for row in rows)
    return dict(sorted(counts.items()))


def make_envelope(
    warnings: list[str],
    docsets: list[dict[str, Any]],
    searches: list[dict[str, Any]],
    local_cache_candidates: list[dict[str, Any]],
    extra: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    payload = {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "official_handoff": {
            "docsets": docsets,
            "searches": searches,
        },
        "local_cache_candidates": local_cache_candidates,
        "warnings": dedupe_preserve_order(warnings),
    }
    if extra:
        payload.update(extra)
    return payload


TOOL_DEFINITIONS: dict[str, ToolDefinition] = {
    "analyze_project_docs_context": ToolDefinition(
        name="analyze_project_docs_context",
        description="Analyze a repository to detect docs-relevant technology context.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "max_files": {"type": "integer", "default": DEFAULT_MAX_FILES},
            },
            "required": ["project_path"],
        },
    ),
    "recommend_dash_docsets": ToolDefinition(
        name="recommend_dash_docsets",
        description="Recommend Dash docsets and official-MCP handoff identifiers.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "context": {"type": "object"},
                "official_docsets": {"type": ["object", "array"]},
                "include_local_cache": {"type": "boolean", "default": True},
                "force_refresh": {"type": "boolean", "default": False},
                "limit": {"type": "integer", "default": 20},
            },
        },
    ),
    "plan_dash_searches": ToolDefinition(
        name="plan_dash_searches",
        description="Plan search_documentation calls for the official Dash MCP.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "project_path": {"type": "string"},
                "context": {"type": "object"},
                "official_docsets": {"type": ["object", "array"]},
                "max_queries": {"type": "integer", "default": 12},
                "search_snippets": {"type": "boolean", "default": True},
            },
            "required": ["task"],
        },
    ),
    "rank_dash_results": ToolDefinition(
        name="rank_dash_results",
        description="Rank results returned by the official Dash MCP search tool.",
        input_schema={
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "query": {"type": "string"},
                "official_results": {"type": ["object", "array"]},
                "project_path": {"type": "string"},
                "context": {"type": "object"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["official_results"],
        },
    ),
    "summarize_docset_coverage": ToolDefinition(
        name="summarize_docset_coverage",
        description="Summarize official Dash visibility versus local cache docsets.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "official_docsets": {"type": ["object", "array"]},
                "status_filter": {"type": "string"},
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
                "offset": {"type": "integer", "default": 0},
                "force_refresh": {"type": "boolean", "default": False},
            },
        },
    ),
    "suggest_offline_docs_for_repo": ToolDefinition(
        name="suggest_offline_docs_for_repo",
        description="Suggest offline Dash docs for a repository and task handoff.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "project_path": {"type": "string"},
                "official_docsets": {"type": ["object", "array"]},
                "limit": {"type": "integer", "default": 20},
                "force_refresh": {"type": "boolean", "default": False},
            },
            "required": ["project_path"],
        },
    ),
    "explain_missing_docsets": ToolDefinition(
        name="explain_missing_docsets",
        description="Explain whether requested docsets are official, local-only, or missing.",
        safe=False,
        input_schema={
            "type": "object",
            "properties": {
                "requested_docsets": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "official_docsets": {"type": ["object", "array"]},
                "force_refresh": {"type": "boolean", "default": False},
            },
            "required": ["requested_docsets"],
        },
    ),
}


def create_server(name: str) -> Server:
    try:
        return Server(name)
    except TypeError:
        return cast(Any, Server)()


server: Server = create_server("dash-docs-enhanced")
dash_server = DashMCPServer()
augmentation_server = DashAugmentationServer(dash_server)


async def list_capabilities(target_server: Server) -> Any:
    return cast(Any, target_server).get_capabilities()


async def handle_initialize(target_server: Server, request: Any) -> dict[str, Any]:
    if getattr(request, "method", None) == "initialize":
        return {
            "protocolVersion": "2025-03-26",
            "capabilities": await list_capabilities(target_server),
            "serverInfo": {
                "name": "Enhanced Dash Augmentation Server",
                "version": __version__,
            },
        }
    return {}


@server.list_tools()
async def list_tools() -> list[Tool]:
    names = list(TOOL_DEFINITIONS)
    if len(names) != len(set(names)):
        raise RuntimeError("Duplicate tool names in TOOL_DEFINITIONS")
    return [definition.to_tool() for definition in TOOL_DEFINITIONS.values()]


async def _handle_analyze_project_docs_context(
    arguments: dict[str, Any],
) -> dict[str, Any]:
    context = await augmentation_server.analyze_project_docs_context(
        str(arguments["project_path"]),
        max_files=clamp_int(arguments.get("max_files"), DEFAULT_MAX_FILES, 1, 1000),
    )
    return make_envelope(
        warnings=[],
        docsets=[],
        searches=[],
        local_cache_candidates=[],
        extra={"project_context": context.to_dict()},
    )


async def _handle_recommend_dash_docsets(
    arguments: dict[str, Any],
) -> dict[str, Any]:
    return await augmentation_server.recommend_dash_docsets(
        project_path=arguments.get("project_path"),
        context=arguments.get("context"),
        official_docsets=arguments.get("official_docsets"),
        include_local_cache=bool(arguments.get("include_local_cache", True)),
        force_refresh=bool(arguments.get("force_refresh", False)),
        limit=clamp_int(arguments.get("limit"), 20, 1, 100),
    )


async def _handle_plan_dash_searches(arguments: dict[str, Any]) -> dict[str, Any]:
    if not str(arguments.get("task", "")).strip():
        raise ValueError("task parameter is required")
    return await augmentation_server.plan_dash_searches(
        task=str(arguments["task"]),
        project_path=arguments.get("project_path"),
        context=arguments.get("context"),
        official_docsets=arguments.get("official_docsets"),
        max_queries=clamp_int(arguments.get("max_queries"), 12, 1, 50),
        search_snippets=bool(arguments.get("search_snippets", True)),
    )


async def _handle_rank_dash_results(arguments: dict[str, Any]) -> dict[str, Any]:
    return await augmentation_server.rank_dash_results(
        official_results=arguments["official_results"],
        task=arguments.get("task"),
        query=arguments.get("query"),
        project_path=arguments.get("project_path"),
        context=arguments.get("context"),
        limit=clamp_int(arguments.get("limit"), 20, 1, 100),
    )


async def _handle_summarize_docset_coverage(
    arguments: dict[str, Any],
) -> dict[str, Any]:
    return await augmentation_server.summarize_docset_coverage(
        official_docsets=arguments.get("official_docsets"),
        status_filter=arguments.get("status_filter"),
        query=arguments.get("query"),
        limit=clamp_int(arguments.get("limit"), 50, 1, 500),
        offset=clamp_int(arguments.get("offset"), 0, 0, 1_000_000),
        force_refresh=bool(arguments.get("force_refresh", False)),
    )


async def _handle_suggest_offline_docs_for_repo(
    arguments: dict[str, Any],
) -> dict[str, Any]:
    return await augmentation_server.suggest_offline_docs_for_repo(
        project_path=str(arguments["project_path"]),
        official_docsets=arguments.get("official_docsets"),
        limit=clamp_int(arguments.get("limit"), 20, 1, 100),
        force_refresh=bool(arguments.get("force_refresh", False)),
    )


async def _handle_explain_missing_docsets(
    arguments: dict[str, Any],
) -> dict[str, Any]:
    requested = arguments.get("requested_docsets")
    if not isinstance(requested, list):
        raise ValueError("requested_docsets must be a list")
    return await augmentation_server.explain_missing_docsets(
        requested_docsets=requested,
        official_docsets=arguments.get("official_docsets"),
        force_refresh=bool(arguments.get("force_refresh", False)),
    )


ToolHandler = Callable[[dict[str, Any]], Any]

TOOL_HANDLERS: dict[str, ToolHandler] = {
    "analyze_project_docs_context": _handle_analyze_project_docs_context,
    "recommend_dash_docsets": _handle_recommend_dash_docsets,
    "plan_dash_searches": _handle_plan_dash_searches,
    "rank_dash_results": _handle_rank_dash_results,
    "summarize_docset_coverage": _handle_summarize_docset_coverage,
    "suggest_offline_docs_for_repo": _handle_suggest_offline_docs_for_repo,
    "explain_missing_docsets": _handle_explain_missing_docsets,
}


def text_content(text: str, is_error: bool = False) -> TextContent:
    kwargs: dict[str, Any] = {"type": "text", "text": text}
    if is_error:
        kwargs["isError"] = True
    try:
        return TextContent(**kwargs)
    except TypeError:
        return TextContent(type="text", text=text)


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    try:
        if name not in TOOL_HANDLERS:
            raise ValueError(f"Unknown tool: {name}")
        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be an object")
        payload = await TOOL_HANDLERS[name](arguments)
        return [
            text_content(
                json.dumps(payload, indent=2, sort_keys=True),
                is_error=False,
            )
        ]
    except ValueError as exc:
        return [text_content(f"Error: {exc}", is_error=True)]
    except Exception as exc:
        logger.exception("Unexpected error in tool %s: %s", name, exc)
        return [
            text_content(
                "An unexpected error occurred. Please check server logs.",
                is_error=True,
            )
        ]


class RateLimiter:
    def __init__(self, max_calls: int = 100, window_seconds: int = 60) -> None:
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self.calls: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str = "default") -> bool:
        now = time.time()
        self.calls[client_id] = [
            call_time
            for call_time in self.calls[client_id]
            if now - call_time < self.window_seconds
        ]
        if len(self.calls[client_id]) >= self.max_calls:
            return False
        self.calls[client_id].append(now)
        return True


rate_limiter = RateLimiter()


async def rate_limited_call_tool(name: str, arguments: Any) -> list[TextContent]:
    if not rate_limiter.is_allowed():
        return [
            text_content(
                "Rate limit exceeded. Please wait before making more requests.",
                is_error=True,
            )
        ]
    return await call_tool(name, arguments)


@contextlib.asynccontextmanager
async def stdio_context() -> Any:
    context: Any = stdio_server()
    if hasattr(context, "__aenter__"):
        async with context as streams:
            yield streams
        return

    try:
        streams = await context.__anext__()
        yield streams
    finally:
        await context.aclose()


async def _cancel_task(task: asyncio.Task[Any]) -> None:
    """Cancel a task and wait for it to finish."""
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError, KeyboardInterrupt):
        await task


async def amain() -> None:
    """Run the server with STDIO streams and handle cancellation."""
    logger.info("Enhanced Dash MCP server starting (logs: %s)", LOG_FILE)
    interactive = is_interactive_mode()
    mode = "interactive" if interactive else "non-interactive"
    logger.info("Running in %s mode", mode)

    async with stdio_context() as (read_stream, write_stream):
        init_options: Any = (
            server.create_initialization_options()
            if hasattr(server, "create_initialization_options")
            else {}
        )
        server_task = asyncio.create_task(
            server.run(read_stream, write_stream, init_options)
        )
        try:
            await server_task
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.info("Received interrupt signal in %s mode", mode)
            await _cancel_task(server_task)
        except Exception as exc:
            logger.exception("Error running server: %s", exc)
            await _cancel_task(server_task)
            raise
        finally:
            logger.info("Enhanced Dash MCP server stopped (was running in %s mode)", mode)


def main() -> None:
    """Console script entry point."""
    asyncio.run(amain())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Enhanced Dash MCP Server - Test Mode")
        print(f"Docsets path: {DashMCPServer().docsets_path}")
        print(f"Index path: {DashMCPServer().index_path}")
        print(f"Log file: {LOG_FILE}")

        async def test_docsets() -> bool:
            server_instance = DashMCPServer()
            docsets = await server_instance.get_available_docsets()
            print(f"Found {len(docsets)} local cache docsets")
            if docsets:
                print("Sample docsets:", [docset["name"] for docset in docsets[:3]])
            return True

        try:
            asyncio.run(test_docsets())
            print("Server test completed successfully")
            sys.exit(0)
        except Exception as exc:
            print(f"Server test failed: {exc}")
            sys.exit(1)

    main()
