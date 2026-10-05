# Guest House completion and test results

Verified on 5 October 2026 against Odoo Community 19.0-20260926 and PostgreSQL 16.15 at localhost:8069, database `thimo_guesthouse`, addon version `19.0.1.2.0`.

The upgrade ran 16 Odoo transaction tests: **0 failed, 0 errors**. All 58 runtime acceptance checks and all 36 distinct browser checks passed. Results below record observed behavior, not just source inspection. Automated transaction and runtime fixtures were rolled back. Two browser-created test bookings were removed by their recorded IDs; the original demo records were preserved. Sequence numbers can have gaps because test transactions do not roll back sequence allocation.

## Retained demonstration data

There are exactly **3 room types, 5 rooms, 5 fictional guest Contacts and 5 bookings**. All rates and totals are in Lesotho maloti (LSL, displayed as M). The fictional guests contain no phone, email or address information. Dates were calculated at the first demo load and remain unchanged on upgrades.

| Room | Type | Capacity | Nightly LSL | Room state |
|---|---|---|---|---|
| 101 | Standard | 2 | 450 | available |
| 102 | Standard | 2 | 450 | reserved |
| 201 | Deluxe | 2 | 650 | occupied |
| 202 | Deluxe | 2 | 650 | available |
| 301 | Family | 4 | 900 | available |

| Booking | Fictional guest | Room | Check-in | Check-out | Nights | Total LSL | State |
|---|---|---|---|---|---|---|---|
| TGH/2026/00157 | Demo Guest Alpha | 101 | 2026-10-14 | 2026-10-16 | 2 | 900 | draft |
| TGH/2026/00158 | Demo Guest Bravo | 102 | 2026-10-07 | 2026-10-10 | 3 | 1350 | confirmed |
| TGH/2026/00159 | Demo Guest Charlie | 201 | 2026-10-04 | 2026-10-07 | 3 | 1950 | checked_in |
| TGH/2026/00160 | Demo Guest Delta | 202 | 2026-09-27 | 2026-09-29 | 2 | 1300 | checked_out |
| TGH/2026/00161 | Demo Guest Echo | 301 | 2026-10-11 | 2026-10-13 | 2 | 1800 | cancelled |

## Runtime acceptance checks

