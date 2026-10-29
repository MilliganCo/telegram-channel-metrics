import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock


def load_analysis():
    source = Path(__file__).parents[1] / 'analyse.py'
    tree = ast.parse(source.read_text(encoding='utf-8-sig'))
    node = next(item for item in tree.body if isinstance(item, ast.AsyncFunctionDef) and item.name == 'analyze_channel')
    namespace = {'POSTS_LIMIT': 50, 'print': Mock()}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
    return namespace['analyze_channel']


class MetricsTests(unittest.IsolatedAsyncioTestCase):
    async def test_averages_use_available_message_fields(self):
        client = SimpleNamespace(get_entity=AsyncMock(return_value=SimpleNamespace(participants_count=123)),
            get_messages=AsyncMock(return_value=[
                SimpleNamespace(views=100, reactions=SimpleNamespace(results=[SimpleNamespace(count=2), SimpleNamespace(count=4)])),
                SimpleNamespace(views=None, reactions=None),
                SimpleNamespace(views=300, reactions=SimpleNamespace(results=[SimpleNamespace(count=2)])),
            ]))
        result = await load_analysis()(client, 'synthetic-channel', posts_limit=3)
        self.assertEqual(result['average_views'], 200)
        self.assertEqual(result['average_reactions'], 4)
        self.assertEqual(result['subscribers'], 123)
        self.assertEqual(result['channel'], 'synthetic-channel')
        client.get_messages.assert_awaited_once_with(unittest.mock.ANY, limit=3)

    async def test_empty_history_and_error_are_handled(self):
        client = SimpleNamespace(get_entity=AsyncMock(return_value=SimpleNamespace(participants_count=0)),
                                 get_messages=AsyncMock(return_value=[]))
        result = await load_analysis()(client, 'synthetic-channel')
        self.assertEqual((result['average_views'], result['average_reactions']), (0, 0))
        client.get_entity.side_effect = RuntimeError('synthetic unavailable')
        self.assertIsNone(await load_analysis()(client, 'synthetic-channel'))


if __name__ == '__main__':
    unittest.main()
