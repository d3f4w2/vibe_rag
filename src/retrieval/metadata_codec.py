from __future__ import annotations

import json
from typing import Any

ENCODED_METADATA_KEYS_FIELD = "rag_encoded_json_keys"
LEGACY_ENCODED_METADATA_KEYS_FIELD = "__rag_encoded_json_keys"


def sanitize_metadata_for_chroma(
    metadata: dict[str, Any],
    *,
    field_name: str,
) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    encoded_keys: list[str] = []

    for key, value in metadata.items():
        if not isinstance(key, str):
            raise ValueError(f"{field_name} keys must be strings.")
        if key in {ENCODED_METADATA_KEYS_FIELD, LEGACY_ENCODED_METADATA_KEYS_FIELD}:
            raise ValueError(f"{field_name} cannot contain reserved key {key}.")

        if is_chroma_scalar(value):
            sanitized[key] = value
            continue

        try:
            sanitized[key] = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        except TypeError as exc:
            raise ValueError(
                f"{field_name}.{key} must be JSON-serializable when non-scalar."
            ) from exc
        encoded_keys.append(key)

    if encoded_keys:
        sanitized[ENCODED_METADATA_KEYS_FIELD] = json.dumps(
            encoded_keys,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    return sanitized


def restore_metadata_from_chroma(metadata: dict[str, Any]) -> dict[str, Any]:
    restored = dict(metadata)
    encoded_keys_raw = restored.pop(ENCODED_METADATA_KEYS_FIELD, None)
    if encoded_keys_raw is None:
        encoded_keys_raw = restored.pop(LEGACY_ENCODED_METADATA_KEYS_FIELD, None)
    if not isinstance(encoded_keys_raw, str):
        return restored

    try:
        encoded_keys = json.loads(encoded_keys_raw)
    except json.JSONDecodeError:
        return restored
    if not isinstance(encoded_keys, list):
        return restored

    for key in encoded_keys:
        if not isinstance(key, str):
            continue
        raw_value = restored.get(key)
        if not isinstance(raw_value, str):
            continue
        try:
            restored[key] = json.loads(raw_value)
        except json.JSONDecodeError:
            continue

    return restored


def is_chroma_scalar(value: object) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))
