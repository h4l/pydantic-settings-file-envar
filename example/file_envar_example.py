import sys
from typing import Tuple, Type

from pydantic import ValidationError
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pydantic_settings_file_envar import FileSuffixEnvSettingsSource


class ExampleSettings(BaseSettings):
    threshold: int
    launch_code: str

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, FileSuffixEnvSettingsSource(settings_cls))


def main() -> None:
    try:
        settings = ExampleSettings()  # type: ignore[call-arg]
    except ValidationError as e:
        print(f"Unable to load settings: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded settings: {settings}")