State pairs below are **booking / room**. A negative test passes when Odoo rejects the operation with the expected exception. Critical-field checks each cover guest, room, arrival, departure, nightly rate and currency. Temporary test stays used June 2031 and LSL 650 per night.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Initial room types | Deluxe / Family / Standard | Deluxe / Family / Standard | PASS |
| Initial room count | 5 | 5 | PASS |
| Initial booking count | 5 | 5 | PASS |
| Fictional guest count | 5 | 5 | PASS |
| Demo states | cancelled / checked_in / checked_out / confirmed / draft | cancelled / checked_in / checked_out / confirmed / draft | PASS |
| Demo currency | LSL | LSL | PASS |
| Demo calculations and relationships | true | true | PASS |
| Demo overlapping active pairs | 0 | 0 | PASS |
| Demo XML upgrade preserves records | Five original snapshots unchanged | Five original snapshots unchanged | PASS |
| TEST 1: create draft | draft / available | draft / available | PASS |
| Nightly rate defaults | 650 | 650 | PASS |
| Number of nights | 3 | 3 | PASS |
| Total: 3 nights × LSL 650 | 1950 | 1950 | PASS |
| Reference generated | true | true | PASS |
| Check-in while draft | UserError | UserError | PASS |
| Check-out while draft | UserError | UserError | PASS |
| Equal check-out/check-in dates | ValidationError | ValidationError | PASS |
| Earlier check-out date | ValidationError | ValidationError | PASS |
| Negative nightly rate | ValidationError | ValidationError | PASS |
| TEST 2: confirm | confirmed / reserved | confirmed / reserved | PASS |
| Check-out before check-in | UserError | UserError | PASS |
| Repeat confirm | UserError | UserError | PASS |
| Overlapping active reservation | ValidationError | ValidationError | PASS |
| Rejected overlap remains draft | draft | draft | PASS |
| TEST 3: check in | checked_in / occupied | checked_in / occupied | PASS |
| Reserve overlapping stay in occupied room | ValidationError | ValidationError | PASS |
| Cancel checked-in booking | UserError | UserError | PASS |
| Rejected cancellation keeps occupancy | checked_in / occupied | checked_in / occupied | PASS |
| TEST 4: check out | checked_out / available | checked_out / available | PASS |
| Reopen checked-out booking | UserError | UserError | PASS |
| Cancel confirmed booking | cancelled / available | cancelled / available | PASS |
| Cancelled stay does not block same dates | confirmed / reserved | confirmed / reserved | PASS |
| Adjacent stays allowed | confirmed | confirmed | PASS |
| Cancel preserves another reservation | cancelled / reserved | cancelled / reserved | PASS |
| Cancel last reservation releases room | available | available | PASS |
| Future non-overlapping reservation while occupied | confirmed / occupied | confirmed / occupied | PASS |
| Second physical check-in | ValidationError | ValidationError | PASS |
| Checkout preserves future reservation | checked_out / reserved | checked_out / reserved | PASS |
| Next guest can check in after departure | checked_in / occupied | checked_in / occupied | PASS |
| Critical fields frozen: confirmed | 6 | 6 | PASS |
| Critical fields frozen: checked_in | 6 | 6 | PASS |
| Critical fields frozen: checked_out | 6 | 6 | PASS |
| Critical fields frozen: cancelled | 6 | 6 | PASS |
| Maintenance room confirmation | ValidationError | ValidationError | PASS |
| Receptionist booking lifecycle | checked_out / available | checked_out / available | PASS |
| Receptionist creates standard guest Contact | true | true | PASS |
| Receptionist cannot modify rooms | AccessError | AccessError | PASS |
| Receptionist cannot create room types | AccessError | AccessError | PASS |
| Receptionist cannot delete booking history | AccessError | AccessError | PASS |
| Public cannot read bookings | AccessError | AccessError | PASS |
| Unassigned internal user cannot read bookings | AccessError | AccessError | PASS |
| Portal cannot read bookings | AccessError | AccessError | PASS |
| Receptionist operational menus | true | true | PASS |
| Configuration restricted to managers | false | false | PASS |
| Manager can configure rooms | maintenance | maintenance | PASS |
| Manager sees Room Types menu | true | true | PASS |
| Final room count after rollback | 5 | 5 | PASS |
| Final booking count after rollback | 5 | 5 | PASS |

## Odoo transaction regression tests

