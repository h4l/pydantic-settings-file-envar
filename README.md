# pydantic-settings-file-envar

Support for loading [pydantic-settings] from files, using the `_FILE`
environment variable suffix pattern commonly used in container images,
especially official Docker images.

If you have a setting called `foo`, by default `pydantic-settings` will load it
from an environment variable `FOO`. With `pydantic-settings-file-envar`, if an
environment variable `FOO_FILE=/a/b/foo` is set, the secret's value will be
loaded from the file at `/a/b/foo`.

> Note that pydantic-settings
> [has built-in support for loading secrets from files](https://docs.pydantic.dev/latest/usage/pydantic_settings/#use-case-docker-secrets),
> so that may be all you need. It's different from the `_FILE` envar pattern in
> that it expects a specific directory to be specified, which contains
> appropriately-named secret files.

## Install

```Console
$ pip install pydantic-settings-file-envar
```

## Usage

To use `_FILE` envar settings, override the `settings_customise_sources()` class
method of your settings class to include the `FileSuffixEnvSettingsSource` this
package provides:

```Python
from pydantic_settings_file_envar import FileSuffixEnvSettingsSource

# ...

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
        # Adding FileSuffixEnvSettingsSource enables _FILE envars
        return (init_settings, env_settings, FileSuffixEnvSettingsSource(settings_cls))
```

If you place it after the default `env_settings` source, `_FILE` environment
variable will only be used if a regular environment variable is not set. The
[pydantic-settings docs have more details on configuring settings sources](https://docs.pydantic.dev/latest/usage/pydantic_settings/#adding-sources).

## Example program & Docker image

The [./example](./example/) dir contains an example command-line program that
loads settings using regular or `_FILE` envars.

Try it like this:

```Console
$ cd example
$ poetry install --with local
$ poetry shell
$ echo -n secret-from-file > /tmp/secret
$ THRESHOLD=9000 LAUNCH_CODE_FILE=/tmp/secret file-envar-example
Loaded settings: threshold=9000 launch_code='secret-from-file'
```

Or the Docker image:

```Console
$ # build the example image
$ docker buildx bake example
[+] Building 5.2s (12/12) FINISHED                                                                         ...
 => => naming to docker.io/library/file-envar-example

$ echo -n secret-from-file > /tmp/secret
$ docker container run --rm -v /tmp:/secrets -e THRESHOLD=9000 -e LAUNCH_CODE_FILE=/secrets/secret file-envar-example
Loaded settings: threshold=9000 launch_code='secret-from-file'
```

[pydantic-settings]: https://github.com/pydantic/pydantic-settings

## Developing

See [docs/dev.md](docs/dev.md).
