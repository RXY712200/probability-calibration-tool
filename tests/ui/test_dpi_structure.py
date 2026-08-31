import pytest
from PySide6.QtCore import QPoint

from .helpers import calculate, click


@pytest.mark.parametrize("size", [(1100, 800), (1250, 900)])
def test_resizable_layout_character_stability_and_confirmation_access(window, h, qapp, size):
    window.resize(*size)
    qapp.processEvents()
    positions = {
        key: widget.mapTo(window, QPoint(0, 0)) for key, widget in window.characters.buttons.items()
    }
    h.seed_history(19, 1)
    calculate(window, reference=True)
    qapp.processEvents()
    for key, widget in window.characters.buttons.items():
        assert widget.mapTo(window, QPoint(0, 0)) == positions[key]
        assert widget.width() >= widget.minimumSizeHint().width()
        assert widget.height() >= widget.minimumSizeHint().height()
        assert window.rect().contains(widget.mapTo(window, widget.rect().bottomRight()))
    click(window.round.post.result.buttons[True])
    click(window.round.post.include.buttons[True])
    qapp.processEvents()
    for widget in (window.round.post.back, window.round.post.save):
        assert widget.isVisible() and widget.width() > 0 and widget.height() > 0
        assert window.rect().contains(widget.mapTo(window, widget.rect().bottomRight()))
