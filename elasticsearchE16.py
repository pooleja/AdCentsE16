import logging
from elasticsearch import Elasticsearch

logger = logging.getLogger('werkzeug')


class ElasticsearchE16:
    """Class responsible for interfacing with Elasticsearch."""

    def __init__(self, hosts):
        """Constructor inputs the host where ES is running."""
        self.hosts = hosts
        self.es = Elasticsearch(hosts=hosts)

    def create_index(self, index_name):
        """
        Create an index on the server with the specified name.

        If the index creation fails or it already exists, the call will throw an exception.
        """
        self.es.indices.create(index=index_name)

    def index_exists(self, index_name):
        """
        Check to see whether the index exists in ES.
        """
        self.es.indices.exists(index=index_name, expand_wildcards='none')

    def index_document(self, document, index_name, document_type):
        """
        Index the specified document into the index.
        """
        return self.es.index(index=index_name, doc_type=document_type, body=document)

    def search(self, query, index_name, document_type):
        """
        Index the specified document into the index.
        """
        return self.es.search(index=index_name, doc_type=document_type, body=query)
