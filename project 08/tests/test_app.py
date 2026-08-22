import pytest
from src.app import App, HealthCheck


def test_app_initialization():
    app = App("test-app")
    assert app.name == "test-app"
    assert app.version == "1.0.0"


def test_add_dependency():
    app = App()
    app.add_dependency("requests")
    app.add_dependency("pydantic")
    app.add_dependency("requests")  # duplicate ignored
    check = app.health_check()
    assert len(check.dependencies) == 2
    assert "requests" in check.dependencies
    assert "pydantic" in check.dependencies


def test_health_check():
    app = App("my-app")
    check = app.health_check()
    assert isinstance(check, HealthCheck)
    assert check.status == "healthy"
    assert check.version == "1.0.0"
    assert check.dependencies == []


def test_format_config():
    app = App()
    result = app.format_config({"key": "value", "num": 42})
    assert '"key"' in result
    assert '"value"' in result
    assert "42" in result
