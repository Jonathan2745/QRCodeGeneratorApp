from pathlib import Path

from PySide6.QtCore import Qt

from qrgenerator.main import main
from qrgenerator.main_window import MainWindow


def test_main_entry_point_is_callable() -> None:
    assert callable(main)


def test_main_window_starts_with_generate_disabled(qtbot, tmp_path: Path) -> None:
    output_path = tmp_path / "qr-code.png"
    window = MainWindow(default_output_path=output_path)
    qtbot.addWidget(window)

    assert window.windowTitle()
    assert window.input_tabs.currentWidget() is window.contact_tab
    assert window.output_path_edit.text() == str(output_path)
    assert window.status_label.text() == "Ready"
    assert not window.generate_button.isEnabled()


def test_generate_button_requires_content_and_output_path(qtbot, tmp_path: Path) -> None:
    window = MainWindow(default_output_path=tmp_path / "qr-code.png")
    qtbot.addWidget(window)
    window.input_tabs.setCurrentWidget(window.text_tab)

    window.content_editor.setPlainText("https://example.com")
    assert window.generate_button.isEnabled()

    window.output_path_edit.clear()
    assert not window.generate_button.isEnabled()

    window.output_path_edit.setText(str(tmp_path / "qr-code.png"))
    assert window.generate_button.isEnabled()


def test_generate_qr_from_window_writes_file_and_updates_preview(qtbot, tmp_path: Path) -> None:
    output_path = tmp_path / "qr-code.png"
    window = MainWindow(default_output_path=output_path)
    qtbot.addWidget(window)
    window.input_tabs.setCurrentWidget(window.text_tab)

    window.content_editor.setPlainText("https://example.com")
    qtbot.mouseClick(window.generate_button, Qt.MouseButton.LeftButton)

    assert output_path.exists()
    assert window.current_preview_path == output_path
    assert "Saved QR code to" in window.status_label.text()
    assert window.preview_label.pixmap() is not None
    assert not window.preview_label.pixmap().isNull()


def test_generate_qr_reports_missing_content_when_called_directly(qtbot, tmp_path: Path) -> None:
    window = MainWindow(default_output_path=tmp_path / "qr-code.png")
    qtbot.addWidget(window)
    window.input_tabs.setCurrentWidget(window.text_tab)

    window.generate_qr()

    assert window.status_label.text() == "Enter content before generating a QR code."


def test_contact_tab_builds_vcard_payload_from_repeated_fields(qtbot, tmp_path: Path) -> None:
    window = MainWindow(default_output_path=tmp_path / "contact.png")
    qtbot.addWidget(window)
    window.input_tabs.setCurrentWidget(window.contact_tab)

    window.phone_count_spin.setValue(2)
    window.email_count_spin.setValue(2)
    window.url_count_spin.setValue(2)

    window.first_name_edit.setText("Jane")
    window.last_name_edit.setText("Doe")
    window.title_edit.setText("Director")
    window.organisation_edit.setText("ACME, Inc.")

    window.phone_fields[0][0].setText("mobile")
    window.phone_fields[0][1].setText("+65 1234")
    window.phone_fields[1][0].setText("work")
    window.phone_fields[1][1].setText("+65 5678")

    window.email_fields[0].setText("jane@example.com")
    window.email_fields[1].setText("jane.doe@example.com")

    window.url_fields[0][0].setText("corporate")
    window.url_fields[0][1].setText("https://example.com")
    window.url_fields[1][1].setText("https://work.example.com")

    address = window.address_fields[0]
    address["line_1"].setText("1 Main St")
    address["line_2"].setText("Level 2")
    address["country"].setText("SG")
    address["state"].setText("Central")
    address["include_county"].setChecked(True)
    address["county"].setText("Singapore")
    address["postal_code"].setText("123456")

    payload = window._build_vcard_payload()

    assert "N:Doe;Jane;;;" in payload
    assert "FN:Jane Doe" in payload
    assert "TITLE:Director" in payload
    assert "ORG:ACME\\, Inc." in payload
    assert "TEL;TYPE=mobile,voice,pref:+65 1234" in payload
    assert "TEL;TYPE=work,voice:+65 5678" in payload
    assert "EMAIL;TYPE=work;PREF:jane@example.com" in payload
    assert "EMAIL;TYPE=work:jane.doe@example.com" in payload
    assert "URL;TYPE=corporate;PREF:https://example.com" in payload
    assert "URL;TYPE=ACME\\, Inc.:https://work.example.com" in payload
    assert "ADR;TYPE=work:;;1 Main St Level 2;Singapore;Central;123456;SG" in payload


def test_contact_tab_generates_qr_file(qtbot, tmp_path: Path) -> None:
    output_path = tmp_path / "contact.png"
    window = MainWindow(default_output_path=output_path)
    qtbot.addWidget(window)
    window.input_tabs.setCurrentWidget(window.contact_tab)

    window.first_name_edit.setText("Jane")
    qtbot.mouseClick(window.generate_button, Qt.MouseButton.LeftButton)

    assert output_path.exists()
    assert "Saved QR code to" in window.status_label.text()
