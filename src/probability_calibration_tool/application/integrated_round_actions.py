"""Post-commit decorator; accepted RoundService owns every transaction/formula."""


class IntegratedRoundActions:
    def __init__(self, rounds, recent):
        self._rounds, self._recent = rounds, recent

    def calculate(self, *args, **kwargs):
        return self._rounds.calculate(*args, **kwargs)

    def recalculate(self, *args, **kwargs):
        return self._rounds.recalculate(*args, **kwargs)

    def complete_pending(self, *args, **kwargs):
        result = self._rounds.complete_pending(*args, **kwargs)
        self._recent()
        return result

    def void_pending(self, *args, **kwargs):
        result = self._rounds.void_pending(*args, **kwargs)
        self._recent()
        return result
