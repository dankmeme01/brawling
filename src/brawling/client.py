from typing import Any
from urllib.parse import quote_plus
from dataclasses import dataclass
import logging
import requests
import re

from .models import *
from .exceptions import *

__all__ = [
    "Client",
    "ErrorResponse"
]

BASE_URL = "https://api.brawlstars.com/v1"
PROXY_URL = "https://bsproxy.royaleapi.dev/v1"

@dataclass
class ErrorResponse:
    error: APIException


class Client:
    """Brawl stars API client"""
    def __init__(self, token: str, *, proxy: bool = False, strict_errors: bool = True):
        """Initialize the main client

        Args:
            token (str): Your token, as specified on the developer website
            proxy (bool, optional): Whether to use [a 3rd party proxy](https://docs.royaleapi.com/#/proxy). Defaults to False.
            strict_errors (bool, optional): Whether to raise exceptions if API returned a status code other than 200, or to return them. Will still raise non-API related exceptions. Defaults to True.
        """
        self.__logger = logging.getLogger("brawling")
        self.__ch = logging.StreamHandler()
        self.__ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s"))
        self.__logger.addHandler(self.__ch)
        self._debug(False)
        self._headers = {"Authorization": f"Bearer {token}"}
        self._base = PROXY_URL if proxy else BASE_URL
        self._strict = strict_errors

        self.session = requests.Session()

    def _debug(self, debug: bool):
        """Toggle debug mode

        Args:
            debug (bool): Whether debug should be enabled or disabled
        """

        self.__ch.setLevel(logging.DEBUG if debug else logging.WARN)

    def _url(self, path: str):
        """Concatenate path to base URL

        Args:
            path (str): Pathname
        """

        return self._base + (path if path.startswith("/") else ("/" + path))

    def _get(self, url: str) -> Any or ErrorResponse:
        """Get a JSON response from a URL, returning/throwing an exception if needed.

        Args:
            url (str): the URL

        Raises:
            Exception: If the status code is not 200 but there was no error information (shouldn't ever happen!)
            APIException: If the API returned an error

        Returns:
            Any or ErrorResponse: Either a JSON object (list/dict) or an ErrorResponse if an error has happened and strict mode is disabled.
        """
        if not url.startswith(self._base):
            url = self._base + quote_plus(url, safe='/')
        else:
            url = self._base + quote_plus(url[len(self._base):], safe='/')

        r = self.session.get(url, headers=self._headers)
        self.__logger.info("got url %s, status: %d", url, r.status_code)
        if r.status_code != 200:
            if not r.text:
                raise Exception(f"Got an error and no message, code: {r.status_code}")

            json = r.json()
            exc = generate_exception(r.status_code, json["reason"], json["message"])

            self.__logger.info("generated exception: %s", str(exc))

            return self._exc_wrapper(exc)

        json = r.json()

        return json

    def _verify_tag(self, tag: str):
        regex = re.compile(r"(#)[0289CGJLPOQRUVY]{3,}", re.IGNORECASE | re.MULTILINE)
        match = regex.match(tag)
        if not match:
            return InvalidTag("Invalid tag", "Incorrect tag was provided")

        return match.group().upper()

    def _exc_wrapper(self, exc: Exception):
        if self._strict:
            raise exc
        else:
            return ErrorResponse(exc)

    def get_battle_log(self, tag: str):
        tag = self._verify_tag(tag)
        if isinstance(tag, Exception):
            return self._exc_wrapper(tag)

        res = self._get(f"/players/{tag}/battlelog")
        if isinstance(res, ErrorResponse):
            return res

        battle_list = res["items"]

        return [Battle.from_json(x) for x in battle_list]
