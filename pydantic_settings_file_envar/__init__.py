import warnings
from pathlib import Path
from typing import Any, Tuple

from pydantic.fields import FieldInfo
from pydantic_settings import EnvSettingsSource

__all__ = [
    "FileSuffixEnvSettingsSource",
    "UnreadableFileWarning",
    "MissingFileWarning",
    "NotAFileWarning",
    "NoReadPermissionWarning",
]


class UnreadableFileWarning(UserWarning):
    "A _FILE envar referenced a file that could not be read."


class MissingFileWarning(UnreadableFileWarning):
    "A _FILE envar referenced a file that does not exist."


class NotAFileWarning(UnreadableFileWarning):
    "A _FILE envar referenced a file that is not a regular file or symlink."


class NoReadPermissionWarning(UnreadableFileWarning):
    "A _FILE envar referenced a file that we have insufficient permissions to read."


class FileSuffixEnvSettingsSource(EnvSettingsSource):
    """
    A Pydantic settings source that loads values from _FILE envars.

    If EnvSettingsSource would load a setting from envar FOO, this source will
    load it from the file path given by envar FOO_FILE.
    """

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> Tuple[Any, str, bool]:
        """
        Get the value for field from a file given by a _FILE environment variable.

        Args:
            field: The field.
            field_name: The field name.

        Returns:
            A tuple contains the key, value if the file exists otherwise `None`, and
                a flag to determine whether value is complex.
        """

        env_val: str | None = None
        field_key: str | None = None
        value_is_complex: bool | None = None
        for field_key, env_name, value_is_complex in self._extract_field_info(
            field, field_name
        ):
            file_env_name = self._apply_case_sensitive(f"{env_name}_FILE")
            file_env_val = self.env_vars.get(file_env_name)
            if file_env_val is None or file_env_val == "":
                continue
            env_val_path = Path(file_env_val)
            if not env_val_path.exists():
                warnings.warn(
                    f"environment variable {file_env_name} references "
                    f"non-existent file: {str(env_val_path)!r}",
                    category=MissingFileWarning,
                )
                continue
            if env_val_path.is_file():
                try:
                    env_val = env_val_path.read_text()
                except PermissionError as e:
                    warnings.warn(
                        f"environment variable {file_env_name} references file "
                        f"that we have insufficient permissions to read: {e}",
                        category=NoReadPermissionWarning,
                    )
                    continue
                break
            else:
                warnings.warn(
                    f"environment variable {file_env_name} references file "
                    f"that is not a regular file or symlink: {str(env_val_path)!r}",
                    category=NotAFileWarning,
                )
                continue

        if field_key is None or value_is_complex is None:
            return None, "", False
        return env_val, field_key, value_is_complex
