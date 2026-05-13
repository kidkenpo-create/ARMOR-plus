from __future__ import annotations

from urllib.parse import urlparse


ALLOWED_EXACT_HOSTS = {
    "acquisition.gov",
    "www.acquisition.gov",
    "acq.osd.mil",
    "raw.githubusercontent.com",
}

ALLOWED_SUFFIXES = (".gov", ".mil")
APPROVED_GITHUB_PREFIX = "/kidkenpo-create/ARMOR-plus/"


def is_allowed_source_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if host in {"raw.githubusercontent.com"}:
        return parsed.path.startswith(APPROVED_GITHUB_PREFIX)

    if host in ALLOWED_EXACT_HOSTS:
        return True

    return host.endswith(ALLOWED_SUFFIXES)


def reject_unapproved_urls(urls: list[str]) -> list[str]:
    return [url for url in urls if not is_allowed_source_url(url)]

