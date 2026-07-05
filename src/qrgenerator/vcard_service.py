from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone


def escape_vcard_text(value: str) -> str:
    """
    Escape special characters for vCard text fields.
    """
    return (
        value.strip()
        .replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
        .replace("\r", "")
    )


def safe_filename(value: str) -> str:
    """
    Convert a contact name into a safe filename.
    """
    cleaned = value.strip() or "contact"
    cleaned = re.sub(r'[<>:"/\\|?*]', "_", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


@dataclass
class Address:
    label: str = "work"
    first_line: str = ""
    second_line: str = ""
    state: str = ""
    county: str = ""
    postal_code: str = ""
    country: str = ""

    def is_empty(self) -> bool:
        return not any(
            [
                self.first_line.strip(),
                self.second_line.strip(),
                self.state.strip(),
                self.county.strip(),
                self.postal_code.strip(),
                self.country.strip(),
            ]
        )


@dataclass
class PhoneNumber:
    label: str = "work"
    country_code: str = ""
    number: str = ""
    preferred: bool = False

    def formatted_phone(self) -> str:
        return f"{self.country_code.strip()} {self.number.strip()}".strip()

    def is_empty(self) -> bool:
        return not self.formatted_phone()


@dataclass
class VCardData:
    first_name: str = ""
    last_name: str = ""
    title: str = ""
    organisation: str = ""
    email: str = ""
    url: str = ""
    emails: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    url_type: str = "work"
    url_types: list[str] = field(default_factory=list)

    primary_phone: PhoneNumber = field(default_factory=PhoneNumber)
    extra_phones: list[PhoneNumber] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)

    @property
    def full_name(self) -> str:
        return f"{self.first_name.strip()} {self.last_name.strip()}".strip()


def build_vcard(data: VCardData) -> str:
    """
    Build vCard 3.0 text using CRLF line endings.
    """
    full_name = data.full_name or "Unnamed Contact"

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape_vcard_text(data.last_name)};{escape_vcard_text(data.first_name)};;;",
        f"FN:{escape_vcard_text(full_name)}",
    ]

    if data.title.strip():
        lines.append(f"TITLE:{escape_vcard_text(data.title)}")

    if data.organisation.strip():
        lines.append(f"ORG:{escape_vcard_text(data.organisation)}")

    email_values = [data.email, *data.emails]
    email_values = [email for email in email_values if email.strip()]

    for index, email in enumerate(email_values):
        email_type = "work;PREF" if index == 0 else "work"
        lines.append(f"EMAIL;TYPE={email_type}:{escape_vcard_text(email)}")

    if not data.primary_phone.is_empty():
        phone_type = data.primary_phone.label or "work"
        lines.append(
            f"TEL;TYPE={escape_vcard_text(phone_type)},voice,pref:"
            f"{escape_vcard_text(data.primary_phone.formatted_phone())}"
        )

    for phone in data.extra_phones:
        if phone.is_empty():
            continue

        phone_type = phone.label or "work"

        if phone.preferred:
            lines.append(
                f"TEL;TYPE={escape_vcard_text(phone_type)},voice,pref:"
                f"{escape_vcard_text(phone.formatted_phone())}"
            )
        else:
            lines.append(
                f"TEL;TYPE={escape_vcard_text(phone_type)},voice:"
                f"{escape_vcard_text(phone.formatted_phone())}"
            )

    for address in data.addresses:
        if address.is_empty():
            continue

        address_type = address.label or "work"

        street = " ".join(
            part.strip() for part in [address.first_line, address.second_line] if part.strip()
        )

        lines.append(
            f"ADR;TYPE={escape_vcard_text(address_type)}:"
            f";;"
            f"{escape_vcard_text(street)};"
            f"{escape_vcard_text(address.county)};"
            f"{escape_vcard_text(address.state)};"
            f"{escape_vcard_text(address.postal_code)};"
            f"{escape_vcard_text(address.country)}"
        )

    url_values = []

    if data.url.strip():
        url_values.append((data.url, data.url_type))

    for index, url in enumerate(data.urls):
        if not url.strip():
            continue

        url_type = data.url_types[index] if index < len(data.url_types) else data.url_type
        url_values.append((url, url_type))

    for index, (url, url_type) in enumerate(url_values):
        escaped_url_type = escape_vcard_text(url_type or "work")
        type_parameters = f"{escaped_url_type};PREF" if index == 0 else escaped_url_type
        lines.append(f"URL;TYPE={type_parameters}:{escape_vcard_text(url)}")

    revision_time = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    lines.append(f"REV:{revision_time}")
    lines.append("END:VCARD")

    return "\r\n".join(lines) + "\r\n"
