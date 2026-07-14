import sqlite3

import pytest

from app.audit_ledger import AuditLedger


def test_hash_chain_and_append_only_triggers(tmp_path):
    db_path = tmp_path / "ledger.db"
    ledger = AuditLedger(db_path)
    ledger.append(
        {
            "event_hour": "2026-01-01T00:00:00",
            "case_type": "spc_incident",
            "raw_spc_signal": 1,
            "validation_class": "credible",
            "priority": "moderate",
            "proposed_action": "increase_sampling_and_notify",
            "governance_decision": "permitted_automatic_workflow",
            "authorized_action": "increase_sampling_and_notify",
            "human_review_required": False,
            "context_summary": "synthetic",
            "model_version": "test-model",
            "policy_version": "test-policy",
            "evidence_reference": "test:1",
            "outcome": "test",
        }
    )
    assert ledger.validate_chain() is True

    with pytest.raises(sqlite3.DatabaseError):
        ledger.conn.execute("UPDATE ledger SET priority='high' WHERE ledger_id=1")
    with pytest.raises(sqlite3.DatabaseError):
        ledger.conn.execute("DELETE FROM ledger WHERE ledger_id=1")
    ledger.close()
