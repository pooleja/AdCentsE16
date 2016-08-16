import logging
from bs4 import BeautifulSoup
import urllib

logger = logging.getLogger('werkzeug')


class AdCentsE16:
    """Class responsible for interfacing with main server."""

    def __init__(self, serverBaseUrl):
        """Constructor inputs the host where server is running."""
        self.serverBaseUrl = serverBaseUrl

    def validate_url(self, url, key):
        """
        Validates if the url specified has a meta key named "AdCentsE16-site-verification" with a content of the key.
        """
        response = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(response, "lxml")
        metatag = soup.find('meta', attrs={'name': 'AdCentsE16-site-verification'})

        if not metatag:
            return False

        # Determine if the meta content matches for the AdCentsE16-site-verification meta tag
        return metatag['content'] == key
