import re
from pathlib import Path

FILE_PATH = Path(__file__).resolve().parents[1] / "enhanced_dash_server.py"

VERSION_RE = re.compile(r"__version__\s*=\s*\"(.+)\"")


def test_version_constant():
    content = FILE_PATH.read_text()
    match = VERSION_RE.search(content)
    assert match, "__version__ not found"
    assert match.group(1) == "2.0.0"
