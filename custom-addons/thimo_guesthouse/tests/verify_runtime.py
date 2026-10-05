"""Execute with `odoo shell` after loading samples; all test writes roll back.

Produces expected/actual evidence separately from the normal regression suite.
The shell provides `env`. Never run this as a normal addon import.
"""
import json
from datetime import date, timedelta

from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import convert_file


assert env.cr.dbname == "thimo_guesthouse", "Use the Guest House database."
results = []


def check(test, expected, actual):
    passed = expected == actual
    results.append({"test": test, "expected": expected, "actual": actual,
                    "result": "PASS" if passed else "FAIL"})
    assert passed, results[-1]


def reject(test, exception_type, action):
    actual = "No exception"
    try:
        with env.cr.savepoint():
            action()
    except exception_type as error:
        actual = type(error).__name__
    check(test, exception_type.__name__, actual)


Booking = env["thimo.guesthouse.booking"]
Room = env["thimo.guesthouse.room"]
Type = env["thimo.guesthouse.room.type"]
Partner = env["res.partner"]
check("Initial room types", ["Deluxe", "Family", "Standard"], sorted(Type.search([]).mapped("name")))
check("Initial room count", 5, Room.with_context(active_test=False).search_count([]))
initial_booking_count = Booking.search_count([])
initial_guest_count = Partner.search_count([("is_guest", "=", True)])
check("At least three bookings", True, initial_booking_count >= 3)
check("Guest Contacts present", True, initial_guest_count > 0)
demo_bookings = Booking.search([])
check("Different booking statuses", True, len(set(demo_bookings.mapped("state"))) >= 2)
check("Different booking dates", True, len(set(demo_bookings.mapped("check_in"))) >= 2)
check("Demo currency", ["LSL"], sorted(set(demo_bookings.mapped("currency_id.name"))))
check("Demo calculations and relationships", True,
      all(b.guest_id.is_guest and b.room_id.active and b.check_out > b.check_in
          and b.number_of_nights == (b.check_out - b.check_in).days
          and b.total == b.currency_id.round(b.number_of_nights * b.nightly_rate)
          for b in demo_bookings))
env.cr.execute("""
    SELECT count(*) FROM thimo_guesthouse_booking a
    JOIN thimo_guesthouse_booking b ON a.id < b.id AND a.room_id = b.room_id
    WHERE a.state IN ('confirmed', 'checked_in') AND b.state IN ('confirmed', 'checked_in')
      AND a.check_in < b.check_out AND a.check_out > b.check_in
""")
check("Demo overlapping active pairs", 0, env.cr.fetchone()[0])
before = {b.id: b.read(["state", "check_in", "check_out", "nightly_rate"])[0] for b in demo_bookings}
convert_file(env, "thimo_guesthouse", "demo/guesthouse_demo.xml", {}, mode="update")
check("Demo XML upgrade preserves records", before,
      {b.id: b.read(["state", "check_in", "check_out", "nightly_rate"])[0] for b in demo_bookings})


class DiscardFixtures(Exception):
    pass


