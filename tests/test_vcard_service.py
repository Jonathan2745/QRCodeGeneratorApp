import re

from qrgenerator.vcard_service import (
    Address,
    PhoneNumber,
    VCardData,
    build_vcard,
    escape_vcard_text,
    safe_filename,
)


def test_escape_vcard_text_escapes_special_characters() -> None:
    assert escape_vcard_text(" ACME, Inc.; Line 1\nLine 2\\ ") == (
        "ACME\\, Inc.\\; Line 1\\nLine 2\\\\"
    )


def test_safe_filename_replaces_windows_reserved_characters() -> None:
    assert safe_filename(' Jane: "QR" / Contact? ') == "Jane_ _QR_ _ Contact_"


def test_safe_filename_uses_default_for_blank_value() -> None:
    assert safe_filename("   ") == "contact"


def test_build_vcard_includes_contact_fields_and_crlf_line_endings() -> None:
    vcard = build_vcard(
        VCardData(
            first_name="Jane",
            last_name="Doe",
            title="Director",
            organisation="ACME, Inc.",
            email="jane@example.com",
            url="https://example.com",
            primary_phone=PhoneNumber(label="mobile", country_code="+65", number="1234"),
            extra_phones=[
                PhoneNumber(label="work", country_code="+65", number="5678", preferred=True),
                PhoneNumber(label="home"),
            ],
            addresses=[
                Address(
                    label="work",
                    first_line="1 Main St",
                    second_line="Level 2",
                    state="Central",
                    county="Singapore",
                    postal_code="123456",
                    country="SG",
                )
            ],
        )
    )

    assert vcard.startswith("BEGIN:VCARD\r\nVERSION:3.0\r\n")
    assert vcard.endswith("END:VCARD\r\n")
    assert "\n" not in vcard.replace("\r\n", "")
    assert "N:Doe;Jane;;;" in vcard
    assert "FN:Jane Doe" in vcard
    assert "ORG:ACME\\, Inc." in vcard
    assert "TEL;TYPE=mobile,voice,pref:+65 1234" in vcard
    assert "TEL;TYPE=work,voice,pref:+65 5678" in vcard
    assert "ADR;TYPE=work:;;1 Main St Level 2;Singapore;Central;123456;SG" in vcard
    assert re.search(r"REV:\d{4}-\d{2}-\d{2}T", vcard)


def test_build_vcard_uses_unnamed_contact_when_name_is_blank() -> None:
    vcard = build_vcard(VCardData())

    assert "FN:Unnamed Contact" in vcard


def test_build_vcard_includes_multiple_emails_and_urls() -> None:
    vcard = build_vcard(
        VCardData(
            first_name="Jane",
            email="primary@example.com",
            emails=["secondary@example.com"],
            url="https://primary.example.com",
            urls=["https://secondary.example.com"],
            url_type="ACME",
        )
    )

    assert "EMAIL;TYPE=work;PREF:primary@example.com" in vcard
    assert "EMAIL;TYPE=work:secondary@example.com" in vcard
    assert "URL;TYPE=ACME;PREF:https://primary.example.com" in vcard
    assert "URL;TYPE=ACME:https://secondary.example.com" in vcard
