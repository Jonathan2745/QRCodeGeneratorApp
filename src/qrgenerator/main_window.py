from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from qrgenerator.config import APP_NAME, DEFAULT_OUTPUT_DIR
from qrgenerator.qr_service import generate_qr_code
from qrgenerator.vcard_service import Address, PhoneNumber, VCardData, build_vcard


class MainWindow(QMainWindow):
    """
    Main application window for generating QR codes from user-entered content.
    """

    def __init__(
        self,
        default_output_path: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.current_preview_path: Path | None = None

        output_path = default_output_path or DEFAULT_OUTPUT_DIR / "qr_code.png"

        self.setWindowTitle(APP_NAME)
        self.resize(960, 720)

        self.input_tabs = QTabWidget()
        self.input_tabs.setObjectName("inputTabs")

        self.text_tab = QWidget()
        self.contact_tab = QWidget()

        self._setup_text_tab()
        self._setup_contact_tab()

        self.input_tabs.addTab(self.text_tab, "Text")
        self.input_tabs.addTab(self.contact_tab, "Contact")
        self.input_tabs.setCurrentWidget(self.contact_tab)

        self.output_path_edit = QLineEdit(str(output_path))
        self.output_path_edit.setObjectName("outputPathEdit")

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("browseButton")

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_path_edit, 1)
        output_layout.addWidget(self.browse_button)

        form_layout = QFormLayout()
        form_layout.addRow("Save as", output_layout)

        self.preview_label = QLabel("No QR code generated")
        self.preview_label.setObjectName("previewLabel")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(260, 260)
        self.preview_label.setStyleSheet(
            "QLabel { border: 1px solid #c8c8c8; background: #fafafa; color: #555; }"
        )

        self.generate_button = QPushButton("Generate QR Code")
        self.generate_button.setObjectName("generateButton")

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.input_tabs)
        layout.addLayout(form_layout)
        layout.addWidget(self.preview_label, 1)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.output_path_edit.textChanged.connect(self._sync_generate_button)
        self.input_tabs.currentChanged.connect(self._sync_generate_button)
        self.browse_button.clicked.connect(self.choose_output_path)
        self.generate_button.clicked.connect(self.generate_qr)

        self._sync_generate_button()

    def _setup_text_tab(self) -> None:
        self.content_editor = QPlainTextEdit()
        self.content_editor.setObjectName("contentEditor")
        self.content_editor.setPlaceholderText("Enter text, URL, or contact details")
        self.content_editor.setMinimumHeight(140)
        self.content_editor.textChanged.connect(self._sync_generate_button)

        layout = QVBoxLayout()
        layout.addWidget(self.content_editor)
        self.text_tab.setLayout(layout)

    def _setup_contact_tab(self) -> None:
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setObjectName("firstNameEdit")

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setObjectName("lastNameEdit")

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("titleEdit")

        self.organisation_edit = QLineEdit()
        self.organisation_edit.setObjectName("organisationEdit")

        details_form = QFormLayout()
        details_form.addRow("First name", self.first_name_edit)
        details_form.addRow("Last name", self.last_name_edit)
        details_form.addRow("Title", self.title_edit)
        details_form.addRow("Organisation", self.organisation_edit)

        self.phone_count_spin = self._create_count_spin_box("numberOfContactNumberSpin", 1)
        self.email_count_spin = self._create_count_spin_box("numberOfEmailSpin", 1)
        self.url_count_spin = self._create_count_spin_box("numberOfUrlSpin", 1)
        self.address_count_spin = self._create_count_spin_box("numberOfAddressSpin", 1)

        self.phone_fields_layout = QVBoxLayout()
        self.email_fields_layout = QVBoxLayout()
        self.url_fields_layout = QVBoxLayout()
        self.address_fields_layout = QVBoxLayout()
        self.address_fields_layout.setSpacing(12)

        details_group = self._create_section("Identity", details_form)
        phone_group = self._create_repeating_section(
            "Phone numbers",
            "Number of contact numbers",
            self.phone_count_spin,
            self.phone_fields_layout,
        )
        email_group = self._create_repeating_section(
            "Emails",
            "Number of emails",
            self.email_count_spin,
            self.email_fields_layout,
        )
        url_group = self._create_repeating_section(
            "URLs",
            "Number of URLs",
            self.url_count_spin,
            self.url_fields_layout,
        )
        address_group = self._create_repeating_section(
            "Addresses",
            "Number of addresses",
            self.address_count_spin,
            self.address_fields_layout,
        )

        for field in [
            self.first_name_edit,
            self.last_name_edit,
            self.title_edit,
            self.organisation_edit,
        ]:
            field.textChanged.connect(self._sync_generate_button)

        self.phone_fields: list[tuple[QLineEdit, QLineEdit]] = []
        self.email_fields: list[QLineEdit] = []
        self.url_fields: list[tuple[QLineEdit, QLineEdit]] = []
        self.address_fields: list[dict[str, QLineEdit | QCheckBox]] = []

        self.phone_count_spin.valueChanged.connect(self._rebuild_phone_fields)
        self.email_count_spin.valueChanged.connect(self._rebuild_email_fields)
        self.url_count_spin.valueChanged.connect(self._rebuild_url_fields)
        self.address_count_spin.valueChanged.connect(self._rebuild_address_fields)

        self._rebuild_phone_fields()
        self._rebuild_email_fields()
        self._rebuild_url_fields()
        self._rebuild_address_fields()

        contact_layout = QVBoxLayout()
        contact_layout.setSpacing(14)
        contact_layout.addWidget(details_group)
        contact_layout.addWidget(phone_group)
        contact_layout.addWidget(email_group)
        contact_layout.addWidget(url_group)
        contact_layout.addWidget(address_group)
        contact_layout.addStretch(1)

        contact_content = QWidget()
        contact_content.setLayout(contact_layout)

        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(420)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(contact_content)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        self.contact_tab.setLayout(layout)

    def _create_section(self, title: str, layout: QFormLayout | QVBoxLayout) -> QGroupBox:
        group = QGroupBox(title)
        group.setLayout(layout)
        return group

    def _create_repeating_section(
        self,
        title: str,
        count_label: str,
        count_spin: QSpinBox,
        fields_layout: QVBoxLayout,
    ) -> QGroupBox:
        count_layout = QFormLayout()
        count_layout.addRow(count_label, count_spin)

        section_layout = QVBoxLayout()
        section_layout.setSpacing(10)
        section_layout.addLayout(count_layout)
        section_layout.addLayout(fields_layout)

        return self._create_section(title, section_layout)

    def _create_count_spin_box(self, object_name: str, value: int) -> QSpinBox:
        spin_box = QSpinBox()
        spin_box.setObjectName(object_name)
        spin_box.setRange(0, 10)
        spin_box.setValue(value)
        return spin_box

    def choose_output_path(self) -> None:
        selected_path, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save QR code",
            self.output_path_edit.text(),
            "PNG Images (*.png);;All Files (*)",
        )

        if selected_path:
            if not selected_path.lower().endswith(".png"):
                selected_path = f"{selected_path}.png"
            self.output_path_edit.setText(selected_path)

    def generate_qr(self) -> None:
        data = self._build_qr_payload()
        output_path_text = self.output_path_edit.text().strip()

        if not data.strip():
            if self._is_contact_mode():
                self.status_label.setText("Enter contact details before generating a QR code.")
            else:
                self.status_label.setText("Enter content before generating a QR code.")
            return

        if not output_path_text:
            self.status_label.setText("Choose where to save the QR code.")
            return

        output_path = Path(output_path_text).expanduser()

        try:
            saved_path = generate_qr_code(data, output_path)
        except Exception as exc:
            self.status_label.setText(f"Could not generate QR code: {exc}")
            return

        self.current_preview_path = saved_path
        self._update_preview()
        self.status_label.setText(f"Saved QR code to {saved_path}")

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._update_preview()

    def _sync_generate_button(self) -> None:
        if not hasattr(self, "generate_button"):
            return

        has_content = (
            self._has_contact_payload() if self._is_contact_mode() else self._has_text_payload()
        )
        has_output_path = bool(self.output_path_edit.text().strip())
        self.generate_button.setEnabled(has_content and has_output_path)

    def _is_contact_mode(self) -> bool:
        return self.input_tabs.currentWidget() is self.contact_tab

    def _has_text_payload(self) -> bool:
        return bool(self.content_editor.toPlainText().strip())

    def _has_contact_payload(self) -> bool:
        return any(
            [
                self.first_name_edit.text().strip(),
                self.last_name_edit.text().strip(),
                self.title_edit.text().strip(),
                self.organisation_edit.text().strip(),
                *(number_edit.text().strip() for _type_edit, number_edit in self.phone_fields),
                *(email_edit.text().strip() for email_edit in self.email_fields),
                *(url_edit.text().strip() for _type_edit, url_edit in self.url_fields),
                *(
                    field.text().strip()
                    for address in self.address_fields
                    for key, field in address.items()
                    if key != "include_county" and isinstance(field, QLineEdit)
                ),
            ]
        )

    def _build_qr_payload(self) -> str:
        if self._is_contact_mode():
            return self._build_vcard_payload()

        return self.content_editor.toPlainText()

    def _build_vcard_payload(self) -> str:
        phone_numbers = [
            PhoneNumber(
                label=phone_type_edit.text().strip() or "work",
                number=number_edit.text().strip(),
                preferred=index == 0,
            )
            for index, (phone_type_edit, number_edit) in enumerate(self.phone_fields)
            if number_edit.text().strip()
        ]

        emails = [
            email_edit.text().strip()
            for email_edit in self.email_fields
            if email_edit.text().strip()
        ]
        urls = [
            url_edit.text().strip()
            for _type_edit, url_edit in self.url_fields
            if url_edit.text().strip()
        ]
        fallback_url_type = self.organisation_edit.text().strip() or "work"
        url_types = [
            type_edit.text().strip() or fallback_url_type
            for type_edit, url_edit in self.url_fields
            if url_edit.text().strip()
        ]

        addresses = []
        for address in self.address_fields:
            include_county = address["include_county"]
            county = (
                address["county"].text().strip()
                if isinstance(include_county, QCheckBox) and include_county.isChecked()
                else ""
            )

            addresses.append(
                Address(
                    first_line=address["line_1"].text().strip(),
                    second_line=address["line_2"].text().strip(),
                    country=address["country"].text().strip(),
                    state=address["state"].text().strip(),
                    county=county,
                    postal_code=address["postal_code"].text().strip(),
                )
            )

        primary_phone = phone_numbers[0] if phone_numbers else PhoneNumber()
        extra_phones = phone_numbers[1:]

        return build_vcard(
            VCardData(
                first_name=self.first_name_edit.text().strip(),
                last_name=self.last_name_edit.text().strip(),
                title=self.title_edit.text().strip(),
                organisation=self.organisation_edit.text().strip(),
                emails=emails,
                urls=urls,
                url_type=fallback_url_type,
                url_types=url_types,
                primary_phone=primary_phone,
                extra_phones=extra_phones,
                addresses=addresses,
            )
        )

    def _rebuild_phone_fields(self) -> None:
        existing_values = [
            (type_edit.text(), number_edit.text()) for type_edit, number_edit in self.phone_fields
        ]
        self._clear_layout(self.phone_fields_layout)
        self.phone_fields = []

        for index in range(self.phone_count_spin.value()):
            phone_type_edit = QLineEdit()
            phone_type_edit.setObjectName(f"phoneTypeEdit_{index + 1}")
            phone_type_edit.setPlaceholderText("mobile, work, home")

            number_edit = QLineEdit()
            number_edit.setObjectName(f"contactNumberEdit_{index + 1}")
            number_edit.setPlaceholderText("+65 1234 5678")

            if index < len(existing_values):
                phone_type_edit.setText(existing_values[index][0])
                number_edit.setText(existing_values[index][1])

            row_layout = QFormLayout()
            row_layout.addRow(f"phone_type_{index + 1}", phone_type_edit)
            row_layout.addRow(f"contact_number_{index + 1}", number_edit)
            self.phone_fields_layout.addLayout(row_layout)
            self.phone_fields.append((phone_type_edit, number_edit))

            phone_type_edit.textChanged.connect(self._sync_generate_button)
            number_edit.textChanged.connect(self._sync_generate_button)

        self._sync_generate_button()

    def _rebuild_email_fields(self) -> None:
        existing_values = [email_edit.text() for email_edit in self.email_fields]
        self._clear_layout(self.email_fields_layout)
        self.email_fields = []

        for index in range(self.email_count_spin.value()):
            email_edit = QLineEdit()
            email_edit.setObjectName(f"emailEdit_{index + 1}")

            if index < len(existing_values):
                email_edit.setText(existing_values[index])

            self.email_fields_layout.addWidget(QLabel(f"email_{index + 1}"))
            self.email_fields_layout.addWidget(email_edit)
            self.email_fields.append(email_edit)
            email_edit.textChanged.connect(self._sync_generate_button)

        self._sync_generate_button()

    def _rebuild_url_fields(self) -> None:
        existing_values = [
            (type_edit.text(), url_edit.text()) for type_edit, url_edit in self.url_fields
        ]
        self._clear_layout(self.url_fields_layout)
        self.url_fields = []

        for index in range(self.url_count_spin.value()):
            url_type_edit = QLineEdit()
            url_type_edit.setObjectName(f"urlTypeEdit_{index + 1}")
            url_type_edit.setPlaceholderText("Defaults to organisation")

            url_edit = QLineEdit()
            url_edit.setObjectName(f"urlEdit_{index + 1}")

            if index < len(existing_values):
                url_type_edit.setText(existing_values[index][0])
                url_edit.setText(existing_values[index][1])

            row_layout = QFormLayout()
            row_layout.addRow(f"url_type_{index + 1}", url_type_edit)
            row_layout.addRow(f"url_{index + 1}", url_edit)
            self.url_fields_layout.addLayout(row_layout)
            self.url_fields.append((url_type_edit, url_edit))
            url_type_edit.textChanged.connect(self._sync_generate_button)
            url_edit.textChanged.connect(self._sync_generate_button)

        self._sync_generate_button()

    def _rebuild_address_fields(self) -> None:
        existing_values = [
            {
                "line_1": address["line_1"].text(),
                "line_2": address["line_2"].text(),
                "country": address["country"].text(),
                "state": address["state"].text(),
                "county": address["county"].text(),
                "postal_code": address["postal_code"].text(),
                "include_county": address["include_county"].isChecked(),
            }
            for address in self.address_fields
        ]
        self._clear_layout(self.address_fields_layout)
        self.address_fields = []

        for index in range(self.address_count_spin.value()):
            fields = {
                "line_1": QLineEdit(),
                "line_2": QLineEdit(),
                "country": QLineEdit(),
                "state": QLineEdit(),
                "county": QLineEdit(),
                "postal_code": QLineEdit(),
                "include_county": QCheckBox("Include county"),
            }

            for key, field in fields.items():
                if isinstance(field, QLineEdit):
                    field.setObjectName(f"address{self._field_object_suffix(key)}Edit_{index + 1}")
                else:
                    field.setObjectName(f"addressIncludeCountyCheck_{index + 1}")

            if index < len(existing_values):
                for key, value in existing_values[index].items():
                    field = fields[key]
                    if isinstance(field, QLineEdit):
                        field.setText(str(value))
                    elif isinstance(field, QCheckBox):
                        field.setChecked(bool(value))

            county_edit = fields["county"]
            include_county_check = fields["include_county"]

            if isinstance(county_edit, QLineEdit) and isinstance(include_county_check, QCheckBox):
                county_edit.setEnabled(include_county_check.isChecked())
                include_county_check.toggled.connect(county_edit.setEnabled)
                include_county_check.toggled.connect(self._sync_generate_button)

            row_layout = QFormLayout()
            row_layout.addRow(f"address_line_1_{index + 1}", fields["line_1"])
            row_layout.addRow(f"address_line_2_{index + 1}", fields["line_2"])
            row_layout.addRow(f"address_Country_{index + 1}", fields["country"])
            row_layout.addRow(f"address_state_{index + 1}", fields["state"])
            row_layout.addRow("", fields["include_county"])
            row_layout.addRow(f"address_county_{index + 1}", fields["county"])
            row_layout.addRow(f"address_postal_code_{index + 1}", fields["postal_code"])

            address_group = QGroupBox(f"Address {index + 1}")
            address_group.setLayout(row_layout)
            self.address_fields_layout.addWidget(address_group)

            for field in fields.values():
                if isinstance(field, QLineEdit):
                    field.textChanged.connect(self._sync_generate_button)

            self.address_fields.append(fields)

        self._sync_generate_button()

    def _field_object_suffix(self, key: str) -> str:
        return "".join(part.capitalize() for part in key.split("_"))

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            widget = item.widget()

            if child_layout is not None:
                self._clear_nested_layout(child_layout)

            if widget is not None:
                widget.deleteLater()

    def _clear_nested_layout(self, layout: QFormLayout | QHBoxLayout | QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            child_layout = item.layout()
            widget = item.widget()

            if child_layout is not None:
                self._clear_nested_layout(child_layout)

            if widget is not None:
                widget.deleteLater()

    def _update_preview(self) -> None:
        if self.current_preview_path is None:
            return

        pixmap = QPixmap(str(self.current_preview_path))

        if pixmap.isNull():
            self.preview_label.setText("Preview unavailable")
            return

        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled_pixmap)
