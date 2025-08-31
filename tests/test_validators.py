import click
from cli.utils.validators import validate_group_ids, validate_entity_types, validate_edge_types


def test_validate_group_ids_trims_and_returns_list():
    assert validate_group_ids((" a ", "b")) == ["a", "b"]


def test_validate_entity_types_case_insensitive_and_errors():
    out = validate_entity_types(("component", "Project"))
    assert out == ["Component", "Project"]
    
    import pytest
    with pytest.raises(click.ClickException):
        validate_entity_types(("Nope",))


def test_validate_edge_types_case_insensitive_and_errors():
    out = validate_edge_types(("depends_on", "DOCUMENTS"))
    assert out == ["DEPENDS_ON", "DOCUMENTS"]
    
    import pytest
    with pytest.raises(click.ClickException):
        validate_edge_types(("not_an_edge",))
