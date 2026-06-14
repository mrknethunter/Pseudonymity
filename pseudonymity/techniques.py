"""Column-level pseudonymisation techniques."""

from __future__ import annotations

import ipaddress
import re
from datetime import date, datetime, timedelta
from typing import Any

from pseudonymity.crypto import deterministic_int, hmac_token


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def age_on(dob: date, reference_date: date) -> int:
    years = reference_date.year - dob.year
    if (reference_date.month, reference_date.day) < (dob.month, dob.day):
        years -= 1
    return years


def age_band(dob: date, reference_date: date) -> str:
    age = age_on(dob, reference_date)
    if age < 30:
        return "18-29"
    if age < 40:
        return "30-39"
    if age < 50:
        return "40-49"
    if age < 60:
        return "50-59"
    if age < 70:
        return "60-69"
    return "70+"


def birth_decade(dob: date) -> str:
    return f"{(dob.year // 10) * 10}s"


def email_domain(email: str) -> str:
    if "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].lower()


def ip_subnet(ip_value: str, prefix: int = 24) -> str:
    try:
        ip = ipaddress.ip_address(ip_value)
        if ip.version == 4:
            network = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
            return str(network)
    except ValueError:
        pass
    return ""


def postal_area(postal_code: str, digits: int = 3) -> str:
    cleaned = re.sub(r"\D", "", postal_code)
    if len(cleaned) >= digits:
        return cleaned[:digits] + ("*" * max(0, len(cleaned) - digits))
    return ""


def mask_email(value: str) -> str:
    if "@" not in value:
        return ""
    local, domain = value.rsplit("@", 1)
    if not local:
        return f"*@{domain.lower()}"
    return f"{local[:1].lower()}{'*' * max(3, len(local) - 1)}@{domain.lower()}"


def mask_phone(value: str, visible_digits: int = 2) -> str:
    digits = re.sub(r"\D", "", value)
    if not digits:
        return ""
    return "*" * max(0, len(digits) - visible_digits) + digits[-visible_digits:]


def format_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)


def numeric_band(value: str, bands: list[int | float], unit: str = "") -> str:
    number = float(value)
    sorted_bands = sorted(float(item) for item in bands)
    for lower, upper in zip(sorted_bands, sorted_bands[1:]):
        if lower <= number < upper:
            suffix = f" {unit}" if unit else ""
            return f"{format_number(lower)}-{format_number(upper)}{suffix}"
    if number < sorted_bands[0]:
        suffix = f" {unit}" if unit else ""
        return f"<{format_number(sorted_bands[0])}{suffix}"
    suffix = f" {unit}" if unit else ""
    return f">={format_number(sorted_bands[-1])}{suffix}"


def numeric_noise(
    value: str,
    key: bytes,
    namespace: str,
    subject_token: str,
    scale: float,
    decimals: int,
    minimum: float | None = None,
    maximum: float | None = None,
) -> str:
    original = float(value)
    raw = deterministic_int(subject_token, key, namespace, 1_000_001)
    fraction = (raw / 1_000_000.0) - 0.5
    noisy = original + (fraction * 2 * scale)
    if minimum is not None:
        noisy = max(minimum, noisy)
    if maximum is not None:
        noisy = min(maximum, noisy)
    return f"{noisy:.{decimals}f}"


def date_shift(value: str, key: bytes, namespace: str, subject_token: str, max_days: int) -> str:
    parsed = parse_iso_date(value)
    offset = deterministic_int(subject_token, key, namespace, (max_days * 2) + 1) - max_days
    return (parsed + timedelta(days=offset)).isoformat()


def apply_rule(
    row: dict[str, str],
    rule: dict[str, Any],
    key: bytes,
    reference_date: date,
    subject_token: str,
) -> str:
    source = rule["source"]
    value = row.get(source, "")
    technique = rule["technique"]
    namespace = rule.get("namespace", source)

    if technique == "keep":
        return value
    if technique == "redact":
        return str(rule.get("replacement", "REDACTED"))
    if technique == "suppress":
        return ""
    if technique == "hmac_token":
        return hmac_token(value, key, namespace, int(rule.get("length", 18)))
    if technique == "mask_email":
        return mask_email(value)
    if technique == "mask_phone":
        return mask_phone(value, int(rule.get("visible_digits", 2)))
    if technique == "email_domain":
        return email_domain(value)
    if technique == "birth_decade":
        return birth_decade(parse_iso_date(value))
    if technique == "age_band":
        return age_band(parse_iso_date(value), reference_date)
    if technique == "postal_area":
        return postal_area(value, int(rule.get("digits", 3)))
    if technique == "ip_subnet":
        return ip_subnet(value, int(rule.get("prefix", 24)))
    if technique == "date_shift":
        return date_shift(value, key, namespace, subject_token, int(rule.get("max_days", 14)))
    if technique == "date_part":
        parsed = parse_iso_date(value)
        part = rule.get("part")
        if part == "year":
            return str(parsed.year)
        if part == "month":
            return f"{parsed.year:04d}-{parsed.month:02d}"
        raise ValueError(f"Unsupported date part: {part}")
    if technique == "numeric_band":
        return numeric_band(value, rule["bands"], str(rule.get("unit", "")))
    if technique == "numeric_noise":
        minimum = rule.get("min")
        maximum = rule.get("max")
        return numeric_noise(
            value=value,
            key=key,
            namespace=namespace,
            subject_token=subject_token,
            scale=float(rule.get("scale", 1.0)),
            decimals=int(rule.get("decimals", 2)),
            minimum=float(minimum) if minimum is not None else None,
            maximum=float(maximum) if maximum is not None else None,
        )
    if technique == "category_map":
        mapping = rule.get("mapping", {})
        return str(mapping.get(value, rule.get("default", "other")))

    raise ValueError(f"Unsupported technique: {technique}")
