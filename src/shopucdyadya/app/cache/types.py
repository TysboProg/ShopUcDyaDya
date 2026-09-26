from typing import Any

type JsonPrimitive = str | int | float | bool | None
type JsonArray = list[Any]
type JsonObject = dict[str, Any]
type JsonValue = JsonPrimitive | JsonArray | JsonObject
