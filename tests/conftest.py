from pathlib import Path
import pytest
from src.tools import Store, Tools


@pytest.fixture
def tools():
    return Tools(Store(Path(__file__).resolve().parents[1] / 'data' / 'original'))
