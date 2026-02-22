from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx


class ApiTimeoutError(TimeoutError):
    """Raised when an API call times out after retries."""


class ApiAuthError(PermissionError):
    """Raised when API credentials are missing or rejected."""


class ApiRateLimitError(RuntimeError):
    """Raised when API rate limit is exceeded."""


class ApiResponseError(RuntimeError):
    """Raised when API returns an unexpected response or status."""


_BASE_URL_ALIASES = {
    "https://cloud.siliconflow.cn/v1": "https://api.siliconflow.cn/v1",
}


def load_dotenv_if_present(dotenv_path: str | Path = ".env") -> None:
    path = Path(dotenv_path)
    if not path.exists():
        return

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        value = raw_value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def _require_env_value(name: str, override: str | None) -> str:
    value = override if override is not None else os.getenv(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required and must be a non-empty string.")
    return value.strip()


def _normalize_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    return _BASE_URL_ALIASES.get(normalized, normalized)


def _read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    parsed = int(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer.")
    return parsed


def _read_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    parsed = float(value)
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive number.")
    return parsed


class ApiClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        embedding_model: str | None = None,
        generation_model: str | None = None,
        timeout_sec: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        load_dotenv_if_present()

        raw_base_url = _require_env_value("EMBEDDING_API_BASE_URL", base_url)
        self.base_url = _normalize_base_url(raw_base_url)
        self.api_key = _require_env_value("EMBEDDING_API_KEY", api_key)
        self.embedding_model = _require_env_value("EMBEDDING_MODEL", embedding_model)

        self.generation_model = generation_model or os.getenv("GENERATION_MODEL")
        self.timeout_sec = (
            timeout_sec if timeout_sec is not None else _read_float_env("EMBEDDING_TIMEOUT_SEC", 30.0)
        )
        self.max_retries = (
            max_retries if max_retries is not None else _read_int_env("EMBEDDING_MAX_RETRIES", 3)
        )
        if self.max_retries <= 0:
            raise ValueError("max_retries must be a positive integer.")

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not isinstance(texts, list) or len(texts) == 0:
            raise ValueError("texts must be a non-empty list of strings.")
        for idx, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"texts[{idx}] must be a non-empty string.")

        payload = {
            "model": self.embedding_model,
            "input": texts,
        }
        response_json = self._post_json("/embeddings", payload)
        return self._parse_embedding_response(response_json, expected_count=len(texts))

    def generate_reasoning(self, prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string.")
        if not self.generation_model:
            raise ValueError("GENERATION_MODEL is required for generate_reasoning.")

        payload = {
            "model": self.generation_model,
            "messages": [{"role": "user", "content": prompt}],
        }
        response_json = self._post_json("/chat/completions", payload)
        choices = response_json.get("choices")
        if not isinstance(choices, list) or len(choices) == 0:
            raise ApiResponseError("generation response missing choices.")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ApiResponseError("generation response contains invalid choice object.")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ApiResponseError("generation response missing message.")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ApiResponseError("generation response missing message content.")
        return content

    def _post_json(self, endpoint: str, payload: dict[str, object]) -> dict[str, object]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(1, self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_sec) as client:
                    response = client.post(url, json=payload, headers=headers)
            except httpx.TimeoutException as exc:
                if attempt < self.max_retries:
                    continue
                raise ApiTimeoutError(
                    f"request timed out after {self.max_retries} attempts: {url}"
                ) from exc
            except httpx.HTTPError as exc:
                raise ApiResponseError(f"http request failed: {url}") from exc

            self._raise_for_status(response)
            return self._parse_json_object(response)

        raise ApiTimeoutError(f"request timed out after {self.max_retries} attempts: {url}")

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        status_code = response.status_code
        if status_code in (401, 403):
            raise ApiAuthError(f"authentication failed with status={status_code}.")
        if status_code == 429:
            raise ApiRateLimitError("rate limit exceeded with status=429.")
        if status_code >= 500:
            raise ApiResponseError(f"api server error with status={status_code}.")
        if status_code >= 400:
            raise ApiResponseError(f"api request failed with status={status_code}.")

    @staticmethod
    def _parse_json_object(response: httpx.Response) -> dict[str, object]:
        try:
            parsed = response.json()
        except ValueError as exc:
            raise ApiResponseError("api response body is not valid JSON.") from exc

        if not isinstance(parsed, dict):
            raise ApiResponseError("api response JSON must be an object.")
        return parsed

    @staticmethod
    def _parse_embedding_response(
        response_json: dict[str, object],
        *,
        expected_count: int,
    ) -> list[list[float]]:
        data = response_json.get("data")
        if not isinstance(data, list) or len(data) == 0:
            raise ApiResponseError("embedding response missing data array.")

        embeddings: list[list[float]] = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ApiResponseError(f"embedding response item[{idx}] is invalid.")

            embedding = item.get("embedding")
            if not isinstance(embedding, list) or len(embedding) == 0:
                raise ApiResponseError(
                    f"embedding response item[{idx}] missing embedding vector."
                )

            normalized_vector: list[float] = []
            for dim, value in enumerate(embedding):
                if not isinstance(value, (int, float)):
                    raise ApiResponseError(
                        f"embedding response item[{idx}][{dim}] is not numeric."
                    )
                normalized_vector.append(float(value))

            embeddings.append(normalized_vector)

        if len(embeddings) != expected_count:
            raise ApiResponseError(
                "embedding response count does not match request input count."
            )

        return embeddings
