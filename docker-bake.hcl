group "default" {
    targets = ["test", "lint", "test-example"]
}

target "test" {
    name = "test_python-${replace(py, ".", "-")}_pydantic-settings-${replace(pydantic_settings, ".", "-")}"
    matrix = {
        py = ["3.8", "latest"],
        pydantic_settings = ["2.0.0", "latest"],
    }
    args = {
        PYTHON_VER = py == "latest" ? "slim" : "${py}-slim"
        PYDANTIC_SETTINGS_VER = pydantic_settings == "latest" ? "" : "==${pydantic_settings}"
    }
    target = "test"
    no-cache-filter = ["test"]
}

target "lint" {
    name = "lint-${lint_type}"
    matrix = {
        lint_type = ["flake8", "black", "isort", "mypy"],
    }
    args = {
        PYTHON_VER = "slim"
    }
    target = "lint-${lint_type}"
    no-cache-filter = ["lint-${lint_type}"]
}

target "example" {
    args = {
        PYTHON_VER = "slim"
    }
    target = "example"
    tags = ["file-envar-example"]
}

target "test-example" {
    inherits = ["example"]
    target = "test-example"
    no-cache-filter = ["test-example"]
}
