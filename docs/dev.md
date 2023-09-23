# Developer Info

The Docker bake file contains targets to lint the project and test on a matrix
of supported dependency versions. Run `$ docker buildx bake --print` to see the
targets.

```Console
$ # Run all test and lint targets
$ docker buildx bake

$ # Just tests
$ docker buildx bake test

$ # A specific test matrix target
$ docker buildx bake test_python-3-8_pydantic-settings-2-0-0
```
