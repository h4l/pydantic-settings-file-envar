from pathlib import Path
from typing import Tuple, Type

import pytest
from pydantic import AliasChoices, Field, ValidationError
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pydantic_settings_file_envar import (
    FileSuffixEnvSettingsSource,
    MissingFileWarning,
    NoReadPermissionWarning,
    NotAFileWarning,
)


class FileSuffixBaseSettings(BaseSettings):
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


class ExampleSettings(FileSuffixBaseSettings):
    foo_bar: str
    baz: int


def test_loads_value_from_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    foo_bar_path = tmp_path / "1"
    baz_path = tmp_path / "2"
    foo_bar_path.write_text("abc")
    baz_path.write_text("42")
    monkeypatch.setenv("FOO_BAR_FILE", str(foo_bar_path))
    monkeypatch.setenv("BAZ_FILE", str(baz_path))

    settings = ExampleSettings()  # type: ignore[call-arg]

    assert settings.foo_bar == "abc"
    assert settings.baz == 42

    # env_settings is before FileSuffix, so regular envars take priority
    monkeypatch.setenv("BAZ", "9000")

    settings = ExampleSettings()  # type: ignore[call-arg]

    assert settings.foo_bar == "abc"
    assert settings.baz == 9000


def test_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BAZ_FILE", str(tmp_path / "missing"))

    with pytest.warns(
        expected_warning=MissingFileWarning,
        match=r"environment variable baz_file references non-existent file: "
        r"'.*/missing'",
    ):
        with pytest.raises(ValidationError, match=r"baz\n.*Field required"):
            ExampleSettings(foo_bar="a")  # type: ignore[call-arg]


def test_non_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bad_path = tmp_path / "non-file"
    bad_path.mkdir()
    monkeypatch.setenv("BAZ_FILE", str(bad_path))

    with pytest.warns(
        expected_warning=NotAFileWarning,
        match=r"environment variable baz_file references file that is not a "
        r"regular file or symlink: '.*/non-file'",
    ):
        with pytest.raises(ValidationError, match=r"baz\n.*Field required"):
            ExampleSettings(foo_bar="a")  # type: ignore[call-arg]


def test_file_without_read_permission(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bad_path = tmp_path / "file-without-read-perm"
    bad_path.write_text("blah")
    bad_path.chmod(0o000)
    monkeypatch.setenv("BAZ_FILE", str(bad_path))

    with pytest.warns(
        expected_warning=NoReadPermissionWarning,
        match=r"environment variable baz_file references file that we have "
        r"insufficient permissions to read: \[Errno 13\] Permission denied: "
        r"'.*/file-without-read-perm'",
    ):
        with pytest.raises(ValidationError, match=r"baz\n.*Field required"):
            ExampleSettings(foo_bar="a")  # type: ignore[call-arg]


class AliasedSettings(FileSuffixBaseSettings):
    foo: str = Field(validation_alias="foo_bar")
    baz: int = Field(validation_alias=AliasChoices("bazington", "mc_baz"))


@pytest.mark.parametrize("baz_var", ["bazington", "mc_baz"])
def test_loads_value_from_alias_envars(
    baz_var: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    foo_path = tmp_path / "1"
    baz_path = tmp_path / "2"
    foo_path.write_text("frob")
    baz_path.write_text("12")
    monkeypatch.setenv("FOO_BAR_FILE", str(foo_path))
    monkeypatch.setenv(f"{baz_var.upper()}_FILE", str(baz_path))

    settings = AliasedSettings()  # type: ignore[call-arg]

    assert settings.foo == "frob"
    assert settings.baz == 12
