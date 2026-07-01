from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Consolidation
    decay_sweep_interval_seconds: int = 900
    consolidation_dry_run: bool = False
    prune_floor: float = 0.0

    # Retrieval
    retrieval_timeout_seconds: float = 5.0
    retrieval_cache_ttl_seconds: int = 30
    reinforce_on_recall: bool = False

    # Storage
    registry_db_path: str = "synapse_registry.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
