import sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

# allow: from src.core import otherwise it breaks
sys.path.insert(0, str(ROOT))
# allow: from core import otherwise it breaks
sys.path.insert(0, str(SRC))
