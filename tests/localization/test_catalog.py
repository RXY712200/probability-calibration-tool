from pathlib import Path

import pytest
from PySide6.QtCore import QTranslator

from probability_calibration_tool.localization import (
    APP_QM_NAME,
    preflight_app_pack,
)
from probability_calibration_tool.localization import (
    PackPreflightStatus as Status,
)

from .helpers import Translator, dummy_pack


@pytest.mark.parametrize(
    "present,config,status",
    [
        (False, {}, Status.MISSING),
        (True, {"load_ok": False}, Status.LOAD_FAILED),
        (True, {"empty": True}, Status.EMPTY_CATALOG),
        (True, {"locale": ""}, Status.MISSING_LOCALE_METADATA),
        (True, {"locale": "zh_TW"}, Status.LOCALE_MISMATCH),
        (True, {"sentinel": ""}, Status.CATALOG_SENTINEL_MISSING),
        (True, {}, Status.VALID),
    ],
)
def test_all_seven_preflight_states(tmp_path, present, config, status):
    if present:
        dummy_pack(tmp_path)
    result = preflight_app_pack(
        tmp_path / "languages", translator_factory=lambda: Translator(**config)
    )
    assert result.status == status
    assert (result.translator is not None) == (status == Status.VALID)
    assert result.path == tmp_path / "languages" / APP_QM_NAME
    assert len(Status) == 7


def test_real_locked_toolchain_ts_qm_qtranslator_smoke(compile_qm, localization_app):
    path = compile_qm(translation="Not hardcoded Chinese")
    translator = QTranslator()
    assert translator.load(str(path))
    assert Path(translator.filePath()) == path
    assert translator.language() == "zh_CN" and not translator.isEmpty()
    assert translator.translate("Localization", "Language") == "Not hardcoded Chinese"
    result = preflight_app_pack(path.parent)
    assert result.status == Status.VALID
    assert result.translator.language() == "zh_CN"
    # Preflight must not install its temporary translator globally.
    assert localization_app.translate("Localization", "Language") == "Language"


@pytest.mark.parametrize(
    "config,expected",
    [
        ({"empty": True}, Status.EMPTY_CATALOG),
        ({"locale": None}, Status.MISSING_LOCALE_METADATA),
        ({"locale": "zh_TW"}, Status.LOCALE_MISMATCH),
        ({"locale": "zh"}, Status.LOCALE_MISMATCH),
        ({"context": "OtherApplication"}, Status.CATALOG_SENTINEL_MISSING),
        ({"source": "Not Language"}, Status.CATALOG_SENTINEL_MISSING),
    ],
)
def test_real_qm_structural_validation(compile_qm, config, expected):
    path = compile_qm(**config)
    assert preflight_app_pack(path.parent).status == expected


@pytest.mark.parametrize(
    "locale,expected",
    [
        (" zh-CN ", Status.VALID),
        ("zh_CN", Status.VALID),
        ("   ", Status.MISSING_LOCALE_METADATA),
        ("zh", Status.LOCALE_MISMATCH),
        ("zh_TW", Status.LOCALE_MISMATCH),
        ("ZH_cn", Status.LOCALE_MISMATCH),
        ("zh_CN.UTF-8", Status.LOCALE_MISMATCH),
    ],
)
def test_locale_normalization_is_deliberately_limited(tmp_path, locale, expected):
    dummy_pack(tmp_path)
    result = preflight_app_pack(
        tmp_path / "languages", translator_factory=lambda: Translator(locale=locale)
    )
    assert result.status == expected


@pytest.mark.parametrize(
    "name",
    [
        "probability_calibration_tool_zh.qm",
        "zh.qm",
        "renamed_zh_CN.qm",
        "probability_calibration_tool_ja_JP.qm",
        "probability_calibration_tool_zh_CN.txt",
        APP_QM_NAME + ".qm",
    ],
)
def test_only_exact_canonical_filename_no_alias_discovery(compile_qm, name):
    path = compile_qm(name=name)
    assert preflight_app_pack(path.parent).status == Status.MISSING


def test_qt_suffix_fallback_cannot_rescue_corrupt_canonical_pack(compile_qm):
    alternative = compile_qm(name=APP_QM_NAME + ".qm")
    canonical = alternative.parent / APP_QM_NAME
    canonical.write_bytes(b"broken canonical QM")
    assert preflight_app_pack(canonical.parent).status == Status.LOAD_FAILED


def test_valid_canonical_pack_is_not_shadowed_by_double_extension(compile_qm):
    canonical = compile_qm(translation="canonical")
    compile_qm(canonical.parent, name=APP_QM_NAME + ".qm", translation="wrong variant")
    result = preflight_app_pack(canonical.parent)
    assert result.status == Status.VALID
    assert result.translator.translate("Localization", "Language") == "canonical"
    assert Path(result.translator.filePath()) == canonical


def test_io_load_error_is_invalid_not_crash(tmp_path):
    dummy_pack(tmp_path)
    result = preflight_app_pack(
        tmp_path / "languages", translator_factory=lambda: Translator(error=OSError("load failed"))
    )
    assert result.status == Status.LOAD_FAILED


def test_validation_stops_at_first_failed_gate(tmp_path):
    dummy_pack(tmp_path)

    class BrokenLoad(Translator):
        def isEmpty(self):
            pytest.fail("Must not inspect a translator after load failure")

    assert (
        preflight_app_pack(
            tmp_path / "languages", translator_factory=lambda: BrokenLoad(load_ok=False)
        ).status
        == Status.LOAD_FAILED
    )


def test_missing_canonical_does_not_even_construct_translator(tmp_path):
    def forbidden():
        pytest.fail("No translator may be constructed for a missing exact path")

    assert preflight_app_pack(tmp_path, translator_factory=forbidden).status == Status.MISSING
