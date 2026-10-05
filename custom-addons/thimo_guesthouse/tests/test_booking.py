from datetime import date, timedelta

from psycopg2 import IntegrityError

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form, TransactionCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestGuesthouseBooking(TransactionCase):
    # Menu visibility examines other applications, so use the complete registry.
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Booking = cls.env["thimo.guesthouse.booking"]
        cls.room_type = cls.env["thimo.guesthouse.room.type"].create({
            "name": "Test Double", "capacity": 2, "default_rate": 650,
        })
        cls.room = cls.env["thimo.guesthouse.room"].create({
            "name": "TEST-201", "room_type_id": cls.room_type.id,
        })
        cls.guest = cls.env["res.partner"].create({"name": "Test Guest", "is_guest": True})
        cls.arrival = date(2030, 6, 10)

    def _booking(self, offset=0, nights=2, **values):
        start = self.arrival + timedelta(days=offset)
        return self.Booking.create({
            "guest_id": self.guest.id, "room_id": self.room.id,
            "check_in": start, "check_out": start + timedelta(days=nights),
            **values,
        })

    def test_rate_totals_reference_and_partner(self):
        booking = self._booking(nights=3)
        self.assertEqual(booking.nightly_rate, 650)
        self.assertEqual(booking.number_of_nights, 3)
        self.assertEqual(booking.total, 1950)
        self.assertRegex(booking.name, r"^TGH/\d{4}/\d{5,}$")
        self.assertIn(booking, self.guest.guesthouse_booking_ids)
        booking.write({"nightly_rate": 700})
        self.assertEqual(booking.total, 2100)
        self.room_type.write({"default_rate": 800})
        self.assertEqual(booking.nightly_rate, 700)
        self.assertEqual(self._booking().nightly_rate, 800)
        duplicate = booking.copy()
        self.assertNotEqual(duplicate.name, booking.name)
        self.assertEqual(duplicate.state, "draft")

    def test_complete_lifecycle(self):
        booking = self._booking()
        self.assertEqual(self.room.state, "available")
        booking.action_confirm()
        self.assertEqual((booking.state, self.room.state), ("confirmed", "reserved"))
        booking.action_check_in()
        self.assertEqual((booking.state, self.room.state), ("checked_in", "occupied"))
        booking.action_check_out()
        self.assertEqual((booking.state, self.room.state), ("checked_out", "available"))

    def test_booking_creation_through_form(self):
        form = Form(self.Booking, view="thimo_guesthouse.view_booking_form")
        self.assertEqual(form.name, "New")
        form.guest_id = self.guest
        form.room_id = self.room
        form.check_in = self.arrival
        form.check_out = self.arrival + timedelta(days=3)
        self.assertEqual(form.nightly_rate, 650)
        self.assertEqual(form.number_of_nights, 3)
        self.assertEqual(form.total, 1950)
        booking = form.save()
        self.assertNotEqual(booking.name, "New")
        self.assertEqual(booking.total, 1950)

    def test_cancel_releases_dates(self):
        booking = self._booking()
        booking.action_confirm()
        booking.action_cancel()
        self.assertEqual((booking.state, self.room.state), ("cancelled", "available"))
        replacement = self._booking()
        replacement.action_confirm()
        self.assertEqual(self.room.state, "reserved")

    def test_adjacent_stays_and_remaining_reservation(self):
        first, following = self._booking(), self._booking(offset=2)
        first.action_confirm()
        following.action_confirm()
        first.action_check_in()
        first.action_check_out()
        self.assertEqual(self.room.state, "reserved")
        following.action_cancel()
        self.assertEqual(self.room.state, "available")

    def test_overlaps_and_drafts(self):
        first = self._booking(nights=4)
        overlap = self._booking(offset=1)
        first.action_confirm()
        for conflicting in (overlap, self._booking(offset=-1, nights=3), self._booking(offset=-1, nights=7)):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                conflicting.action_confirm()
        self.assertEqual(overlap.state, "draft")
        other_room = self.env["thimo.guesthouse.room"].create({
            "name": "TEST-202", "room_type_id": self.room_type.id,
        })
        self._booking(room_id=other_room.id).action_confirm()

    def test_date_and_rate_validation(self):
        for end in (self.arrival, self.arrival - timedelta(days=1)):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self._booking(check_out=end)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self._booking(nightly_rate=-1)
        booking = self._booking()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            booking.write({"check_out": booking.check_in})

    def test_invalid_transitions_and_api_writes(self):
        booking = self._booking()
        for action in (booking.action_check_in, booking.action_check_out, booking.action_cancel):
            with self.assertRaises(UserError), self.cr.savepoint():
                action()
        with self.assertRaises(UserError), self.cr.savepoint():
            self._booking(state="confirmed")
        # A direct API write gets exactly the same validation as a button.
        booking.write({"state": "confirmed"})
        for values in ({"state": "draft"}, {"state": "checked_out"}, {"nightly_rate": 1}):
            with self.assertRaises(UserError), self.cr.savepoint():
                booking.write(values)
        booking.action_check_in()
        with self.assertRaises(UserError), self.cr.savepoint():
            booking.action_cancel()
        booking.action_check_out()
        with self.assertRaises(UserError), self.cr.savepoint():
            booking.action_check_in()

    def test_only_one_physical_occupant(self):
        first, next_stay = self._booking(), self._booking(offset=10)
        first.action_confirm()
        next_stay.action_confirm()
        first.action_check_in()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            next_stay.action_check_in()
        first.action_check_out()
        next_stay.action_check_in()
        self.assertEqual(self.room.state, "occupied")

    def test_reserving_an_occupied_room(self):
        occupant = self._booking(nights=4)
        occupant.action_confirm()
        occupant.action_check_in()
        overlapping = self._booking(offset=1)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            overlapping.action_confirm()
        self.assertEqual((overlapping.state, self.room.state), ("draft", "occupied"))
        # Physical occupancy today does not prevent a non-overlapping future stay.
        future = self._booking(offset=10)
        future.action_confirm()
        self.assertEqual((future.state, self.room.state), ("confirmed", "occupied"))

    def test_critical_fields_frozen_in_every_non_draft_state(self):
        other_room = self.env["thimo.guesthouse.room"].create({
            "name": "TEST-FROZEN", "room_type_id": self.room_type.id,
        })
        other_guest = self.env["res.partner"].create({"name": "Other Test Guest", "is_guest": True})
        changes = {
            "guest_id": other_guest.id, "room_id": other_room.id,
            "check_in": self.arrival + timedelta(days=1),
            "check_out": self.arrival + timedelta(days=4),
            "nightly_rate": 700, "currency_id": self.room_type.currency_id.id,
        }
        booking = self._booking()
        booking.action_confirm()
        for action in (None, booking.action_check_in, booking.action_check_out):
            if action:
                action()
            before = booking.read(list(changes))[0]
            for field, value in changes.items():
                with self.assertRaises(UserError), self.cr.savepoint():
                    booking.write({field: value})
            self.assertEqual(booking.read(list(changes))[0], before)
        cancelled = self._booking(offset=10)
        cancelled.action_confirm()
        cancelled.action_cancel()
        for field, value in changes.items():
            with self.assertRaises(UserError), self.cr.savepoint():
                cancelled.write({field: value})

    def test_atomic_batch_confirmation(self):
        first, second = self._booking(), self._booking()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            (first | second).action_confirm()
        self.assertEqual((first.state, second.state, self.room.state), ("draft", "draft", "available"))

    def test_maintenance_and_archiving(self):
        self.room.action_set_maintenance()
        booking = self._booking()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            booking.action_confirm()
        self.room.action_end_maintenance()
        booking.action_confirm()
        for action in (self.room.action_set_maintenance, self.room.action_archive,
                       self.guest.action_archive, self.room_type.action_archive):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                action()
        booking.action_cancel()
        self.room.action_archive()
        self.room_type.action_archive()

    def test_snapshots_room_defaults_and_history(self):
        another_type = self.env["thimo.guesthouse.room.type"].create({
            "name": "Test Family", "capacity": 4, "default_rate": 900,
        })
        another_room = self.env["thimo.guesthouse.room"].create({
            "name": "TEST-301", "room_type_id": another_type.id,
        })
        booking = self._booking()
        booking.write({"room_id": another_room.id})
        self.assertEqual(booking.nightly_rate, 900)
        booking.action_confirm()
        another_type.write({"default_rate": 1000})
        self.assertEqual(booking.nightly_rate, 900)
        with self.assertRaises(UserError), self.cr.savepoint():
            booking.unlink()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            booking.write({"name": "CHANGED"})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            another_room.write({"state": "available"})

    @mute_logger("odoo.sql_db")
    def test_database_overlap_and_occupancy_guards(self):
        first, second, later = self._booking(), self._booking(), self._booking(offset=10)
        first.action_confirm()
        self.env.flush_all()
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.cr.execute("UPDATE thimo_guesthouse_booking SET state = 'confirmed' WHERE id = %s", [second.id])
        first.action_check_in()
        later.action_confirm()
        self.env.flush_all()
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.cr.execute("UPDATE thimo_guesthouse_booking SET state = 'checked_in' WHERE id = %s", [later.id])

    def test_receptionist_and_public_permissions(self):
        receptionist = self.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Test Receptionist", "login": "test_thimo_receptionist",
            "group_ids": [Command.set([self.env.ref("thimo_guesthouse.group_guesthouse_receptionist").id])],
        })
        booking = self._booking().with_user(receptionist)
        booking.action_confirm()
        booking.action_check_in()
        booking.action_check_out()
        self.assertEqual(self.room.state, "available")
        self.env["res.partner"].with_user(receptionist).create({"name": "New Guest", "is_guest": True})
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.room.with_user(receptionist).action_set_maintenance()
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.Booking.with_user(self.env.ref("base.public_user")).search([])
        menus = self.env["ir.ui.menu"].with_user(receptionist)
        visible = menus._visible_menu_ids()
        self.assertIn(self.env.ref("thimo_guesthouse.menu_bookings").id, visible)
        self.assertIn(self.env.ref("thimo_guesthouse.menu_guests").id, visible)
        self.assertNotIn(self.env.ref("thimo_guesthouse.menu_guesthouse_configuration").id, visible)
        self.assertNotIn(self.env.ref("thimo_guesthouse.menu_room_types").id, visible)
        receptionist.write({"group_ids": [Command.set([self.env.ref("base.group_user").id])]})
        visible = menus._visible_menu_ids()
        self.assertNotIn(self.env.ref("thimo_guesthouse.menu_guesthouse_root").id, visible)
        self.assertNotIn(self.env.ref("thimo_guesthouse.menu_guests").id, visible)