try:
    with env.cr.savepoint():
        room_type = Type.create({"name": "Runtime Test Type", "default_rate": 650,
                                 "currency_id": env.ref("base.LSL").id, "capacity": 2})
        room = Room.create({"name": "RUNTIME-VERIFY-ROOM", "room_type_id": room_type.id})
        guest = Partner.create({"name": "Runtime Fictional Guest", "is_guest": True})
        arrival = date(2031, 6, 10)

        def booking(offset=0, nights=3, **values):
            start = arrival + timedelta(days=offset)
            return Booking.create({"guest_id": guest.id, "room_id": room.id,
                                   "check_in": start, "check_out": start + timedelta(days=nights), **values})

        def state_pair(record):
            return [record.state, record.room_id.state]

        stay = booking()
        check("TEST 1: create draft", ["draft", "available"], state_pair(stay))
        check("Nightly rate defaults", 650, stay.nightly_rate)
        check("Number of nights", 3, stay.number_of_nights)
        check("Total: 3 nights × LSL 650", 1950, stay.total)
        check("Reference generated", True, stay.name.startswith("TGH/") and stay.name != "New")
        reject("Check-in while draft", UserError, stay.action_check_in)
        reject("Check-out while draft", UserError, stay.action_check_out)
        reject("Equal check-out/check-in dates", ValidationError, lambda: booking(check_out=arrival))
        reject("Earlier check-out date", ValidationError,
               lambda: booking(check_out=arrival - timedelta(days=1)))
        reject("Negative nightly rate", ValidationError, lambda: booking(nightly_rate=-1))
        stay.action_confirm()
        check("TEST 2: confirm", ["confirmed", "reserved"], state_pair(stay))
        reject("Check-out before check-in", UserError, stay.action_check_out)
        reject("Repeat confirm", UserError, stay.action_confirm)
        conflict = booking(offset=1)
        reject("Overlapping active reservation", ValidationError, conflict.action_confirm)
        check("Rejected overlap remains draft", "draft", conflict.state)
        stay.action_check_in()
        check("TEST 3: check in", ["checked_in", "occupied"], state_pair(stay))
        reject("Reserve overlapping stay in occupied room", ValidationError, conflict.action_confirm)
        reject("Cancel checked-in booking", UserError, stay.action_cancel)
        check("Rejected cancellation keeps occupancy", ["checked_in", "occupied"], state_pair(stay))
        stay.action_check_out()
        check("TEST 4: check out", ["checked_out", "available"], state_pair(stay))
        reject("Reopen checked-out booking", UserError, stay.action_check_in)

        cancelled = booking()
        cancelled.action_confirm()
        cancelled.action_cancel()
        check("Cancel confirmed booking", ["cancelled", "available"], state_pair(cancelled))
        replacement = booking()
        replacement.action_confirm()
        check("Cancelled stay does not block same dates", ["confirmed", "reserved"], state_pair(replacement))
        following = booking(offset=3)
        following.action_confirm()
        check("Adjacent stays allowed", "confirmed", following.state)
        replacement.action_cancel()
        check("Cancel preserves another reservation", ["cancelled", "reserved"], state_pair(replacement))
        following.action_cancel()
        check("Cancel last reservation releases room", "available", room.state)

        occupant, future = booking(offset=20), booking(offset=30)
        occupant.action_confirm()
        occupant.action_check_in()
        future.action_confirm()
        check("Future non-overlapping reservation while occupied", ["confirmed", "occupied"], state_pair(future))
        reject("Second physical check-in", ValidationError, future.action_check_in)
        occupant.action_check_out()
        check("Checkout preserves future reservation", ["checked_out", "reserved"], state_pair(occupant))
        future.action_check_in()
        check("Next guest can check in after departure", ["checked_in", "occupied"], state_pair(future))
        future.action_check_out()

        changes = {"guest_id": guest.id, "room_id": room.id,
                   "check_in": arrival + timedelta(days=1), "check_out": arrival + timedelta(days=5),
                   "nightly_rate": 700, "currency_id": env.ref("base.LSL").id}
        for state in ("confirmed", "checked_in", "checked_out", "cancelled"):
            protected = booking(offset=50)
            protected.action_confirm()
            if state in ("checked_in", "checked_out"):
                protected.action_check_in()
            if state == "checked_out":
                protected.action_check_out()
            if state == "cancelled":
                protected.action_cancel()
            count = 0
            for field, value in changes.items():
                try:
                    with env.cr.savepoint():
                        protected.write({field: value})
                except UserError:
                    count += 1
            check(f"Critical fields frozen: {state}", 6, count)
            if state == "confirmed":
                protected.action_cancel()
            if state == "checked_in":
                protected.action_check_out()

        room.action_set_maintenance()
        unavailable = booking()
        reject("Maintenance room confirmation", ValidationError, unavailable.action_confirm)
        room.action_end_maintenance()
        receptionist = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Runtime Receptionist", "login": "runtime_guesthouse_receptionist",
            "group_ids": [Command.set([env.ref("thimo_guesthouse.group_guesthouse_receptionist").id])],
        })
        staff_stay = booking(offset=70).with_user(receptionist)
        staff_stay.action_confirm()
        staff_stay.action_check_in()
        staff_stay.action_check_out()
        check("Receptionist booking lifecycle", ["checked_out", "available"], state_pair(staff_stay))
        staff_guest = Partner.with_user(receptionist).create({"name": "Runtime New Guest", "is_guest": True})
        check("Receptionist creates standard guest Contact", True, staff_guest.is_guest)
        reject("Receptionist cannot modify rooms", AccessError,
               lambda: room.with_user(receptionist).action_set_maintenance())
        reject("Receptionist cannot create room types", AccessError,
               lambda: Type.with_user(receptionist).create({"name": "Denied"}))
        reject("Receptionist cannot delete booking history", AccessError, staff_stay.unlink)
        reject("Public cannot read bookings", AccessError,
               lambda: Booking.with_user(env.ref("base.public_user")).search([]))
        ordinary = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Runtime Ordinary User", "login": "runtime_guesthouse_ordinary",
            "group_ids": [Command.set([env.ref("base.group_user").id])],
        })
        reject("Unassigned internal user cannot read bookings", AccessError,
               lambda: Booking.with_user(ordinary).search([]))
        portal = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Runtime Portal User", "login": "runtime_guesthouse_portal",
            "group_ids": [Command.set([env.ref("base.group_portal").id])],
        })
        reject("Portal cannot read bookings", AccessError, lambda: Booking.with_user(portal).search([]))
        visible = env["ir.ui.menu"].with_user(receptionist)._visible_menu_ids()
        check("Receptionist operational menus", True, all(
            env.ref(f"thimo_guesthouse.menu_{name}").id in visible for name in ("bookings", "rooms", "guests")))
        check("Configuration restricted to managers", False,
              env.ref("thimo_guesthouse.menu_room_types").id in visible)
        manager = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Runtime Manager", "login": "runtime_guesthouse_manager",
            "group_ids": [Command.set([env.ref("thimo_guesthouse.group_guesthouse_manager").id])],
        })
        manager_type = Type.with_user(manager).create({"name": "Runtime Manager Type", "default_rate": 500, "capacity": 2})
        manager_room = Room.with_user(manager).create({"name": "RUNTIME-MANAGER", "room_type_id": manager_type.id})
        manager_room.action_set_maintenance()
        check("Manager can configure rooms", "maintenance", manager_room.state)
        manager_room.unlink()
        manager_type.unlink()
        check("Manager sees Room Types menu", True, env.ref("thimo_guesthouse.menu_room_types").id in
              env["ir.ui.menu"].with_user(manager)._visible_menu_ids())
        raise DiscardFixtures()
except DiscardFixtures:
    pass

env.cr.rollback()
check("Final room count after rollback", 5, Room.with_context(active_test=False).search_count([]))
check("Final booking count after rollback", initial_booking_count, Booking.search_count([]))
check("Final guest count after rollback", initial_guest_count,
      Partner.search_count([("is_guest", "=", True)]))
print("GUESTHOUSE_RESULTS=" + json.dumps(results, default=str))
