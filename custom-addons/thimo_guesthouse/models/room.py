from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .common import BLOCKING_STATES, lock_records


class Room(models.Model):
    _name = "thimo.guesthouse.room"
    _description = "Guest House Room"
    _order = "name, id"

    name = fields.Char(string="Room Number / Name", required=True)
    room_type_id = fields.Many2one(
        "thimo.guesthouse.room.type", required=True, ondelete="restrict", index=True,
        domain=[("active", "=", True)],
    )
    active = fields.Boolean(default=True)
    maintenance = fields.Boolean(
        groups="thimo_guesthouse.group_guesthouse_manager", copy=False,
    )
    booking_ids = fields.One2many("thimo.guesthouse.booking", "room_id")
    state = fields.Selection(
        [("available", "Available"), ("reserved", "Reserved"),
         ("occupied", "Occupied"), ("maintenance", "Maintenance")],
        compute="_compute_state", store=True, readonly=True, compute_sudo=True,
    )

    _unique_name = models.Constraint("UNIQUE (name)", "Room numbers/names must be unique.")

    @api.depends("maintenance", "booking_ids.state")
    def _compute_state(self):
        for room in self:
            states = set(room.booking_ids.mapped("state"))
            room.state = (
                "maintenance" if room.maintenance else
                "occupied" if "checked_in" in states else
                "reserved" if "confirmed" in states else
                "available"
            )

    @api.constrains("name", "active", "room_type_id")
    def _check_room(self):
        for room in self:
            if not room.name or not room.name.strip():
                raise ValidationError(self.env._("A room must have a number/name."))
            if room.active and not room.room_type_id.active:
                raise ValidationError(self.env._("An active room requires an active room type."))

    @api.model_create_multi
    def create(self, vals_list):
        self.check_access("create")
        defaults = self.default_get(["room_type_id"])
        prepared = []
        for original in vals_list:
            vals = dict(original)
            if "state" in vals:
                raise ValidationError(self.env._("Room status is determined by bookings and maintenance."))
            if isinstance(vals.get("name"), str):
                vals["name"] = vals["name"].strip()
            prepared.append(vals)
        type_ids = {vals.get("room_type_id", defaults.get("room_type_id")) for vals in prepared}
        types = self.env["thimo.guesthouse.room.type"].browse([value for value in type_ids if value])
        types.check_access("read")
        lock_records(types)
        return super().create(prepared)

    def write(self, vals):
        self.check_access("write")
        vals = dict(vals)
        if "state" in vals:
            raise ValidationError(self.env._("Room status is determined by bookings and maintenance."))
        if isinstance(vals.get("name"), str):
            vals["name"] = vals["name"].strip()
        types = self.room_type_id
        if vals.get("room_type_id"):
            types |= self.env["thimo.guesthouse.room.type"].browse(vals["room_type_id"])
        types.check_access("read")
        lock_records(types)
        lock_records(self)
        if vals.get("maintenance") or ("active" in vals and not vals["active"]) or "room_type_id" in vals:
            if self.env["thimo.guesthouse.booking"].sudo().search_count([
                ("room_id", "in", self.ids), ("state", "in", BLOCKING_STATES),
            ]):
                raise ValidationError(self.env._("A room with active bookings cannot enter maintenance, be archived or change type."))
        return super().write(vals)

    def action_set_maintenance(self):
        return self.write({"maintenance": True})

    def action_end_maintenance(self):
        return self.write({"maintenance": False})
