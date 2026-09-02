import weakref
from pathlib import Path

from PySide6.QtCore import QSettings

from probability_calibration_tool.localization import APP_QM_NAME, PREFERENCE_KEY


class Translator:
    def __init__(self, *, load_ok=True, empty=False, locale="zh_CN", sentinel="test", error=None):
        self.load_ok, self.empty, self.locale = load_ok, empty, locale
        self.sentinel, self.error, self.path = sentinel, error, None

    def load(self, path, directory="", delimiters="", suffix=""):
        assert (directory, delimiters, suffix) == ("", "", "")
        self.path = path
        if self.error:
            raise self.error
        return self.load_ok

    def filePath(self):
        return self.path

    def isEmpty(self):
        return self.empty

    def language(self):
        return self.locale

    def translate(self, context, source):
        assert (context, source) == ("Localization", "Language")
        return self.sentinel


class App:
    """No Python ownership of translators, just like Qt's installation contract."""

    def __init__(self, *, fail=None, error=None):
        self.events, self.active = [], {}
        self.fail, self.error = fail, error

    def installTranslator(self, translator):
        name = Path(translator.filePath()).name
        self.events.append(("install", name))
        self.active[id(translator)] = weakref.ref(translator)
        if name == self.fail:
            if self.error:
                raise self.error
            return False
        return True

    def removeTranslator(self, translator):
        self.events.append(("remove", Path(translator.filePath()).name))
        self.active.pop(id(translator), None)
        return True


def dummy_pack(root):
    path = root / "languages" / APP_QM_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"Only used with injected Translator")
    return path


def write_preference(root, raw):
    root.mkdir(parents=True, exist_ok=True)
    settings = QSettings(str(root / "settings.ini"), QSettings.Format.IniFormat)
    settings.setFallbacksEnabled(False)
    settings.setValue(PREFERENCE_KEY, raw)
    settings.sync()
    assert settings.status() == QSettings.Status.NoError


class SettingsPlan:
    """One fresh short-lived object per planned operation; record teardown state."""

    def __init__(self, *plans):
        self.plans, self.records, self.hook = list(plans), [], None

    def __call__(self, path, format):
        assert format == QSettings.Format.IniFormat
        assert Path(path).is_absolute() and Path(path).name == "settings.ini"
        config = self.plans.pop(0)
        record = {"calls": [], "values": dict(config.get("values", {}))}
        self.records.append(record)
        return PlannedSettings(config, record, self)


class PlannedSettings:
    def __init__(self, config, record, plan):
        self.config, self.record, self.plan = config, record, plan
        self._set_failed = False

    def setFallbacksEnabled(self, enabled):
        assert enabled is False
        self.record["calls"].append("fallbacks_off")

    def setAtomicSyncRequired(self, required):
        assert required is True
        self.record["calls"].append("atomic_on")

    def contains(self, key):
        self.record["calls"].append("contains")
        if error := self.config.get("read_error"):
            raise type(error)(*error.args)
        return key in self.record["values"]

    def value(self, key):
        self.record["calls"].append("value")
        if self.plan.hook:
            self.plan.hook()
        return self.record["values"].get(key)

    def status(self):
        self.record["calls"].append("status")
        return self.config.get("status", QSettings.Status.NoError)

    def setValue(self, key, value):
        self.record["calls"].append(("set", value))
        self.record["values"][key] = value
        if self.config.get("set_error") and not self._set_failed:
            self._set_failed = True
            error = self.config["set_error"]
            raise type(error)(*error.args)

    def remove(self, key):
        self.record["calls"].append("remove")
        self.record["values"].pop(key, None)

    def sync(self):
        self.record["calls"].append("sync")
        if error := self.config.get("sync_error"):
            raise type(error)(*error.args)

    def __del__(self):
        self.record["teardown_values"] = dict(self.record["values"])
        self.record["calls"].append("teardown")
