import ipaddress
from typing import Optional, Tuple

import numpy as np
from sklearn.feature_extraction import FeatureHasher
from sklearn.preprocessing import OneHotEncoder

from app.domain.entities.audit_event import AuditEvent
from app.domain.interfaces.encode_pipeline import EncodePipeline


USER_HASH_DIM_DEFAULT = 64
RESOURCE_HASH_DIM_DEFAULT = 128
VERB_VOCAB_DEFAULT = (
    "get", "list", "create", "update", "patch",
    "delete", "deletecollection", "watch",
    "proxy", "connect", "bind", "approve",
    "escalate", "impersonate", "use", "unknown"
)
WORKING_HOURS_DEFAULT = (9, 18)
USER_AGENT_TYPES_DEFAULT = (
    "kubectl", "helm", "controller", "browser", "curl", "other"
)
SENSITIVE_RESOURCES_DEFAULT = ("secrets", "serviceaccounts", "tokenreviews")

TIME_FEATURE_FLAGS = 5
USER_FLAGS = 3
RESOURCE_FLAGS = 1
NAMESPACE_FLAGS = 3
IP_SOURCES_FLAGS = 3
RESPONSES_FLAGS = 6


class EncodePipelineImpl(EncodePipeline):
    def __init__(
        self,
        user_hash_dim: int = USER_HASH_DIM_DEFAULT,
        resource_hash_dim: int = RESOURCE_HASH_DIM_DEFAULT,
        verb_vocab: Tuple[str] = VERB_VOCAB_DEFAULT,
        working_hours: Tuple[int, int] = WORKING_HOURS_DEFAULT,
        ua_types: Tuple[str] = USER_AGENT_TYPES_DEFAULT,
        sensitive_resources: Tuple[str] = SENSITIVE_RESOURCES_DEFAULT
    ) -> None:
        self.user_hash_dim = user_hash_dim
        self.resource_hash_dim = resource_hash_dim
        self.working_hours = working_hours
        self.verb_vocab = list(verb_vocab)
        self.ua_types = list(ua_types)
        self.sensitive_resources = set(sensitive_resources)

        self.user_hasher: FeatureHasher = FeatureHasher(
            n_features=self.user_hash_dim, input_type='dict', alternate_sign=False)
        self.resource_hasher: FeatureHasher = FeatureHasher(
            n_features=self.resource_hash_dim, input_type='dict', alternate_sign=False)
        self.verb_encoder: OneHotEncoder = OneHotEncoder(
            categories=[self.verb_vocab], handle_unknown='ignore', sparse_output=False)
        self.ua_encoder: OneHotEncoder = OneHotEncoder(
            categories=[self.ua_types], handle_unknown='ignore', sparse_output=False)

        self.is_fit = False

        self.feature_dim = (
            TIME_FEATURE_FLAGS +                            # time
            len(self.verb_vocab) +                          # verb one-hot (16)
            # user (hash + 3 flags)
            self.user_hash_dim + USER_FLAGS +
            len(self.ua_types) +                            # userAgent (6)
            # resource (hash + sensitive)
            self.resource_hash_dim + RESOURCE_FLAGS +
            NAMESPACE_FLAGS +                          # namespace (4)
            IP_SOURCES_FLAGS +                         # ip flags (3)
            RESPONSES_FLAGS                            # response (6)
        )

        self._fit()

    def shape(self) -> int:
        return self.feature_dim

    def _fit(self) -> None:
        verbs_arr = np.array(self.verb_vocab).reshape(-1, 1)
        self.verb_encoder.fit(verbs_arr)

        ua_arr = np.array(self.ua_types).reshape(-1, 1)
        self.ua_encoder.fit(ua_arr)
        self.is_fit = True

    def transform(self, event: AuditEvent) -> None:
        vec = self._event_to_vector(event)
        if vec is None:
            raise RuntimeError("Событие не прошло валидацию")
        event.vec = vec

    def _event_to_vector(self, event: AuditEvent) -> Optional[np.ndarray]:
        self._clean_event(event)

        parts = [
            self._encode_time(event),
            self._encode_verb(event),
            self._encode_user(event),
            self._encode_user_agent(event),
            self._encode_resource(event),
            self._encode_namespace(event),
            self._encode_ip(event),
            self._encode_response(event),
        ]
        return np.concatenate(parts)

    def _norm_str(self, s: Optional[str]) -> str:
        return (s or "unknown").lower().strip()

    def _clean_event(self, event: AuditEvent) -> None:
        event.timestamp = event.timestamp_as_datetime()
        event.verb = self._norm_str(event.verb)
        event.user_username = self._norm_str(event.user_username)
        event.user_agent = self._norm_str(event.user_agent)
        event.object_resource = self._norm_str(event.object_resource)
        event.object_subresource = (
            event.object_subresource or "").lower().strip()
        event.object_namespace = (
            event.object_namespace or "unknown").lower().strip()
        event.response_code = int(
            event.response_code) if event.response_code is not None else 0
        event.source_ips = event.source_ips or []

    def _encode_time(self, event: AuditEvent) -> np.ndarray:
        ts = event.timestamp
        hour = ts.hour
        dow = ts.weekday()
        hour_sin = np.sin(2 * np.pi * hour / 24.0)
        hour_cos = np.cos(2 * np.pi * hour / 24.0)
        dow_sin = np.sin(2 * np.pi * dow / 7.0)
        dow_cos = np.cos(2 * np.pi * dow / 7.0)
        start, end = self.working_hours
        is_work = 1.0 if start <= hour < end else 0.0
        return np.array([hour_sin, hour_cos, dow_sin, dow_cos, is_work], dtype=float)

    def _encode_verb(self, event: AuditEvent) -> np.ndarray:
        v = event.verb
        v_arr = np.array([v]).reshape(-1, 1)
        vec = self.verb_encoder.transform(v_arr)
        return vec.ravel()

    def _encode_user(self, event: AuditEvent) -> np.ndarray:
        username = event.user_username or "unknown"
        hashed = self.user_hasher.transform([{username: 1.0}]).toarray()[0]
        is_sa = 1.0 if "system:serviceaccount" in username else 0.0
        is_system = 1.0 if username.startswith("system:") else 0.0
        is_user = 1.0 if (
            not is_sa and not is_system and username != "unknown") else 0.0
        return np.concatenate([hashed.astype(float), np.array([is_sa, is_user, is_system], dtype=float)])

    def _map_user_agent_type(self, ua: str) -> str:
        ua_low = (ua or "unknown").lower()
        if "kubectl" in ua_low:
            return "kubectl"
        if "helm" in ua_low:
            return "helm"
        if "controller" in ua_low or "controller-manager" in ua_low:
            return "controller"
        if "mozilla" in ua_low or "chrome" in ua_low or "safari" in ua_low or "firefox" in ua_low:
            return "browser"
        if "curl" in ua_low or "wget" in ua_low:
            return "curl"
        return "other"

    def _encode_user_agent(self, event: AuditEvent) -> np.ndarray:
        ua_type = self._map_user_agent_type(event.user_agent)
        ua_arr = np.array([ua_type]).reshape(-1, 1)
        vec = self.ua_encoder.transform(ua_arr)
        return vec.ravel()

    def _encode_resource(self, event: AuditEvent) -> np.ndarray:
        res = event.object_resource or "unknown"
        sub = event.object_subresource or ""
        token = f"{res}/{sub}" if sub else res
        hashed = self.resource_hasher.transform([{token: 1.0}]).toarray()[0]
        sensitive_flag = 1.0 if res in self.sensitive_resources else 0.0
        return np.concatenate([hashed.astype(float), np.array([sensitive_flag], dtype=float)])

    def _encode_namespace(self, event: AuditEvent) -> np.ndarray:
        ns = event.object_namespace
        is_kube_system = 1.0 if ns.startswith(
            "kube-") or ns == "kube-system" else 0.0
        is_prod = 1.0 if "prod" in ns or ns.endswith("-prod") else 0.0
        is_infra = 1.0 if "infra" in ns else 0.0
        return np.array([is_kube_system, is_prod, is_infra], dtype=float)

    def _encode_ip(self, event: AuditEvent) -> np.ndarray:
        ips = event.source_ips
        internal = 0.0
        cluster_internal = 0.0
        external = 0.0
        for ip in ips:
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    internal = 1.0
                else:
                    external = 1.0
                if str(ip).startswith("10.") or str(ip).startswith("192.168.") or str(ip).startswith("172."):
                    cluster_internal = 1.0
            except ValueError:
                print("Invalid IP address skipped: %r", ip)
                continue
        return np.array([internal, cluster_internal, external], dtype=float)

    def _encode_response(self, event: AuditEvent) -> np.ndarray:
        code = int(event.response_code) if event.response_code is not None else 0
        classes = np.zeros(5, dtype=float)
        if 100 <= code < 200:
            classes[0] = 1.0
        elif 200 <= code < 300:
            classes[1] = 1.0
        elif 300 <= code < 400:
            classes[2] = 1.0
        elif 400 <= code < 500:
            classes[3] = 1.0
        elif 500 <= code < 600:
            classes[4] = 1.0
        failure = 1.0 if code >= 400 else 0.0
        return np.concatenate([classes, np.array([failure], dtype=float)])
