"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Two-epoch local model; no proof, independent authority or trusted time.
"""
import hashlib
from pathlib import Path
from emission_end_consistency import EndConsistency
from emission_gap import BindingRejected
from persistent_unified import canonical
from state_rollback import Checkpoint


class EndFreshness:
    """Fixed verifier-owned directed transition, separate mock reference.
    Pre-enrolled closure checkpoints; no implicit enrollment on restart.
    """
    def __init__(self, root, *, key, scope, first, config, epochs, initialize=False):
        if (type(epochs) is not tuple or len(epochs) != 2
                or any(type(e) is not str or not e for e in epochs)
                or epochs[0] == epochs[1]):
            raise BindingRejected("INVALID_EPOCH_POLICY")
        self.epochs = epochs
        self.root = Path(root)
        self.state = Checkpoint(self.root / "current")
        self.reference = Checkpoint(self.root / "reference")
        self.digests = {e: hashlib.sha256(canonical([
            "TAG/QA/END-FRESHNESS/v1", scope, first,
            hashlib.sha256(key).hexdigest(), list(epochs), e])).hexdigest()
            for e in epochs}
        self.gates = {}
        for i, e in enumerate(epochs):
            self.gates[e] = EndConsistency(self.root / ("closure-" + str(i)),
                key=key, scope=scope, epoch=e, first=first, config=config,
                initialize=initialize)
        if initialize:
            self.reference.advance(None, self.digests[epochs[0]])
            self.state.advance(None, self.digests[epochs[0]])
        with self.state._locked():
            self._current()

    def _current(self):
        digest = self.state._read()
        self.reference.check(digest)
        for epoch, expected in self.digests.items():
            if digest == expected:
                return epoch
        raise BindingRejected("UNKNOWN_CURRENT_EPOCH")

    def transition(self, *, expected, target):
        # Trusted local verifier action only; no source-driven transition.
        with self.state._locked():
            current = self._current()
            if (current != expected or (expected, target) != self.epochs):
                raise BindingRejected("EPOCH_TRANSITION_NOT_AUTHORIZED")
            self.reference.advance(self.digests[current], self.digests[target])
            self.state._write(self.digests[target])

    def accept(self, records, anchor):
        with self.state._locked():
            current = self._current()
            if type(anchor) is dict and anchor.get("epoch") != current:
                raise BindingRejected("TERMINAL_EPOCH_NOT_CURRENT")
            return self.gates[current].accept(records, anchor)
