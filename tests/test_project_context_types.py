from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"


def test_project_context_optional_lists() -> None:
    content = FILE_PATH.read_text()
    assert "class ProjectDocsContext" in content
    assert "dependencies: list[str] = field(default_factory=list)" in content
    assert "current_files: list[str] = field(default_factory=list)" in content
