from pathlib import Path
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import toml


class MailAccountSettings(BaseSettings):
    """Single mail account credentials."""
    # Support typo 'adress' from TOML via validation alias
    address: str = Field(..., validation_alias="adress", description="Email address")
    password: str = Field(..., description="Email password")


class MailSettings(BaseSettings):
    """Mail server settings and accounts with per-address passwords."""
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    # Nested TOML tables expected under [mail.accounts.<key>]
    accounts: dict[str, MailAccountSettings] = Field(
        default_factory=dict,
        description="Map of account key -> credentials",
    )
    # Backwards-compat for existing config: [mail.schreiber]
    schreiber: Optional[MailAccountSettings] = None


class SchedulerSettings(BaseSettings):
    """Work schedule for sending emails."""
    # 0=Mon ... 6=Sun
    workdays: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4])
    start_hour: int = Field(9, description="Start hour in 24h format")
    end_hour: int = Field(17, description="End hour in 24h format (exclusive)")


class Settings(BaseSettings):
    """Main application settings loaded from TOML configuration."""
    mail: MailSettings
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    @classmethod
    def from_toml(cls, toml_path: str | Path = "config.toml") -> "Settings":
        """Load settings from a TOML file."""
        toml_path = Path(toml_path)
        
        if not toml_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {toml_path}")
        
        with open(toml_path, "r", encoding="utf-8") as f:
            config_data = toml.load(f)

        # Normalize legacy mail.* subtables into mail.accounts
        mail_cfg = config_data.get("mail")
        if isinstance(mail_cfg, dict):
            # Start with any existing accounts mapping
            accounts = dict(mail_cfg.get("accounts") or {})
            # Keys that belong to MailSettings itself
            reserved_keys = {"imap_host", "imap_port", "smtp_host", "smtp_port", "accounts"}
            # Any other dict-valued subtables under [mail.*] are account entries
            for key in list(mail_cfg.keys()):
                if key in reserved_keys:
                    continue
                value = mail_cfg.get(key)
                if isinstance(value, dict):
                    accounts[key] = mail_cfg.pop(key)
            if accounts:
                mail_cfg["accounts"] = accounts
        
        # Convert TOML data to Pydantic model
        return cls(**config_data)


# Global settings instance
def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings.from_toml()


# Convenience function for getting genai settings
def get_mail_settings() -> MailSettings:
    """Get mail settings from the global configuration."""
    return get_settings().mail


# Timezone utilities
BERLIN_TZ = ZoneInfo("Europe/Berlin")


def now_berlin() -> datetime:
    """Return current timezone-aware datetime in Europe/Berlin."""
    return datetime.now(BERLIN_TZ)


if __name__ == "__main__":
    print(get_mail_settings())