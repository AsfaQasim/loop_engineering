import json

import requests
from pydantic import BaseModel


class HealthCheck(BaseModel):
    status: str
    version: str
    dependencies: list[str]


class App:
    def __init__(self, name: str = "capstone-app"):
        self.name = name
        self.version = "1.0.0"
        self._dependencies: list[str] = []

    def add_dependency(self, dep: str) -> None:
        if dep not in self._dependencies:
            self._dependencies.append(dep)

    def health_check(self) -> HealthCheck:
        return HealthCheck(
            status="healthy",
            version=self.version,
            dependencies=self._dependencies,
        )

    def fetch_remote(self, url: str) -> dict | None:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException:
            return None

    def format_config(self, config: dict) -> str:
        return json.dumps(config, indent=2)
