"""Process-local translation ownership and explicit, restart-only INI preferences.

No business-layer dependencies. QM files are trusted assets, not a security sandbox.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QLibraryInfo, QSettings, QTranslator

PREFERENCE_KEY = "localization/preferred_language"
APP_QM_NAME = "probability_calibration_tool_zh_CN.qm"
SettingsFactory = Callable[..., QSettings]
TranslatorFactory = Callable[[], QTranslator]


class Language(StrEnum):
    EN = "en"
    ZH_CN = "zh_CN"


class PreferenceState(StrEnum):
    DEFAULT = "default"
    SAVED_VALID = "saved_valid"
    SAVED_INVALID = "saved_invalid"
    READ_ERROR = "read_error"


class FallbackReason(StrEnum):
    NONE = "none"
    PREFERRED_PACK_MISSING = "preferred_pack_missing"
    PREFERRED_PACK_INVALID = "preferred_pack_invalid"
    INVALID_PREFERENCE = "invalid_preference"
    SETTINGS_READ_ERROR = "settings_read_error"
    APP_INSTALL_FAILED = "app_install_failed"
    INITIALIZATION_ERROR = "initialization_error"


class QtTranslationStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    LOADED = "loaded"
    UNAVAILABLE = "unavailable"
    LOAD_FAILED = "load_failed"


class PackPreflightStatus(StrEnum):
    VALID = "valid"
    MISSING = "missing"
    LOAD_FAILED = "load_failed"
    EMPTY_CATALOG = "empty_catalog"
    MISSING_LOCALE_METADATA = "missing_locale_metadata"
    LOCALE_MISMATCH = "locale_mismatch"
    CATALOG_SENTINEL_MISSING = "catalog_sentinel_missing"


class PreferenceSaveFailure(StrEnum):
    NONE = "none"
    PACK_INVALID = "pack_invalid"
    SETTINGS_ACCESS_ERROR = "settings_access_error"
    SETTINGS_FORMAT_ERROR = "settings_format_error"
    VERIFY_MISMATCH = "verify_mismatch"


@dataclass(frozen=True)
class PreferenceReadResult:
    preferred_language: Language
    state: PreferenceState
    key_existed: bool = False
    raw_value: object = None
    status: QSettings.Status = QSettings.Status.NoError


@dataclass(frozen=True)
class PackPreflightResult:
    status: PackPreflightStatus
    path: Path
    translator: QTranslator | None = field(default=None, repr=False)


@dataclass(frozen=True)
class PreferenceSaveResult:
    failure: PreferenceSaveFailure
    restart_required: bool

    @property
    def success(self) -> bool:
        return self.failure == PreferenceSaveFailure.NONE


def _settings(path: Path, factory: SettingsFactory) -> QSettings:
    settings = factory(str(path), QSettings.Format.IniFormat)
    settings.setFallbacksEnabled(False)
    settings.setAtomicSyncRequired(True)
    return settings


def read_preference(
    settings_path: Path, *, settings_factory: SettingsFactory = QSettings
) -> PreferenceReadResult:
    """No setValue/remove/clear/sync: reading must not persist even a default."""
    try:
        settings = _settings(settings_path, settings_factory)
        existed = settings.contains(PREFERENCE_KEY)
        raw = settings.value(PREFERENCE_KEY) if existed else None
        status = settings.status()  # Read first, since INI parsing can be lazy.
    except OSError:
        return PreferenceReadResult(
            Language.EN, PreferenceState.READ_ERROR, status=QSettings.Status.AccessError
        )
    if status != QSettings.Status.NoError:
        return PreferenceReadResult(Language.EN, PreferenceState.READ_ERROR, existed, raw, status)
    if not existed:
        return PreferenceReadResult(Language.EN, PreferenceState.DEFAULT)
    if isinstance(raw, str) and raw in (Language.EN.value, Language.ZH_CN.value):
        return PreferenceReadResult(Language(raw), PreferenceState.SAVED_VALID, True, raw)
    return PreferenceReadResult(Language.EN, PreferenceState.SAVED_INVALID, True, raw)


def _load_exact(translator: QTranslator, path: Path) -> bool:
    # Explicit empty directory/delimiters/suffix disable Qt's default filename
    # fallback (including .qm.qm). Also verify the actual loaded path defensively.
    return translator.load(str(path), "", "", "") and Path(translator.filePath()).absolute() == path


def preflight_app_pack(
    languages_directory: Path, *, translator_factory: TranslatorFactory = QTranslator
) -> PackPreflightResult:
    path = Path(languages_directory).absolute() / APP_QM_NAME
    status = PackPreflightStatus
    try:
        if not path.is_file():
            return PackPreflightResult(status.MISSING, path)
        translator = translator_factory()
        if not _load_exact(translator, path):
            return PackPreflightResult(status.LOAD_FAILED, path)
        if translator.isEmpty():
            return PackPreflightResult(status.EMPTY_CATALOG, path)
        locale = translator.language().strip().replace("-", "_")
        if not locale:
            return PackPreflightResult(status.MISSING_LOCALE_METADATA, path)
        if locale != Language.ZH_CN.value:
            return PackPreflightResult(status.LOCALE_MISMATCH, path)
        if not translator.translate("Localization", "Language"):
            return PackPreflightResult(status.CATALOG_SENTINEL_MISSING, path)
    except OSError:
        return PackPreflightResult(status.LOAD_FAILED, path)
    return PackPreflightResult(status.VALID, path, translator)


def _save_failure(status: QSettings.Status) -> PreferenceSaveFailure:
    return {
        QSettings.Status.NoError: PreferenceSaveFailure.NONE,
        QSettings.Status.AccessError: PreferenceSaveFailure.SETTINGS_ACCESS_ERROR,
        QSettings.Status.FormatError: PreferenceSaveFailure.SETTINGS_FORMAT_ERROR,
    }[status]


def _persist_preference(
    path: Path, selected: Language, factory: SettingsFactory
) -> PreferenceSaveFailure:
    old = read_preference(path, settings_factory=factory)
    if old.status != QSettings.Status.NoError:
        return _save_failure(old.status)
    writer = None
    attempted = verified = False
    try:
        writer = _settings(path, factory)
        attempted = True  # Also restore if setValue mutates and then raises.
        writer.setValue(PREFERENCE_KEY, selected.value)
        writer.sync()
        failure = _save_failure(writer.status())
        if failure != PreferenceSaveFailure.NONE:
            return failure
        check = read_preference(path, settings_factory=factory)  # Fresh second reader.
        if check.status != QSettings.Status.NoError:
            return _save_failure(check.status)
        if not check.key_existed or check.raw_value != selected.value:
            return PreferenceSaveFailure.VERIFY_MISMATCH
        verified = True
        return PreferenceSaveFailure.NONE
    except OSError:
        return PreferenceSaveFailure.SETTINGS_ACCESS_ERROR
    finally:
        if writer is not None and attempted and not verified:
            # Best effort only, NOT an ACID rollback. Prevent a delayed/destructor
            # sync from retaining the rejected new value. Unrelated keys survive.
            try:
                if old.key_existed:
                    writer.setValue(PREFERENCE_KEY, old.raw_value)
                else:
                    writer.remove(PREFERENCE_KEY)
            except Exception:
                logging.getLogger(__name__).exception(
                    "Could not restore the rejected in-memory language preference."
                )


@dataclass(frozen=True)
class _SessionLanguage:
    effective_language: Language
    startup_notice_kind: FallbackReason
    qt_translation_status: QtTranslationStatus
    settings_path: Path
    languages_directory: Path
    app_translator: QTranslator | None = field(default=None, repr=False)
    qt_translator: QTranslator | None = field(default=None, repr=False)


@dataclass
class LocalizationContext:
    """Owns translators for the process UI lifetime, never for a business session."""

    _session: _SessionLanguage
    _preference: PreferenceReadResult
    _available: frozenset[Language]
    _fallback: FallbackReason
    _settings_factory: SettingsFactory = field(default=QSettings, repr=False)
    _translator_factory: TranslatorFactory = field(default=QTranslator, repr=False)

    @property
    def preferred_language(self) -> Language:
        return self._preference.preferred_language

    @property
    def preference_state(self) -> PreferenceState:
        return self._preference.state

    @property
    def effective_language(self) -> Language:
        return self._session.effective_language

    @property
    def available_languages(self) -> frozenset[Language]:
        return self._available

    @property
    def fallback_reason(self) -> FallbackReason:
        return self._fallback

    @property
    def startup_notice_kind(self) -> FallbackReason:
        return self._session.startup_notice_kind

    @property
    def qt_translation_status(self) -> QtTranslationStatus:
        return self._session.qt_translation_status

    @property
    def settings_path(self) -> Path:
        return self._session.settings_path

    @property
    def languages_directory(self) -> Path:
        return self._session.languages_directory

    @property
    def app_translator(self) -> QTranslator | None:
        return self._session.app_translator

    @property
    def qt_translator(self) -> QTranslator | None:
        return self._session.qt_translator

    @property
    def restart_required(self) -> bool:
        return self.preferred_language != self.effective_language

    def save_preference(self, selected: Language) -> PreferenceSaveResult:
        if not isinstance(selected, Language):
            raise TypeError("save_preference requires a supported Language enum member.")
        if selected == Language.ZH_CN:
            if selected not in self._available:
                return PreferenceSaveResult(
                    PreferenceSaveFailure.PACK_INVALID, self.restart_required
                )
            pack = preflight_app_pack(
                self.languages_directory, translator_factory=self._translator_factory
            )
            if pack.status != PackPreflightStatus.VALID:
                self._available = self._available - {selected}  # Demotion only, never promotion.
                return PreferenceSaveResult(
                    PreferenceSaveFailure.PACK_INVALID, self.restart_required
                )
        if (
            self.preference_state == PreferenceState.SAVED_VALID
            and selected == self.preferred_language
        ):
            failure = PreferenceSaveFailure.NONE
        else:
            failure = _persist_preference(self.settings_path, selected, self._settings_factory)
        if failure == PreferenceSaveFailure.NONE:
            self._preference = PreferenceReadResult(
                selected, PreferenceState.SAVED_VALID, True, selected.value
            )
            self._fallback = FallbackReason.NONE
        return PreferenceSaveResult(failure, self.restart_required)


def english_context(root: Path) -> LocalizationContext:
    """I/O-free fallback for an unexpected initialization failure at bootstrap."""
    root = Path(root).absolute()
    reason = FallbackReason.INITIALIZATION_ERROR
    return LocalizationContext(
        _SessionLanguage(
            Language.EN,
            reason,
            QtTranslationStatus.NOT_REQUIRED,
            root / "settings.ini",
            root / "languages",
        ),
        PreferenceReadResult(Language.EN, PreferenceState.READ_ERROR),
        frozenset({Language.EN}),
        reason,
    )


def initialize_localization(
    app: QCoreApplication,
    root: Path,
    *,
    settings_factory: SettingsFactory = QSettings,
    translator_factory: TranslatorFactory = QTranslator,
) -> LocalizationContext:
    root = Path(root).absolute()
    settings_path, directory = root / "settings.ini", root / "languages"
    preference = read_preference(settings_path, settings_factory=settings_factory)
    pack = preflight_app_pack(directory, translator_factory=translator_factory)
    available = frozenset(
        {Language.EN, Language.ZH_CN} if pack.status == PackPreflightStatus.VALID else {Language.EN}
    )
    effective, reason = Language.EN, FallbackReason.NONE
    qt_status = QtTranslationStatus.NOT_REQUIRED
    app_translator = qt_translator = None
    attempted_app = attempted_qt = None
    if preference.state == PreferenceState.READ_ERROR:
        reason = FallbackReason.SETTINGS_READ_ERROR
    elif preference.state == PreferenceState.SAVED_INVALID:
        reason = FallbackReason.INVALID_PREFERENCE
    elif (
        preference.preferred_language == Language.ZH_CN and pack.status != PackPreflightStatus.VALID
    ):
        reason = (
            FallbackReason.PREFERRED_PACK_MISSING
            if pack.status == PackPreflightStatus.MISSING
            else FallbackReason.PREFERRED_PACK_INVALID
        )
    try:
        if (
            preference.preferred_language == Language.ZH_CN
            and pack.status == PackPreflightStatus.VALID
        ):
            qt_status = QtTranslationStatus.UNAVAILABLE
            try:
                qt_path = (
                    Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)).absolute()
                    / "qtbase_zh_CN.qm"
                )
                if qt_path.is_file():
                    qt_status = QtTranslationStatus.LOAD_FAILED
                    candidate = translator_factory()
                    if _load_exact(candidate, qt_path) and not candidate.isEmpty():
                        attempted_qt = candidate
                        if app.installTranslator(candidate):
                            qt_translator, qt_status = candidate, QtTranslationStatus.LOADED
                        else:
                            app.removeTranslator(candidate)
                            attempted_qt = None
            except (OSError, RuntimeError):
                logging.getLogger(__name__).exception(
                    "Qt framework translation failed; application translation remains available."
                )
                if attempted_qt is not None:
                    app.removeTranslator(attempted_qt)
                    attempted_qt = None
                qt_translator = None
                qt_status = QtTranslationStatus.LOAD_FAILED
            attempted_app = pack.translator
            if app.installTranslator(pack.translator):
                effective, app_translator = Language.ZH_CN, pack.translator
            else:
                app.removeTranslator(pack.translator)
                if attempted_qt is not None:
                    app.removeTranslator(attempted_qt)
                attempted_app = attempted_qt = None
                qt_translator, qt_status = None, QtTranslationStatus.NOT_REQUIRED
                reason = FallbackReason.APP_INSTALL_FAILED
                available = frozenset({Language.EN})
        return LocalizationContext(
            _SessionLanguage(
                effective,
                reason,
                qt_status,
                settings_path,
                directory,
                app_translator,
                qt_translator,
            ),
            preference,
            available,
            reason,
            settings_factory,
            translator_factory,
        )
    except BaseException:
        # Even a programming failure must not leave a half-installed language
        # behind when bootstrap's narrow initialization boundary falls back.
        for translator in (attempted_app, attempted_qt):
            if translator is not None:
                app.removeTranslator(translator)
        raise
