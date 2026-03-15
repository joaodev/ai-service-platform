import json
import logging
from urllib import request
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)


def dispatch_webhook(target_url: str, event_message: dict) -> None:
    data = json.dumps(event_message).encode("utf-8")
    http_request = request.Request(
        target_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=5):
            return
    except (HTTPError, URLError, TimeoutError) as exc:
        logger.warning("Webhook dispatch failed for %s: %s", target_url, exc)


def dispatch_many_webhooks(target_urls: list[str], event_message: dict) -> None:
    for target_url in target_urls:
        dispatch_webhook(target_url=target_url, event_message=event_message)
