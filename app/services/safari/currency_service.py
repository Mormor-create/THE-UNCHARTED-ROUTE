
"""Daily exchange rates for The Uncharted Route public pricing."""

import json
import logging
import time
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

API_URL = "https://open.er-api.com/v6/latest/USD"
CACHE_SECONDS = 6 * 60 * 60
REQUEST_TIMEOUT = 8

_cache = {
    "rates": None,
    "updated_at": None,
    "expires_at": 0,
}


class CurrencyConversionError(Exception):
    """Raised when a currency conversion cannot be calculated."""


def get_exchange_rates(force_refresh=False):
    """Return USD-based rates, using memory cache and stale data if needed."""
    now = time.time()

    if (
        not force_refresh
        and _cache["rates"]
        and now < _cache["expires_at"]
    ):
        return {
            "rates": _cache["rates"],
            "updated_at": _cache["updated_at"],
            "stale": False,
        }

    try:
        req = Request(
            API_URL,
            headers={"User-Agent": "TheUnchartedRoute/1.0"},
        )

        with urlopen(req, timeout=REQUEST_TIMEOUT) as response:
            payload = json.loads(response.read().decode("utf-8"))

        if payload.get("result") != "success":
            raise CurrencyConversionError(
                "The exchange-rate provider returned an unsuccessful response."
            )

        rates = payload.get("rates", {})
        if not isinstance(rates, dict) or not rates.get("USD"):
            raise CurrencyConversionError(
                "The exchange-rate response did not contain valid rates."
            )

        updated_at = payload.get("time_last_update_utc")

        _cache.update({
            "rates": rates,
            "updated_at": updated_at,
            "expires_at": now + CACHE_SECONDS,
        })

        return {
            "rates": rates,
            "updated_at": updated_at,
            "stale": False,
        }

    except (
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        CurrencyConversionError,
    ):
        logger.warning(
            "Could not refresh TUR exchange rates.",
            exc_info=True,
        )

        # Do not break the property page if the provider is temporarily down.
        if _cache["rates"]:
            return {
                "rates": _cache["rates"],
                "updated_at": _cache["updated_at"],
                "stale": True,
            }

        raise CurrencyConversionError(
            "Exchange rates are temporarily unavailable."
        )


def convert_amount(amount, source_currency, target_currency):
    """Convert without modifying the original supplier amount."""
    from_currency = (source_currency or "").upper()
    to_currency = (target_currency or "").upper()

    if not from_currency or not to_currency:
        raise CurrencyConversionError("A currency code is missing.")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise CurrencyConversionError("The price amount is invalid.")

    if from_currency == to_currency:
        return amount

    data = get_exchange_rates()
    rates = data["rates"]

    source_rate = rates.get(from_currency)
    target_rate = rates.get(to_currency)

    if not source_rate or not target_rate:
        raise CurrencyConversionError(
            f"Conversion from {from_currency} to {to_currency} is unavailable."
        )

    return amount / float(source_rate) * float(target_rate)


def get_conversion_metadata():
    """Return the provider update timestamp and stale-cache status."""
    data = get_exchange_rates()
    return {
        "updated_at": data["updated_at"],
        "stale": data["stale"],
        "provider": "ExchangeRate-API",
        "provider_url": "https://www.exchangerate-api.com/",
    }
