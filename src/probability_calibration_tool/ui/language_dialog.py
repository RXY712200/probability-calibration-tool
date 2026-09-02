"""Settings/startup presentation only; delegates all preference/pack work to Step 3."""

from PySide6.QtCore import QT_TRANSLATE_NOOP, QCoreApplication, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from probability_calibration_tool.localization import (
    FallbackReason,
    Language,
    PreferenceSaveFailure,
    PreferenceState,
    QtTranslationStatus,
)

from .localization import template
from .widgets import button, label

LANGUAGE_NAMES = {Language.EN: "English", Language.ZH_CN: "简体中文"}
PROVENANCE_SOURCES = {
    Language.EN: QT_TRANSLATE_NOOP("Localization", "Built-in"),
    Language.ZH_CN: QT_TRANSLATE_NOOP("Localization", "External language pack"),
}
STARTUP_SOURCES = {
    FallbackReason.NONE: None,
    FallbackReason.PREFERRED_PACK_MISSING: QT_TRANSLATE_NOOP(
        "Localization",
        'The preferred interface language is "简体中文", but its language pack was not found. English will be used for this launch. The preferred language setting will not be changed.',
    ),
    FallbackReason.PREFERRED_PACK_INVALID: QT_TRANSLATE_NOOP(
        "Localization",
        'The "简体中文" language pack could not be loaded. English will be used for this launch. The preferred language setting will not be changed.',
    ),
    FallbackReason.INVALID_PREFERENCE: QT_TRANSLATE_NOOP(
        "Localization",
        "The saved interface language preference is invalid. English will be used for this launch. The settings file will not be changed automatically.",
    ),
    FallbackReason.SETTINGS_READ_ERROR: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference could not be read. English will be used for this launch. The existing settings file will not be modified.",
    ),
    FallbackReason.APP_INSTALL_FAILED: QT_TRANSLATE_NOOP(
        "Localization",
        'The "简体中文" language pack could not be loaded. English will be used for this launch. The preferred language setting will not be changed.',
    ),
    FallbackReason.INITIALIZATION_ERROR: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference could not be read. English will be used for this launch. The existing settings file will not be modified.",
    ),
}
SAVE_FAILURE_SOURCES = {
    PreferenceSaveFailure.PACK_INVALID: QT_TRANSLATE_NOOP(
        "Localization",
        'The "简体中文" language pack could not be verified, so the new interface language setting was not saved. Make sure the language pack still exists and can be loaded.',
    ),
    PreferenceSaveFailure.SETTINGS_ACCESS_ERROR: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference could not be saved. The existing preference remains unchanged.",
    ),
    PreferenceSaveFailure.SETTINGS_FORMAT_ERROR: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference could not be saved. The existing preference remains unchanged.",
    ),
    PreferenceSaveFailure.VERIFY_MISMATCH: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference could not be saved. The existing preference remains unchanged.",
    ),
}
SAVE_SUCCESS_SOURCES = {
    Language.EN: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference was saved. English will take effect the next time the application starts.",
    ),
    Language.ZH_CN: QT_TRANSLATE_NOOP(
        "Localization",
        "The interface language preference was saved. The new interface language will take effect the next time the application starts.",
    ),
}
QT_DEGRADED_SOURCE = QT_TRANSLATE_NOOP(
    "Localization",
    "Simplified Chinese is active, but Qt's standard translations could not be loaded. Some Qt-owned text may remain in English.",
)


def startup_notice(context):
    source = STARTUP_SOURCES[context.startup_notice_kind]
    if source is not None:
        return QCoreApplication.translate("Localization", source)
    if context.qt_translation_status in (
        QtTranslationStatus.UNAVAILABLE,
        QtTranslationStatus.LOAD_FAILED,
    ):
        return QCoreApplication.translate(
            "Localization",
            QT_DEGRADED_SOURCE,
        )
    return None


