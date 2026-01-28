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
        self.cohere_url = self._ensure_trailing_slash(os.environ.get("COHERE_URL") or None)
        self.openai_url = self._ensure_trailing_slash(os.environ.get("OPENAI_URL") or None)
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
        self.dev_show_incoming_message: bool = (os.environ.get("DEV_SHOW_INCOMING_MESSAGE") or "no").lower() in ['yes', 'true']

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
                openai_url=self.openai_url,
                precheck_api_key=self.precheck_api_key,
                raise_4xx_when_blocked=self.raise_4xx_when_blocked,
                dev_record_time=self.dev_record_time,
                proxy_log_path=self.proxy_log_path,
                dev_cohere_api_key=self.dev_cohere_api_key,
                dev_source_for_jailbreak_embeddings=self.dev_source_for_jailbreak_embeddings,
                dev_cohere_logger_level=self.dev_cohere_logger_level,
                dev_show_sentence_transformers_progress_bar=self.dev_show_sentence_transformers_progress_bar,
                home=self.home,
                huggingface_config_path=self.huggingface_config_path,
                dev_avoid_accurate_citation_quality=self.dev_avoid_accurate_citation_quality,
                dev_show_incoming_message=self.dev_show_incoming_message,
            ).items()
            if value is not None and value != ""
        }

    @staticmethod
    def _ensure_trailing_slash(url: str | None) -> str | None:
        if url is not None:
            return url.rstrip('/') + '/'
        return url
