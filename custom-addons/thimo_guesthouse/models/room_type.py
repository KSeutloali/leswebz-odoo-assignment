import math

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .common import lock_records


class RoomType(models.Model):
    _name = "thimo.guesthouse.room.type"
    _description = "Guest House Room Type"
    _order = "name, id"

    name = fields.Char(required=True)
    default_rate = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True,
        default=lambda self: self.env.company.currency_id,
    )
    capacity = fields.Integer(required=True, default=1)
    description = fields.Text()
    active = fields.Boolean(default=True)
    room_ids = fields.One2many("thimo.guesthouse.room", "room_type_id")

    _positive_capacity = models.Constraint(
        "CHECK (capacity > 0)", "Room capacity must be greater than zero.",
    )
    _non_negative_rate = models.Constraint(
        "CHECK (default_rate >= 0)", "The default nightly rate cannot be negative.",
    )

    @api.constrains("name", "capacity", "default_rate")
    def _check_values(self):
        for room_type in self:
            if not room_type.name or not room_type.name.strip():
                raise ValidationError(self.env._("A room type must have a name."))
            if room_type.capacity <= 0:
                raise ValidationError(self.env._("Room capacity must be greater than zero."))
            if not math.isfinite(room_type.default_rate) or room_type.default_rate < 0:
                raise ValidationError(self.env._("The default nightly rate must be finite and non-negative."))

    def write(self, vals):
        self.check_access("write")
        lock_records(self)
        if "active" in vals and not vals["active"] and self.env["thimo.guesthouse.room"].sudo().search_count([
            ("room_type_id", "in", self.ids), ("active", "=", True),
        ]):
            raise ValidationError(self.env._("Archive the active rooms before archiving their room type."))
        return super().write(vals)
