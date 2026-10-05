from odoo import fields, models
from odoo.exceptions import ValidationError

from .common import BLOCKING_STATES, lock_records


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_guest = fields.Boolean(groups="thimo_guesthouse.group_guesthouse_receptionist")
    guesthouse_booking_ids = fields.One2many(
        "thimo.guesthouse.booking", "guest_id",
        groups="thimo_guesthouse.group_guesthouse_receptionist",
    )

    def write(self, vals):
        if ("active" in vals and not vals["active"]) or ("is_guest" in vals and not vals["is_guest"]):
            self.check_access("write")
            lock_records(self)
            if self.env["thimo.guesthouse.booking"].sudo().search_count([
                ("guest_id", "in", self.ids), ("state", "in", BLOCKING_STATES),
            ]):
                raise ValidationError(self.env._("A guest with active bookings cannot be archived or unmarked."))
        return super().write(vals)
