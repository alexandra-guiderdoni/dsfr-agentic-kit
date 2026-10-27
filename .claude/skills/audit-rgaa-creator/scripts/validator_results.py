"""Distinguer un document instruit d'une réponse inexploitable du validateur."""

from typing import Any


def validator_result(payload: Any) -> dict[str, Any]:
    messages = payload.get("messages") if isinstance(payload, dict) else None
    valid_messages = isinstance(messages, list) and all(
        isinstance(item, dict)
        and item.get("type") in {"error", "info", "non-document-error"}
        and (
            item.get("type") == "non-document-error"
            or isinstance(item.get("message"), str)
            and bool(item["message"].strip())
        )
        for item in messages
    )
    non_document_errors = (
        sum(item.get("type") == "non-document-error" for item in messages)
        if valid_messages
        else 0
    )
    if not valid_messages or non_document_errors:
        return {
            "status": "not_collected",
            "executed": False,
            "reason": "non_document_error"
            if non_document_errors
            else "invalid_validator_response",
            "non_document_error_count": non_document_errors,
            "errors": None,
            "warnings": None,
        }
    return {
        "status": "collected",
        "executed": True,
        "reason": None,
        "non_document_error_count": 0,
        "errors": sum(item.get("type") == "error" for item in messages),
        "warnings": sum(item.get("subType") == "warning" for item in messages),
    }
