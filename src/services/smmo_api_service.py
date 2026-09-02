import asyncio
import os

import aiohttp

from dotenv import load_dotenv
from typing import Any

from src.shared.app_error import AppError

load_dotenv()

class SMMOAPIService:
    # CONSTANTS
    _COMPONENT: str = "SMMO_API_Service"
    _BASE_URL: str = "https://api.simple-mmo.com/v1"
    _API_KEY: str = ""

    # ERRORS
    @classmethod
    def _rate_limit_error(cls) -> AppError:
        return AppError(
            component=cls._COMPONENT,
            type="GENERIC",
            code="001",
            message="Rate limit exceeded. Please wait before making more requests."
        )

    @classmethod
    def _api_call_error(cls, api_error_message: str) -> AppError:
        return AppError(
            component=cls._COMPONENT,
            type="GENERIC",
            code="002",
            message=f"Error occurred while calling the API: {api_error_message}"
        )

    @classmethod
    def _api_status_error(cls, status_code: int) -> AppError:
        return AppError(
            component=cls._COMPONENT,
            type="GENERIC",
            code="003",
            message=f"Unexpected status code received from the API: {status_code}"
        )

    def _api_key_missing_error(self) -> AppError:
        return AppError(
            component=self._COMPONENT,
            type="GENERIC",
            code="004",
            message="API key not found. Please set the SIMPLEMMO_API_KEY environment variable."
        )

    @classmethod
    def _session_not_started_error(cls) -> AppError:
        return AppError(
            component=cls._COMPONENT,
            type="GENERIC",
            code="005",
            message="The API service session has not been started."
        )

    # METHODS
    def __init__(self) -> None:
        api_key: str | None = os.getenv("SIMPLEMMO_API_KEY")
        if api_key is None:
            raise self._api_key_missing_error()

        self._API_KEY = api_key
        self._session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={"Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=10),
            )

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

        self._session = None

    async def call_api(self, endpoint: str) -> dict[str, Any]:
        if self._session is None or self._session.closed:
            raise self._session_not_started_error()

        url: str = f"{self._BASE_URL}/{endpoint.lstrip('/')}"

        try:
            async with self._session.post(
                url,
                params={"api_key": self._API_KEY},
            ) as response:
                if response.status == 429: # Rate limit exceeded
                    raise self._rate_limit_error()

                if response.status != 200:
                    raise self._api_status_error(response.status)

                payload: dict[str, Any] = await response.json()
                rate_limit_remaining: int = int(
                    response.headers.get("X-RateLimit-Remaining", 0)
                )
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise self._api_call_error(str(e))

        return {
            "status": response.status,
            "payload": payload,
            "rate_limit_remaining": rate_limit_remaining
        }