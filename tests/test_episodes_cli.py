import json
import types
from click.testing import CliRunner
from unittest.mock import AsyncMock, MagicMock, patch

from cli.commands.episodes import episode_group
import click


class FakeEpisode:
    def __init__(self, payload):
        self._payload = payload

    def model_dump(self, mode='json'):
        return dict(self._payload)


def test_episodes_get_after_z_succeeds_and_filters(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv('NEO4J_PASSWORD', 'pw')

    # Create a fake retrieve_episodes in a fake module tree
    mod = types.ModuleType('graphiti_core.utils.maintenance.graph_data_operations')

    async def retrieve_episodes(driver, reference_time, last_n, group_ids=None):
        return [
            FakeEpisode({'uuid': 'a', 'valid_at': '2025-08-31T15:20:00Z'}),
            FakeEpisode({'uuid': 'b', 'valid_at': '2025-08-31T15:40:00Z'}),
        ]

    mod.retrieve_episodes = retrieve_episodes

    # Inject module path into sys.modules
    import sys
    sys.modules['graphiti_core'] = sys.modules.get('graphiti_core', types.ModuleType('graphiti_core'))
    sys.modules['graphiti_core.utils'] = types.ModuleType('graphiti_core.utils')
    sys.modules['graphiti_core.utils.maintenance'] = types.ModuleType('graphiti_core.utils.maintenance')
    sys.modules['graphiti_core.utils.maintenance.graph_data_operations'] = mod

    # Patch client
    mock_client = MagicMock()
    @click.group()
    @click.pass_context
    def app(ctx):
        class C:
            def get_client(self_non):
                return mock_client
        ctx.obj = C()
    app.add_command(episode_group)
    result = runner.invoke(app, [
        'episodes', 'get', '--group-id', 'x', '--after', '2025-08-31T15:30:00Z', '-o', 'json'
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    uuids = [d['uuid'] for d in data]
    assert uuids == ['b']  # only the later episode remains


def test_episodes_add_formats_result(monkeypatch):
    runner = CliRunner()
    monkeypatch.setenv('NEO4J_PASSWORD', 'pw')

    class AddResult:
        class _Ep:
            def model_dump(self, mode='json'):
                return {'uuid': 'ep1', 'name': 'T', 'group_id': 'g'}
        episode = _Ep()
        nodes = [1, 2]
        edges = [1]

    mock_client = MagicMock()
    mock_client.add_episode = AsyncMock(return_value=AddResult())

    @click.group()
    @click.pass_context
    def app2(ctx):
        class C:
            def get_client(self_non):
                return mock_client
        ctx.obj = C()
    app2.add_command(episode_group)
    result = runner.invoke(app2, ['episodes', 'add', 'T', 'body', '--source', 'text', '--group-id', 'g'])
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data['episode']['name'] == 'T'
    assert data['nodes_created'] == 2 and data['edges_created'] == 1
