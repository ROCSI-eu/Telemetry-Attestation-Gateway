"""EXPERIMENTAL · SYNTHETIC_ONLY · A0_SYNTHETIC · NOT VALIDATION OR PRODUCTION AUTHORIZATION.
Local synthetic terminal uniqueness using the existing Checkpoint mock.
No proof, independent authority, real telemetry, or physical completeness claim.
"""
import hashlib
import hmac

from emission_end_anchor import check_closed
from persistent_unified import canonical
from state_rollback import Checkpoint
from emission_gap import BindingRejected

VERSION = "TAG/QA/EMISSION-END-CONSISTENCY/v1"


class EndConsistency:
    """One verifier-owned private checkpoint per (scope, epoch, first, test key)."""

    def __init__(self, state_dir, *, key, scope, epoch, first, config, initialize=False):
        if (type(key) is not bytes or len(key) != 32
                or type(scope) is not str or not scope
                or type(epoch) is not str or not epoch
                or type(first) is not int or not 1 <= first < 2**64):
            raise BindingRejected("INVALID_END_CONSISTENCY_POLICY")
        self.key, self.scope, self.epoch = key, scope, epoch
        self.first, self.config = first, config
        # Domain-separated context; persist only digests, not test keys or observations.
        self.context = [VERSION, scope, epoch, first, hashlib.sha256(key).hexdigest()]
        self.empty = hashlib.sha256(canonical([self.context, "UNSET"])).hexdigest()
        self.reference = Checkpoint(state_dir)  # Existing bounded, atomic, mode-0600 reference.
        if initialize:
            self.reference.advance(None, self.empty)
        else:
            # A missing or invalid reference fails closed, never implicitly re-enrolls.
            with self.reference._locked():
                self.reference._read()

    def accept(self, records, anchor):
        # Verify supplied records, test-only MAC, epoch and final before any state change.
        check_closed(records, anchor, key=self.key, scope=self.scope,
                     epoch=self.epoch, first=self.first, config=self.config)
        digest = hashlib.sha256(canonical(
            [self.context, anchor["final"], anchor["mac"]])).hexdigest()
        with self.reference._locked():
            retained = self.reference._read()
            if hmac.compare_digest(retained, self.empty):
                self.reference._write(digest)
                return "ACCEPT"
            if hmac.compare_digest(retained, digest):
                return "IDEMPOTENT"
            raise BindingRejected("TERMINAL_CLOSURE_CONFLICT")