These tests ran during the actual module upgrade, including Odoo's Form helper, real ORM constraints and direct PostgreSQL integrity checks. The test log is in the persistent Odoo volume at `/var/lib/odoo/guesthouse-completion-tests.log`.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| test_adjacent_stays_and_remaining_reservation | Adjacent dates accepted; another reservation keeps room reserved | Both stays confirmed; checkout left reserved; final cancellation made available | PASS |
| test_atomic_batch_confirmation | Conflicting batch fails atomically | ValidationError; both bookings draft and room available after rollback | PASS |
| test_booking_creation_through_form | Form saves draft with generated reference and correct defaults | Odoo Form saved; rate 650, 3 nights, total 1950; reference replaced New | PASS |
| test_cancel_releases_dates | Confirmed cancellation releases room and permits replacement | Cancelled/available; replacement on same dates confirmed/reserved | PASS |
| test_complete_lifecycle | Draft → confirmed → checked_in → checked_out; corresponding room states | Available → reserved → occupied → available; booking states matched | PASS |
| test_critical_fields_frozen_in_every_non_draft_state | Six critical fields protected in all four non-draft states | All 24 writes rejected with UserError; stored values preserved | PASS |
| test_database_overlap_and_occupancy_guards | Database rejects overlapping active states and second occupant | Both direct SQL updates raised IntegrityError | PASS |
| test_date_and_rate_validation | Equal/earlier departure and negative rate rejected | Create/write checks raised ValidationError | PASS |
| test_invalid_transitions_and_api_writes | Invalid buttons and direct state writes rejected | Draft check-in/out/cancel, create-confirmed, backwards/jump transitions and checked-in cancellation raised UserError | PASS |
| test_maintenance_and_archiving | Maintenance unavailable; active reservations protect rooms, types and guests | ValidationError for unavailable allocation and guarded archive/maintenance actions | PASS |
| test_only_one_physical_occupant | Second physical check-in blocked until previous guest leaves | Second check-in rejected; accepted after previous checkout | PASS |
| test_overlaps_and_drafts | All overlap shapes rejected on confirmation; draft/different room allowed | Three conflicting confirmations raised ValidationError; other room confirmed | PASS |
| test_rate_totals_reference_and_partner | Correct totals, rate snapshots, guest relation, unique sequence | 3 × 650 = 1950; override 700 = 2100; later default 800; copy draft with new reference | PASS |
| test_receptionist_and_public_permissions | Staff operates bookings/Contacts; configuration and public access restricted | Staff lifecycle and guest create succeeded; unauthorized writes/read raised AccessError; menus matched roles | PASS |
| test_reserving_an_occupied_room | Overlapping reservation blocked; non-overlapping future dates permitted | Overlap raised ValidationError; future booking confirmed while room stayed occupied | PASS |
| test_snapshots_room_defaults_and_history | Room change sets draft rate; confirmed history/reference/status protected | Draft rate 900; snapshot unchanged after default 1000; forbidden edits/deletion rejected | PASS |

## Browser checks

Verified with a real headless Chrome session authenticated through the normal Odoo login. Menus and records were opened, search was applied, and workflow buttons were clicked. Server reads after each button click confirmed both booking and room states. There were no uncaught JavaScript exceptions. Duplicate successful navigation checks are listed once.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Browser booking list | 5 | 5 | PASS |
| Browser buttons: draft | action_confirm | action_confirm | PASS |
| Browser booking fields: draft | true | true | PASS |
| Browser rate editable: draft | true | true | PASS |
| Browser buttons: confirmed | action_cancel / action_check_in | action_cancel / action_check_in | PASS |
| Browser booking fields: confirmed | true | true | PASS |
| Browser rate editable: confirmed | false | false | PASS |
| Browser buttons: checked_in | action_check_out | action_check_out | PASS |
| Browser booking fields: checked_in | true | true | PASS |
| Browser rate editable: checked_in | false | false | PASS |
| Browser buttons: checked_out | None | None | PASS |
| Browser booking fields: checked_out | true | true | PASS |
| Browser rate editable: checked_out | false | false | PASS |
| Browser buttons: cancelled | None | None | PASS |
| Browser booking fields: cancelled | true | true | PASS |
| Browser rate editable: cancelled | false | false | PASS |
| Browser menu: guesthouse-rooms | 5 | 5 | PASS |
| Browser Room form | true | true | PASS |
| Browser menu: guesthouse-guests | 5 | 5 | PASS |
| Browser standard Contact guest flag | true | true | PASS |
| Browser Contact booking-history tab | true | true | PASS |
| Browser menu: guesthouse-room-types | 3 | 3 | PASS |
| Browser Room Type form | true | true | PASS |
| Browser menu: guesthouse-bookings | 5 | 5 | PASS |
| Browser Cancelled search filter | 1 | 1 | PASS |
| Browser Cancelled result | true | true | PASS |
| Browser new booking defaults | true | true | PASS |
| Browser create draft | draft / available | draft / available | PASS |
| Browser Confirm click | confirmed / reserved | confirmed / reserved | PASS |
| Browser Check In click | checked_in / occupied | checked_in / occupied | PASS |
| Browser Check Out click | checked_out / available | checked_out / available | PASS |
| Browser new booking defaults (cancel case) | true | true | PASS |
| Browser create draft (cancel case) | draft / available | draft / available | PASS |
| Browser Confirm click (cancel case) | confirmed / reserved | confirmed / reserved | PASS |
| Browser Cancel click | cancelled / available | cancelled / available | PASS |
| Browser uncaught JavaScript exceptions | 0 | 0 | PASS |

