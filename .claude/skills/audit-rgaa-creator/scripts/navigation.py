"""Navigation Playwright bornée par la réponse HTTP réellement observée."""

from __future__ import annotations

from typing import Any


_PROXY_ERROR_MARKERS = (
    "ERR_PROXY_CONNECTION_FAILED",
    "ERR_TUNNEL_CONNECTION_FAILED",
)


def _error_kind(message: str) -> str:
    upper = message.upper()
    if any(marker in upper for marker in _PROXY_ERROR_MARKERS):
        return "BLOQUÉ-INFRA"
    return "INJOIGNABLE"


async def goto_checked(page: Any, url: str, timeout: int) -> Any:
    """Navigue vers une URL et refuse de traiter un refus comme la page cible.

    Un en-tête ``x-deny-reason`` identifie le proxy de sortie. Une réponse
    HTTP en erreur sans cet en-tête est attribuée au site cible et reste une
    erreur de navigation, jamais une preuve RGAA ou DSFR.
    """
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
    except Exception as exc:  # Playwright expose plusieurs classes selon le moteur.
        message = str(exc)
        raise RuntimeError(f"{_error_kind(message)} : navigation impossible vers {url} : {message}") from exc
    if response is None:
        raise RuntimeError(f"INJOIGNABLE : aucune réponse HTTP pour {url}")
    headers = {str(key).lower(): str(value) for key, value in response.headers.items()}
    deny_reason = headers.get("x-deny-reason", "").strip()
    if deny_reason:
        raise RuntimeError(
            f"BLOQUÉ-INFRA : le proxy refuse {url} (x-deny-reason: {deny_reason})"
        )
    if response.status >= 400:
        server = headers.get("server", "").strip()
        suffix = f"; serveur: {server}" if server else ""
        raise RuntimeError(
            f"ERREUR_SITE : réponse HTTP {response.status} pour {url}{suffix}"
        )
    return response