class LanguageDialog(QDialog):
    saved = Signal(str)

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self._saving = False
        self._saved = False
        self.setWindowTitle(QCoreApplication.translate("Localization", "Language"))
        layout = QVBoxLayout(self)
        preferred = (
            LANGUAGE_NAMES[context.preferred_language]
            if context.preference_state in (PreferenceState.DEFAULT, PreferenceState.SAVED_VALID)
            else QCoreApplication.translate("Localization", "Unavailable")
        )
        self.preferred = label(
            template(
                "Localization",
                QT_TRANSLATE_NOOP("Localization", "Preferred language: %1"),
                preferred,
            )
        )
        self.current = label(
            template(
                "Localization",
                QT_TRANSLATE_NOOP("Localization", "Current language: %1"),
                LANGUAGE_NAMES[context.effective_language],
            )
        )
        layout.addWidget(self.preferred)
        layout.addWidget(self.current)
        layout.addWidget(label(QCoreApplication.translate("Localization", "Available")))
        self.group = QButtonGroup(self)
        self.choices, self.available_rows, self.provenance = {}, {}, {}
        for language in (Language.EN, Language.ZH_CN):
            container = QWidget()
            language_row = QHBoxLayout(container)
            language_row.setContentsMargins(0, 0, 0, 0)
            choice = QRadioButton(LANGUAGE_NAMES[language])
            self.choices[language] = choice
            self.group.addButton(choice)
            choice.toggled.connect(self._selection_changed)
            provenance = label(
                QCoreApplication.translate(
                    "Localization",
                    PROVENANCE_SOURCES[language],
                )
            )
            self.provenance[language] = provenance
            self.available_rows[language] = container
            language_row.addWidget(choice)
            language_row.addWidget(provenance)
            language_row.addStretch()
            layout.addWidget(container)
        self.message = label()
        layout.addWidget(self.message)
        row = QHBoxLayout()
        self.cancel = button(QCoreApplication.translate("Localization", "Cancel"))
        self.confirm = button(QCoreApplication.translate("Localization", "Confirm"))
        row.addWidget(self.cancel)
        row.addWidget(self.confirm)
        layout.addLayout(row)
        self.cancel.clicked.connect(self.reject)
        self.confirm.clicked.connect(self._confirm)
        self._refresh_available()
        if (
            context.preference_state in (PreferenceState.DEFAULT, PreferenceState.SAVED_VALID)
            and context.preferred_language in context.available_languages
        ):
            self.choices[context.preferred_language].setChecked(True)
        self._selection_changed()

    def _refresh_available(self):
        self.group.setExclusive(False)
        for language, choice in self.choices.items():
            available = language in self.context.available_languages
            choice.setEnabled(available)
            self.available_rows[language].setVisible(available)
            if not available:
                choice.setChecked(False)
        self.group.setExclusive(True)
        self._selection_changed()

    def _selection_changed(self):
        selected = self._selected()
        healthy_noop = (
            self.context.preference_state == PreferenceState.SAVED_VALID
            and selected == self.context.preferred_language
        )
        self.confirm.setEnabled(
            not self._saving and not self._saved and selected is not None and not healthy_noop
        )

    def _selected(self):
        return next(
            (
                language
                for language, choice in self.choices.items()
                if choice.isEnabled() and choice.isChecked()
            ),
            None,
        )

    def _confirm(self):
        selected = self._selected()
        if (
            self._saving
            or self._saved
            or selected is None
            or (
                self.context.preference_state == PreferenceState.SAVED_VALID
                and selected == self.context.preferred_language
            )
        ):
            return
        self._saving = True
        self._selection_changed()
        try:
            result = self.context.save_preference(selected)
            if not result.success:
                self.message.setText(
                    QCoreApplication.translate("Localization", SAVE_FAILURE_SOURCES[result.failure])
                )
                self._refresh_available()
                return
            message = QCoreApplication.translate("Localization", SAVE_SUCCESS_SOURCES[selected])
            self._saved = True
            self.accept()
            self.saved.emit(message)
        finally:
            self._saving = False
            self._selection_changed()