## Module, environment and cleanup checks

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Module upgrade | Installed 19.0.1.2.0; no model/view/access errors | Upgrade exited 0; version 19.0.1.2.0 installed | PASS |
| Python imports and model registration | Custom models and res.partner extension load | Registry loaded; all four expected models present | PASS |
| XML/security load | All manifest data and demo XML load | All data files loaded during upgrade; demo converter loaded 18 records | PASS |
| Static source and manifest validation | Valid Python/XML; all manifest paths and 6 ACL entries present | 13 Python files, 8 XML files parsed; paths and 6 ACL rows checked | PASS |
| Docker Compose validation | Valid current Compose configuration | docker compose config --quiet exited 0 | PASS |
| Repeated explicit demo load | No duplicates or changed demo records | Loader reported samples already exist; final counts remained 5/5 | PASS |
| Services | Odoo and PostgreSQL healthy | Both services healthy in docker compose ps | PASS |
| localhost:8069 | Health pass and HTTP 200 with session-aware redirects | Health status pass; db_server_status true; cookie-aware HTTP 200 | PASS |
| Current Odoo/PostgreSQL logs | No unexpected warning/error/critical/fatal/panic | 230 log lines inspected from current startup; zero matches | PASS |
| Browser test cleanup | Remove only two temporary bookings; retain five demo bookings and five rooms | IDs 221/222 removed; SQL and browser both confirmed five bookings; five rooms retained | PASS |
| Credential and backup exclusions | Local credential files and both new backups ignored by Git | All five paths confirmed by git check-ignore | PASS |
| Source credential scan | No known local credentials in Git-visible files | 31 Git-visible files scanned; no credential values found | PASS |
| Final logs after cleanup | No unexpected warning/error/critical/fatal/panic | 97 final Odoo/PostgreSQL log lines inspected; zero matches | PASS |

## Corrections and practical limits

The initial demo loader used Odoo's deprecated `kind` argument; it was removed for Odoo 19 compatibility. The browser driver initially clicked a table row rather than its field cell; its selector was corrected and the unfinished navigation checks then passed. A cookie-free HTTP probe cycled through database-selection redirects; a probe retaining Odoo's session cookies returned HTTP 200. These did not require changes to the business models, views, permissions or architecture.

Room availability is date-based. An occupied room rejects overlapping reservations and any second physical check-in, while a non-overlapping future reservation is allowed. Checkout/cancellation leaves a room reserved when another confirmed reservation remains. Cancellation is available from Confirmed; a checked-in stay must be checked out.

No unresolved Guest House defect was found in the tested scope. This stage verified an upgrade of the existing installation and the actual demo import; it did not repeat a fresh Ubuntu/Docker installation. No bakery setup or business work was performed.

## Reproduce

With the serving Odoo container stopped, run the module's regression suite:

```bash
docker compose stop odoo
docker compose run --rm --no-deps -T odoo odoo \
  -d thimo_guesthouse -u thimo_guesthouse --without-demo \
  --stop-after-init --no-http --max-cron-threads=0 \
  --test-enable --test-tags /thimo_guesthouse
```

Load the samples if needed, then run the detailed acceptance checks. The first loader requires an empty room list; repeat runs preserve an existing complete sample set. The acceptance script expects the initial sample set:

```bash
docker compose run --rm --no-deps -T odoo odoo shell \
  -d thimo_guesthouse --no-http --max-cron-threads=0 \
  < custom-addons/thimo_guesthouse/demo/load_demo.py
docker compose run --rm --no-deps -T odoo odoo shell \
  -d thimo_guesthouse --no-http --max-cron-threads=0 \
  < custom-addons/thimo_guesthouse/tests/verify_runtime.py
docker compose up -d --wait --wait-timeout 180
```
