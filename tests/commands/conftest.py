import pytest


@pytest.fixture
def default_list() -> list[str]:
    return ["lorem ipsum", "dolor sit amet"]
