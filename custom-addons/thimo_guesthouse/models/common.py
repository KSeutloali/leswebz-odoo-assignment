from odoo.tools import SQL


BLOCKING_STATES = ("confirmed", "checked_in")


def lock_records(records):
    """Serialize operations even with Odoo's repeatable-read snapshots.

    An actual row update makes competing transactions retry with a fresh
    snapshot. A SELECT FOR UPDATE alone would leave an old snapshot usable.
    Callers check access before this private, non-business-field update.
    Always acquire records in ID order to avoid deadlocks.
    """
    if not records:
        return
    records.flush_recordset()
    for record_id in sorted(records.ids):
        records.env.cr.execute(SQL(
            "UPDATE %s SET id = id WHERE id = %s",
            SQL.identifier(records._table), record_id,
        ))
    records.invalidate_recordset()
