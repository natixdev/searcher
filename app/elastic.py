from elasticsearch import AsyncElasticsearch

from settings import settings


INDEX_MAPPING = {
    'mappings': {
        'properties': {
            'id': {
                'type': 'integer',
            },
            'text': {
                'type': 'text',
            },
        },
    },
}


elasticsearch_client = AsyncElasticsearch(
    hosts=[
        {
            'host': settings.elasticsearch_host,
            'port': settings.elasticsearch_port,
            'scheme': 'http',
        },
    ],
)


async def create_index() -> None:
    """Создает индекс Elasticsearch, если он отсутствует."""
    if await elasticsearch_client.indices.exists(
        index=settings.elasticsearch_index,
    ):
        return

    await elasticsearch_client.indices.create(
        index=settings.elasticsearch_index,
        body=INDEX_MAPPING,
    )
