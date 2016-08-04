import logging

log = logging.getLogger('werkzeug')


class ElasticsearchE16:
    """Class responsible for interfacing with Elasticsearch."""

    def __init__(self, searchHost):
        """Constructor inputs the host where ES is running."""
        self.searchHost = searchHost
