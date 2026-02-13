import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent.parent / "data"
