from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"


def test_changelog_preserves_history():
    content = CHANGELOG.read_text()
    assert "1.0.0" in content, "Full changelog history is missing"


def test_changelog_header_present():
    first_line = CHANGELOG.read_text().splitlines()[0].strip()
    assert first_line == "# Changelog", "Changelog header missing"


def test_latest_release_at_top():
    """Ensure the latest version entry is directly below the header."""
    lines = [line.strip() for line in CHANGELOG.read_text().splitlines()]
    assert lines[1].startswith("## [2.0.0]"), "Latest release is not at the top"
