import math
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .common import BLOCKING_STATES, lock_records


class Booking(models.Model):
    _name = "thimo.guesthouse.booking"
    _description = "Guest House Booking"
    _order = "check_in desc, id desc"

    name = fields.Char(
        string="Reference", required=True, readonly=True, copy=False, index=True,
        default=lambda self: self.env._("New"),
    )
    guest_id = fields.Many2one(
        "res.partner", string="Guest", required=True, ondelete="restrict", index=True,
        domain=[("is_guest", "=", True), ("active", "=", True)],
    )
    room_id = fields.Many2one(
        "thimo.guesthouse.room", string="Room", required=True, ondelete="restrict", index=True,
        domain=[("active", "=", True), ("state", "!=", "maintenance")],
    )
    check_in = fields.Date(required=True, default=fields.Date.context_today, index=True)
    check_out = fields.Date(
        required=True, default=lambda self: fields.Date.context_today(self) + timedelta(days=1),
    )
    nightly_rate = fields.Monetary(required=True)
    currency_id = fields.Many2one("res.currency", required=True, readonly=True)
    number_of_nights = fields.Integer(compute="_compute_amounts", store=True, readonly=True)
    total = fields.Monetary(compute="_compute_amounts", store=True, readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("checked_in", "Checked In"),
         ("checked_out", "Checked Out"), ("cancelled", "Cancelled")],
        required=True, default="draft", readonly=True, copy=False, index=True,
    )

    _unique_reference = models.Constraint("UNIQUE (name)", "Booking references must be unique.")
    _valid_dates = models.Constraint(
        "CHECK (check_out > check_in)", "Check-out must be after check-in.",
    )
    _non_negative_rate = models.Constraint(
        "CHECK (nightly_rate >= 0)", "The nightly rate cannot be negative.",
    )
    _no_overlap = models.Constraint(
        "EXCLUDE USING gist (room_id WITH =, daterange(check_in, check_out, '[)') WITH &&) "
        "WHERE (state IN ('confirmed', 'checked_in'))",
        "This room already has an active booking for these dates.",
    )
    _one_checked_in = models.UniqueIndex(
        "(room_id) WHERE state = 'checked_in'",
        "Only one guest can be checked into a room at a time.",
    )

    _editable_fields = {"guest_id", "room_id", "check_in", "check_out", "nightly_rate", "currency_id"}
    _transitions = {
        "draft": {"confirmed"},
        "confirmed": {"checked_in", "cancelled"},
        "checked_in": {"checked_out"},
        "checked_out": set(),
        "cancelled": set(),
    }

    @api.depends("check_in", "check_out", "nightly_rate", "currency_id")
    def _compute_amounts(self):
        for booking in self:
            booking.number_of_nights = (
                (booking.check_out - booking.check_in).days
                if booking.check_in and booking.check_out else 0
            )
            amount = booking.number_of_nights * booking.nightly_rate
            booking.total = booking.currency_id.round(amount) if booking.currency_id else amount

    def _validate_stay(self, check_in, check_out, nightly_rate):
        start, end = fields.Date.to_date(check_in), fields.Date.to_date(check_out)
        if not start or not end or end <= start:
            raise ValidationError(self.env._("Check-out must be after check-in."))
        if not math.isfinite(float(nightly_rate)) or float(nightly_rate) < 0:
            raise ValidationError(self.env._("The nightly rate must be finite and non-negative."))

    @api.constrains("check_in", "check_out", "nightly_rate", "state", "room_id")
    def _check_stay(self):
        for booking in self:
            booking._validate_stay(booking.check_in, booking.check_out, booking.nightly_rate)
            if booking.state in BLOCKING_STATES:
                booking._check_overlap()

    def _check_overlap(self):
        self.ensure_one()
        conflict = self.sudo().search([
            ("id", "!=", self.id), ("room_id", "=", self.room_id.id),
            ("state", "in", BLOCKING_STATES),
            ("check_in", "<", self.check_out), ("check_out", ">", self.check_in),
        ], limit=1)
        if conflict:
            raise ValidationError(self.env._(
                "Room %(room)s already has active booking %(reference)s for these dates.",
                room=self.room_id.display_name, reference=conflict.name,
            ))

    def _check_allocation(self, target_state):
        self.ensure_one()
        if not self.guest_id.active or not self.guest_id.is_guest:
            raise ValidationError(self.env._("Select an active contact marked as a guest."))
        room = self.room_id
        if not room.active or not room.room_type_id.active or room.sudo().maintenance:
            raise ValidationError(self.env._("Select an active room outside maintenance with an active room type."))
        self._check_overlap()
        if target_state == "checked_in" and self.sudo().search_count([
            ("id", "!=", self.id), ("room_id", "=", room.id), ("state", "=", "checked_in"),
        ]):
            raise ValidationError(self.env._("Another guest is still checked into this room."))

    @api.onchange("room_id")
    def _onchange_room_id(self):
        if self.state == "draft" and self.room_id:
            self.nightly_rate = self.room_id.room_type_id.default_rate
            self.currency_id = self.room_id.room_type_id.currency_id

    @api.model_create_multi
    def create(self, vals_list):
        self.check_access("create")
        defaults = self.default_get(["guest_id", "room_id", "check_in", "check_out", "state", "nightly_rate"])
        prepared = []
        for original in vals_list:
            vals = {**defaults, **original}
            if vals.get("state", "draft") != "draft":
                raise UserError(self.env._("New bookings must start in Draft."))
            if {"number_of_nights", "total"} & vals.keys():
                raise ValidationError(self.env._("Nights and total are calculated automatically."))
            room = self.env["thimo.guesthouse.room"].browse(vals.get("room_id")).exists()
            if len(room) != 1:
                raise ValidationError(self.env._("Select a room for the booking."))
            room.check_access("read")
            vals.setdefault("nightly_rate", room.room_type_id.default_rate)
            currency = room.room_type_id.currency_id
            if vals.get("currency_id", currency.id) != currency.id:
                raise ValidationError(self.env._("Use the selected room type's currency."))
            vals["currency_id"] = currency.id
            self._validate_stay(vals.get("check_in"), vals.get("check_out"), vals["nightly_rate"])
            vals["name"] = self.env["ir.sequence"].next_by_code("thimo_guesthouse.booking")
            if not vals["name"]:
                raise UserError(self.env._("The guest-house booking sequence is missing."))
            prepared.append(vals)
        return super().create(prepared)

    def write(self, vals):
        self.check_access("write")
        if {"name", "number_of_nights", "total"} & vals.keys():
            raise ValidationError(self.env._("Reference, nights and total cannot be edited."))
        if not self:
            return True
        lock_records(self)
        if self._editable_fields & vals.keys() and any(booking.state != "draft" for booking in self):
            raise UserError(self.env._("Only draft bookings can change their guest, room, dates or rate."))

        guests = self.guest_id
        if vals.get("guest_id"):
            guests |= self.env["res.partner"].browse(vals["guest_id"])
        rooms = self.room_id
        if vals.get("room_id"):
            rooms |= self.env["thimo.guesthouse.room"].browse(vals["room_id"])
        guests.check_access("read")
        rooms.check_access("read")
        lock_records(guests)
        lock_records(rooms.room_type_id)
        lock_records(rooms)

        target_state = vals.get("state")
        if "state" in vals:
            for booking in self:
                if target_state not in self._transitions[booking.state]:
                    raise UserError(self.env._(
                        "Booking %(reference)s cannot move from %(current)s to %(target)s.",
                        reference=booking.name, current=booking.state, target=target_state,
                    ))

        # Apply draft changes separately per record so defaults remain room-specific.
        for booking in self:
            values = dict(vals)
            if "room_id" in values:
                room = self.env["thimo.guesthouse.room"].browse(values["room_id"]).exists()
                if len(room) != 1:
                    raise ValidationError(self.env._("Select a room for the booking."))
                values.setdefault("nightly_rate", room.room_type_id.default_rate)
                values.setdefault("currency_id", room.room_type_id.currency_id.id)
            if "currency_id" in values:
                room = self.env["thimo.guesthouse.room"].browse(values.get("room_id", booking.room_id.id))
                if values["currency_id"] != room.room_type_id.currency_id.id:
                    raise ValidationError(self.env._("Use the selected room type's currency."))
            booking._validate_stay(
                values.get("check_in", booking.check_in), values.get("check_out", booking.check_out),
                values.get("nightly_rate", booking.nightly_rate),
            )
            # Validate the final draft values before confirmation's SQL constraint.
            draft_values = {key: value for key, value in values.items() if key != "state"}
            if draft_values:
                super(Booking, booking).write(draft_values)
            if target_state in BLOCKING_STATES:
                booking._check_allocation(target_state)
            if "state" in values:
                super(Booking, booking).write({"state": target_state})
        return True

    def action_confirm(self):
        return self.write({"state": "confirmed"})

    def action_check_in(self):
        return self.write({"state": "checked_in"})

    def action_check_out(self):
        return self.write({"state": "checked_out"})

    def action_cancel(self):
        return self.write({"state": "cancelled"})

    @api.ondelete(at_uninstall=False)
    def _unlink_only_drafts(self):
        if any(booking.state != "draft" for booking in self):
            raise UserError(self.env._("Only draft bookings can be deleted; retain other bookings as history."))
