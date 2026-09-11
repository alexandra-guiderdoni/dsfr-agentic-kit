"""Contrat commun de lancement des navigateurs Playwright de la campagne."""

from __future__ import annotations

import os
import subprocess
import urllib.parse
from collections.abc import Mapping
from pathlib import Path
from typing import Any


class BrowserLaunchConfigError(ValueError):
    """Configuration de lancement navigateur absente ou non gouvernable."""


def _launch_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
    browser = config.get("browser", {})
    if not isinstance(browser, Mapping):
        raise BrowserLaunchConfigError("browser doit être un objet")
    launch = browser.get("launch", {})
    if launch is None:
        return {}
    if not isinstance(launch, Mapping):
        raise BrowserLaunchConfigError("browser.launch doit être un objet")
    return launch


def browser_launch_options(
    config: Mapping[str, Any], environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """Construit les options Playwright sans accepter de secret en YAML."""
    launch = _launch_config(config)
    options: dict[str, Any] = {"headless": bool(launch.get("headless", True))}

    for key in ("args", "channel", "executable_path"):
        if key in launch and launch[key] not in (None, "", []):
            options[key] = launch[key]

    proxy = launch.get("proxy")
    if proxy is None:
        return options
    if not isinstance(proxy, Mapping):
        raise BrowserLaunchConfigError("browser.launch.proxy doit être un objet")
    server = str(proxy.get("server", "")).strip()
    if not server:
        raise BrowserLaunchConfigError("browser.launch.proxy.server est requis")
    parsed = urllib.parse.urlsplit(server)
    if parsed.username or parsed.password:
        raise BrowserLaunchConfigError(
            "browser.launch.proxy.server ne doit pas contenir d’identifiants"
        )
    proxy_options: dict[str, str] = {"server": server}
    if proxy.get("bypass"):
        proxy_options["bypass"] = str(proxy["bypass"])
    if environ is None:
        environ = os.environ
    for config_key, option_key in (
        ("username_env", "username"),
        ("password_env", "password"),
    ):
        env_name = str(proxy.get(config_key, "")).strip()
        if not env_name:
            continue
        value = environ.get(env_name)
        if value is None:
            raise BrowserLaunchConfigError(
                f"variable d’environnement {env_name} absente pour le proxy"
            )
        proxy_options[option_key] = value
    options["proxy"] = proxy_options
    return options


def _redact_proxy_server(server: object) -> object:
    if not isinstance(server, str):
        return server
    try:
        parsed = urllib.parse.urlsplit(server)
        if not (parsed.username or parsed.password):
            return server
        host = parsed.hostname or ""
        if ":" in host:
            host = f"[{host}]"
        port = f":{parsed.port}" if parsed.port else ""
        return urllib.parse.urlunsplit(
            (parsed.scheme, f"{host}{port}", parsed.path, parsed.query, parsed.fragment)
        )
    except ValueError:
        return "<proxy expurgé>"


def browser_launch_summary(
    config: Mapping[str, Any], environ: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """Retourne une trace sans exposer les valeurs secrètes du proxy."""
    launch = _launch_config(config)
    summary: dict[str, Any] = {
        "headless": bool(launch.get("headless", True)),
        "args": list(launch.get("args", [])),
        "channel": launch.get("channel"),
        "executable_path": launch.get("executable_path"),
    }
    proxy = launch.get("proxy")
    if proxy is not None:
        if not isinstance(proxy, Mapping):
            raise BrowserLaunchConfigError("browser.launch.proxy doit être un objet")
        if environ is None:
            environ = os.environ
        summary["proxy"] = {
            "server": _redact_proxy_server(proxy.get("server")),
            "bypass": proxy.get("bypass"),
            "username_env": proxy.get("username_env"),
            "password_env": proxy.get("password_env"),
            "username_present": bool(
                proxy.get("username_env") and environ.get(str(proxy["username_env"]))
            ),
            "password_present": bool(
                proxy.get("password_env") and environ.get(str(proxy["password_env"]))
            ),
        }
    return summary


def check_playwright_python(python: Path) -> tuple[bool, str]:
    """Vérifie l’import réellement utilisé par les contrôles de la campagne."""
    try:
        result = subprocess.run(
            [
                str(python),
                "-c",
                "import playwright.async_api; print(playwright.__file__)",
            ],
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    detail = (result.stdout or result.stderr or "").strip()
    return result.returncode == 0, detail
