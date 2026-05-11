from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse

from opensearchpy import OpenSearch, helpers

from app.domain.entities.audit_event import AuditEvent
from app.domain.interfaces.log_provider import LogProvider


class OpenSearchLogProvider(LogProvider):
    def __init__(
        self,
        base_url: str,
        source_index: str,
        anomaly_index: str,
        username: str | None = None,
        password: str | None = None,
        timeout_seconds: int = 30,
        verify_ssl: bool = True,
        timestamp_field: str = "requestReceivedTimestamp",
    ) -> None:
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.hostname:
            raise ValueError("`base_url` must include scheme and hostname.")

        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"}:
            raise ValueError("`base_url` scheme must be http or https.")

        host_config: dict[str, Any] = {
            "host": parsed.hostname,
            "port": parsed.port or (443 if scheme == "https" else 80),
            "scheme": scheme,
        }

        client_kwargs: dict[str, Any] = {
            "hosts": [host_config],
            "use_ssl": scheme == "https",
            "verify_certs": verify_ssl,
            "ssl_show_warn": False,
            "timeout": timeout_seconds,
        }
        if username:
            client_kwargs["http_auth"] = (username, password or "")

        self.client = OpenSearch(**client_kwargs)
        self.source_index = source_index
        self.anomaly_index = anomaly_index
        self._timestamp_field = timestamp_field

    def fetch_audit_events(
        self,
        start_ts: Optional[datetime] = None,
        end_ts: Optional[datetime] = None,
        size: Optional[int] = None,
    ) -> list[AuditEvent]:
        ts_field = self._timestamp_field
        filters: list[dict[str, Any]] = []
        if start_ts is not None or end_ts is not None:
            range_clause: dict[str, Any] = {"range": {ts_field: {}}}
            if start_ts is not None:
                range_clause["range"][ts_field]["gte"] = start_ts.isoformat()
            if end_ts is not None:
                range_clause["range"][ts_field]["lte"] = end_ts.isoformat()
            filters.append(range_clause)

        body: dict[str, Any] = {
            "sort": [{ts_field: {"order": "asc"}}],
            "query": {"bool": {"filter": filters}},
        }
        if size is not None:
            body["size"] = size

        response = self.client.search(index=self.source_index, body=body)
        hits = response.get("hits", {}).get("hits", [])
        events: list[AuditEvent] = []
        for hit in hits:
            source = hit.get("_source", {})
            event = self._map_source_to_event(source, self._timestamp_field)
            if event is not None:
                events.append(event)
        return events

    def save_anomalies(self, documents: list[dict[str, Any]]) -> None:
        if not documents:
            return

        actions = [
            {
                "_index": self.anomaly_index,
                "_source": self._serialize_value(document),
            }
            for document in documents
        ]
        helpers.bulk(self.client, actions)

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {
                str(key): OpenSearchLogProvider._serialize_value(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [OpenSearchLogProvider._serialize_value(item) for item in value]
        return value

    @staticmethod
    def _parse_timestamp(
        source: dict[str, Any],
        primary_field: str,
    ) -> datetime | None:
        for key in (
            primary_field,
            "@timestamp",
            "timestamp",
            "requestReceivedTimestamp",
        ):
            if key in source and source[key] is not None:
                value = source[key]
                try:
                    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                except ValueError:
                    continue
        return None

    @staticmethod
    def _read_nested(source: dict[str, Any], path: list[str], default: Any = None) -> Any:
        value: Any = source
        for key in path:
            if not isinstance(value, dict):
                return default
            value = value.get(key)
            if value is None:
                return default
        return value

    @classmethod
    def _map_source_to_event(
        cls,
        source: dict[str, Any],
        timestamp_field: str,
    ) -> AuditEvent | None:
        timestamp = cls._parse_timestamp(source, timestamp_field)
        if timestamp is None:
            return None

        user = cls._read_nested(source, ["user", "username"], "unknown")
        source_ips = source.get("sourceIPs", [])
        if not isinstance(source_ips, list):
            source_ips = [str(source_ips)]

        return AuditEvent(
            timestamp=timestamp,
            verb=str(source.get("verb") or "unknown"),
            user_username=str(user or "unknown"),
            user_agent=str(source.get("userAgent") or "unknown"),
            object_resource=str(
                cls._read_nested(source, ["objectRef", "resource"], "unknown")
            ),
            object_subresource=cls._read_nested(
                source, ["objectRef", "subresource"]),
            object_namespace=cls._read_nested(
                source, ["objectRef", "namespace"]),
            response_code=cls._read_nested(source, ["responseStatus", "code"]),
            source_ips=[str(item) for item in source_ips],
        )
