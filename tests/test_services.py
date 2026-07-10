import json
from datetime import datetime, timezone
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.models import Document
from app.services import (
    DocumentNotFoundError, delete_document, search_documents
)


def rows_result(values):
    result = MagicMock()
    result.scalars.return_value.all.return_value = values
    return result


async def request(method: str, path: str, payload: dict | None = None):
    body = json.dumps(payload).encode() if payload is not None else b''
    messages = []
    received = False

    async def receive():
        nonlocal received
        if not received:
            received = True
            return {'type': 'http.request', 'body': body, 'more_body': False}
        return {'type': 'http.disconnect'}

    async def send(message):
        messages.append(message)

    await app(
        {
            'type': 'http',
            'asgi': {'version': '3.0'},
            'http_version': '1.1',
            'method': method,
            'scheme': 'http',
            'path': path,
            'raw_path': path.encode(),
            'query_string': b'',
            'headers': [(b'content-type', b'application/json')],
            'client': ('testclient', 50000),
            'server': ('testserver', 80),
        },
        receive,
        send,
    )
    status = next(
        message['status']
        for message in messages if message['type'] == 'http.response.start'
    )
    response_body = b''.join(
        message.get('body', b'')
        for message in messages
        if message['type'] == 'http.response.body'
    )
    return status, response_body


class ServiceTests(IsolatedAsyncioTestCase):
    async def test_search_doesnt_query_pg_when_elasticsearch_has_no_hits(self):
        session = MagicMock()
        session.execute = AsyncMock()

        with patch(
            'app.services.elasticsearch_client.search',
            new=AsyncMock(return_value={'hits': {'hits': []}}),
        ):
            documents = await search_documents(session, 'nothing')

        self.assertEqual(documents, [])
        session.execute.assert_not_awaited()

    async def test_delete_logs_elasticsearch_failure_after_db_commit(self):
        session = MagicMock()
        session.get = AsyncMock(return_value=MagicMock())
        session.delete = AsyncMock()
        session.commit = AsyncMock()

        with (
            patch(
                'app.services.elasticsearch_client.delete',
                new=AsyncMock(side_effect=ConnectionError),
            ),
            patch('app.services.logger.exception'),
        ):
            await delete_document(session, 7)

        session.commit.assert_awaited_once()


class ApiFunctionalTests(IsolatedAsyncioTestCase):
    async def test_search_endpoint_returns_documents(self):
        document = Document(
            id=1,
            rubrics=['python'],
            text='FastAPI',
            created_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )
        with patch(
            'app.api.v1.search.search_documents',
            new=AsyncMock(return_value=[document]),
        ):
            status, body = await request(
                'POST', '/api/v1/search', {'text': 'FastAPI'}
            )

        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['documents'][0]['id'], 1)

    async def test_delete_endpoint_returns_no_content(self):
        with patch(
            'app.api.v1.documents.delete_document',
            new=AsyncMock(),
        ) as delete:
            status, body = await request('DELETE', '/api/v1/documents/1')

        self.assertEqual(status, 204)
        self.assertEqual(body, b'')
        delete.assert_awaited_once()

    async def test_delete_endpoint_returns_not_found(self):
        with patch(
            'app.api.v1.documents.delete_document',
            new=AsyncMock(side_effect=DocumentNotFoundError),
        ):
            status, body = await request('DELETE', '/api/v1/documents/404')

        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body)['detail'], 'Документ не найден')
