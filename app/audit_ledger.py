from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import sqlite3
from typing import Any

import pandas as pd


class AuditLedger:
    """Tamper-evident SQLite ledger for a research prototype.

    The ledger is append-only within SQLite via UPDATE/DELETE prevention triggers
    and uses a SHA-256 hash chain. It is not a substitute for enterprise WORM
    storage, institutional identity controls, or external audit infrastructure.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.conn = sqlite3.connect(str(database_path))
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ledger (
                ledger_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time TEXT NOT NULL,
                case_type TEXT NOT NULL,
                raw_spc_signal INTEGER,
                validation_class TEXT,
                priority TEXT,
                proposed_action TEXT,
                governance_decision TEXT,
                authorized_action TEXT,
                human_review_required INTEGER,
                context_summary TEXT,
                model_version TEXT,
                policy_version TEXT,
                evidence_reference TEXT,
                outcome TEXT,
                previous_hash TEXT NOT NULL,
                record_hash TEXT NOT NULL UNIQUE,
                payload_json TEXT NOT NULL
            )
            """
        )
        self.conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS ledger_prevent_update
            BEFORE UPDATE ON ledger
            BEGIN
                SELECT RAISE(ABORT, 'ledger is append-only: UPDATE prohibited');
            END;
            """
        )
        self.conn.execute(
            """
            CREATE TRIGGER IF NOT EXISTS ledger_prevent_delete
            BEFORE DELETE ON ledger
            BEGIN
                SELECT RAISE(ABORT, 'ledger is append-only: DELETE prohibited');
            END;
            """
        )
        self.conn.commit()

    @staticmethod
    def _canonical_json(record: dict[str, Any]) -> str:
        return json.dumps(record, sort_keys=True, default=str, separators=(",", ":"))

    def _last_hash(self) -> str:
        row = self.conn.execute("SELECT record_hash FROM ledger ORDER BY ledger_id DESC LIMIT 1").fetchone()
        return str(row[0]) if row else self.GENESIS_HASH

    def append(self, record: dict[str, Any]) -> str:
        payload_json = self._canonical_json(record)
        previous_hash = self._last_hash()
        record_hash = sha256(f"{previous_hash}|{payload_json}".encode("utf-8")).hexdigest()

        self.conn.execute(
            """
            INSERT INTO ledger (
                event_time, case_type, raw_spc_signal, validation_class, priority,
                proposed_action, governance_decision, authorized_action,
                human_review_required, context_summary, model_version, policy_version,
                evidence_reference, outcome, previous_hash, record_hash, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(record.get("event_hour", record.get("event_time", ""))),
                record.get("case_type", "spc_case"),
                int(record.get("raw_spc_signal", 0)),
                record.get("validation_class"),
                record.get("priority"),
                record.get("proposed_action"),
                record.get("governance_decision"),
                record.get("authorized_action"),
                int(bool(record.get("human_review_required", False))),
                record.get("context_summary"),
                record.get("model_version"),
                record.get("policy_version"),
                record.get("evidence_reference"),
                record.get("outcome"),
                previous_hash,
                record_hash,
                payload_json,
            ),
        )
        self.conn.commit()
        return record_hash

    def validate_chain(self) -> bool:
        previous_hash = self.GENESIS_HASH
        rows = self.conn.execute(
            "SELECT previous_hash, record_hash, payload_json FROM ledger ORDER BY ledger_id"
        ).fetchall()
        for stored_previous, record_hash, payload_json in rows:
            if stored_previous != previous_hash:
                return False
            expected = sha256(f"{previous_hash}|{payload_json}".encode("utf-8")).hexdigest()
            if expected != record_hash:
                return False
            previous_hash = record_hash
        return True

    def export_csv(self, output_path: Path) -> pd.DataFrame:
        df = pd.read_sql_query("SELECT * FROM ledger ORDER BY ledger_id", self.conn)
        df.to_csv(output_path, index=False)
        return df

    def close(self) -> None:
        self.conn.close()
