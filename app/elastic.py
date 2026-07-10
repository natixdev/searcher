from elasticsearch import AsyncElasticsearch

from app.settings import settings

elasticsearch_client = AsyncElasticsearch(
    hosts=[
        {
            'host': settings.elasticsearch_host,
            'port': settings.elasticsearch_port,
            'scheme': 'http',
        },
    ],
)
