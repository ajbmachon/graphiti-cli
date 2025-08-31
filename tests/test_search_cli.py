import json
from click.testing import CliRunner
from unittest.mock import AsyncMock, MagicMock, patch


class FakeEdge:
    def __init__(self, data):
        self._data = data

    def model_dump(self, mode='json'):
        return dict(self._data)


class FakeNode:
    def __init__(self, data):
        self._data = data

    def model_dump(self, mode='json'):
        return dict(self._data)


def make_mock_client_for_fallback():
    client = MagicMock()
    client.search = AsyncMock(return_value=[])  # no edges

    class NodeResult:
        def __init__(self):
            self.nodes = [FakeNode({
                'uuid': 'n1', 'name': 'Auth', 'entity_type': 'Component', 'group_id': 'test'
            })]

    client.search_ = AsyncMock(return_value=NodeResult())
    return client


def make_mock_client_for_edges():
    client = MagicMock()
    client.search = AsyncMock(return_value=[FakeEdge({'uuid': 'u1', 'name': 'RELATES_TO', 'fact': 'A->B', 'group_id': 'g'})])
    client.search_ = AsyncMock()
    return client


def test_search_accepts_z_datetime_and_node_fallback(monkeypatch):
    from cli.commands.search import search_command
    import click
    runner = CliRunner()
    mock_client = make_mock_client_for_fallback()
    monkeypatch.setenv('NEO4J_PASSWORD', 'pw')
    # Minimal wrapper group that injects our client object
    @click.group()
    @click.pass_context
    def app(ctx):
        class C:
            def get_client(self_non):
                return mock_client
        ctx.obj = C()
    app.add_command(search_command)
    result = runner.invoke(app, [
        'search', 'integration', '-g', 'test', '--created-after', '2025-08-31T12:00:00Z', '-o', 'json'
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert isinstance(data, list) and data, 'expected node fallback results'
    # Ensure node fallback was used
    assert mock_client.search.await_count == 1
    assert mock_client.search_.await_count == 1


def test_search_center_node_ids_only(monkeypatch):
    from cli.commands.search import search_command
    import click
    runner = CliRunner()
    mock_client = make_mock_client_for_edges()
    monkeypatch.setenv('NEO4J_PASSWORD', 'pw')
    @click.group()
    @click.pass_context
    def app(ctx):
        class C:
            def get_client(self_non):
                return mock_client
        ctx.obj = C()
    app.add_command(search_command)
    result = runner.invoke(app, [
        'search', 'x', '--center-node', '123', '--ids-only', '-o', 'json'
    ])
    assert result.exit_code == 0, result.output
    ids = json.loads(result.output)
    assert ids == ['u1']
    assert mock_client.search.await_count == 1
