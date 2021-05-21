import pytest
from project_name import hello


@pytest.mark.parametrize(
    "name",
    [
        None,
        "",
        "  ",
    ],
)
def test_error_hello(name):
    with pytest.raises(ValueError):
        hello(name)


@pytest.mark.parametrize(
    "name",
    [
        "Memgraph",
        "Multiple words",
        '"Escaped"',
    ],
)
def test_correct_hello(name):
    hello_name = hello(name)
    assert hello_name == f'Hello project "{name}"'
