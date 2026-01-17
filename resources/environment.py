from __future__ import annotations
import os
import dotenv
from pathlib import Path

dotenv.load_dotenv()


class Environment:
    """
    Environment configuration for the Guardrails service.
    """
    def __init__(self):
        cohere_url: str | None = os.environ.get("COHERE_URL") or None
        if cohere_url is not None:
            cohere_url = cohere_url.rstrip('/') + '/'
        self.cohere_url = cohere_url
        self.raise_4xx_when_blocked: bool = (os.environ.get("RAISE_4XX_WHEN_BLOCKED") or "yes").lower() in ['yes', 'true']
        self.precheck_api_key: bool = (os.environ.get("PRECHECK_API_KEY") or "no").lower() in ['yes', 'true']
        self.dev_record_time: bool = (os.environ.get("DEV_RECORD_TIME") or "no").lower() in ['yes', 'true']
        self.proxy_log_path: str = os.environ.get("PROXY_LOG_PATH") or "/var/log/llm_proxy/proxy.log"
        self.dev_cohere_api_key: str | None = os.environ.get("DEV_COHERE_API_KEY", None)
        self.dev_source_for_jailbreak_embeddings: str | None = os.environ.get("DEV_SOURCE_FOR_JAILBREAK_EMBEDDINGS", None)
        self.dev_cohere_logger_level: str = str(os.environ.get("DEV_COHERE_LOGGER_LEVEL") or "NOTSET").upper()
        self.dev_show_sentence_transformers_progress_bar: bool = (os.environ.get("DEV_SHOW_SENTENCE_TRANSFORMERS_PROGRESS_BAR") or "yes").lower() in ['yes', 'true']
        home = os.environ.get("HOME")
        self.huggingface_config_path: str | None = os.environ.get("HUGGINGFACE_CONFIG_PATH", None if home is None else Path(home, '.cache/huggingface/config')) or None
        self.dev_avoid_accurate_citation_quality: str = os.environ.get("DEV_AVOID_ACCURATE_CITATION_QUALITY", "no").lower() in ['yes', 'true']

    _instance: Environment | None = None

    @classmethod
    def get_instance(cls) -> Environment:
        if cls._instance is None:
            cls._instance = Environment()
        return cls._instance

    def __dict__(self):
        return {
            key: value
            for key, value in dict(
                cohere_url=self.cohere_url,
                raise_4xx_when_blocked=self.raise_4xx_when_blocked,
                dev_record_time=self.dev_record_time,
                proxy_log_path=self.proxy_log_path,
                dev_cohere_api_key=self.dev_cohere_api_key,
                dev_cohere_logger_level=self.dev_cohere_logger_level,
            ).items()
            if value is not None and value != ""
        }
