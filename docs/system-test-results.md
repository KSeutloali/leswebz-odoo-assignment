# Final system testing and repository review

Verified on **5 October 2026**, using Odoo Community **19.0-20260926**, PostgreSQL
**16.15**, Docker Compose **2.32.4** and the actual running assignment databases.

All required environment, isolation, persistence and business workflows passed.
The repository handoff remains incomplete: **zero commits, zero tracked files,
and no configured remote**. Source is present locally, but a recipient cannot
clone this application yet. Do not describe the overall project as submission-ready.

## Method and current dataset

Guest House: **60 live ORM checks and 20 browser checks passed**. New temporary
bookings executed Draft → Confirmed → Checked In → Checked Out, with actual room
states checked at each step. Cancellation, overlaps, dates, totals, protected
fields and staff/public/portal permissions were exercised. All test writes were
rolled back. Views and button visibility were checked in an authenticated browser.

The live data currently has **3 room types, 5 rooms, 4 fictional guest Contacts
and 4 bookings**: Confirmed, Checked In, Checked Out and Cancelled. The original
draft and its guest were absent before this testing began. Four bookings exceed
the assignment minimum of three. The verifier now checks the approved minimum
and records the starting counts for rollback checks, rather than requiring five
unchanged sample bookings. No deleted business data was restored or overwritten.

Bakery: **68 read-only document/stock checks and 12 browser checks passed**.
This pass audited the existing completed workflow against real stock moves,
quants, linked receipts, POS deliveries, payments and posted session accounting.
No additional production, purchases or sales were created. The earlier actual
frontend sales and before/after measurements are recorded in
[bakery-test-results.md](bakery-test-results.md).

The first browser test attempt timed out because the test driver incorrectly
escaped a JavaScript selector. The selector was corrected and all 20 Guest House
browser checks then passed. No application defect was involved.

## Requirement results

| TEST | EXPECTED | ACTUAL | RESULT |
|---|---|---|---|
| Compose configuration | Valid | docker compose config --quiet exited 0 | PASS |
| PostgreSQL startup | Healthy and accepting connections | PostgreSQL 16.15 healthy; queries succeeded | PASS |
| Odoo startup | Healthy web server | Odoo 19.0-20260926 healthy; both registries loaded | PASS |
| localhost:8069 | HTTP 200 | Database selector HTTP 200; health status pass, db_server_status true | PASS |
| Custom addon mount | Host source mounted readonly at /mnt/extra-addons | Readonly bind confirmed; host/container manifest SHA256 equal | PASS |
| Guest House module loads | Installed module, working model imports and views | 19.0.1.2.0 installed; live ORM and browser checks passed | PASS |
| Developer Mode | Enabled in actual browser | odoo.debug = 1; developer menu rendered | PASS |
| Exactly two Odoo databases | ["thimo_guesthouse","vishanti_bakery"] | ["thimo_guesthouse","vishanti_bakery"] | PASS |
| Independent database identities | Different PostgreSQL OIDs and Odoo UUIDs | OIDs 16397 / 19646; UUIDs differ | PASS |
| Guest House isolation | Custom functionality only in guest-house database | Installed in house; uninstalled and no custom booking table in bakery | PASS |
| Bakery applications | stock, purchase, mrp, point_of_sale installed | All four installed; LGPL-3; no Enterprise modules | PASS |
| Safe container restart | down then up, retaining volumes | docker compose down; docker compose up -d --wait --wait-timeout 180; both healthy | PASS |
| Databases reopen after restart | Both present and usable | Both PostgreSQL identities retained; both browser logins succeeded | PASS |
| Guest House records persist | Identical counts and content | All 4 sampled tables unchanged; 3 types / 5 rooms / 4 bookings / 4 guest Contacts | PASS |
| Bakery configuration and history persist | Identical products, BoM, manufacturing, purchase, stock and POS data | All 19 sampled bakery tables unchanged; 1 MO / 1 PO / 3 transfers / 2 POS orders / 10 Done moves | PASS |
| Named volumes persist | Same names, creation times and mountpoints | Both named volumes retained unchanged | PASS |
| Odoo filestores persist | Identical files and contents | House 17 files; bakery 471 files; both full-tree SHA256 checksums unchanged | PASS |
| Mounts persist | Same mounted volumes and binds | Mount sets identical after sorting by destination | PASS |
| Unexpected startup/test log errors | 0 | 0 | PASS |
| Guest House end-to-end | ["draft/available","confirmed/reserved","checked_in/occupied","checked_out/available"] | ["draft/available","confirmed/reserved","checked_in/occupied","checked_out/available"] | PASS |
| Croissant manufacturing to POS | Consume only required ingredients, produce 10, sell 1, finish with 9 | Done MO consumed Flour 1 / Sugar 0.20 / Yeast 0.05 kg; output 10; paid POS delivered 1; stock 9 | PASS |
| Coca-Cola purchase to POS | Receive 24, sell 2, finish with 22 | Confirmed P00001; WH/IN/00001 Done 24; paid POS delivered 2; stock 22 | PASS |
| Local secret exclusion | Sensitive files ignored and untracked; no known secrets in source | Ignore checks passed; known credential scan and common token/private-key patterns clear | PASS |
| Repository contains reproducible source | Project source committed to Git | No commits, no tracked files; source exists only as untracked workspace files | FAIL |
| Clone and fresh-install reproduction | Published URL and verified clean clone setup | No remote configured; README contains explicit REPOSITORY_URL placeholder | NOT VERIFIED |
| Backup restoration | Actual restore exercise | Not performed during this final system pass | NOT VERIFIED |

The log scan used all Odoo and PostgreSQL logs since the restart, looking for
ERROR, CRITICAL, FATAL, Traceback and WARNING; there were zero matching lines.
Expected ACL denials from negative tests appeared as INFO in the one-off test
process, and its registry loaded successfully. Odoo serving logs showed both
database registries loading and successful backend requests.

## Persistence evidence

Executed sequentially:

```bash
docker compose down
docker compose up -d --wait --wait-timeout 180
docker compose ps
```

No volume deletion command was run. Before/after checksums cover every column of
every row in the 23 business tables below, ordered by record ID. **All 23 matched
exactly**, proving content persistence rather than merely checking database names.

| DATABASE | TABLE | ROWS BEFORE / AFTER | CHECKSUM MATCH |
|---|---|---|---|
| thimo_guesthouse | thimo_guesthouse_room_type | 3 / 3 | PASS |
| thimo_guesthouse | thimo_guesthouse_room | 5 / 5 | PASS |
| thimo_guesthouse | thimo_guesthouse_booking | 4 / 4 | PASS |
| thimo_guesthouse | res_partner | 9 / 9 | PASS |
| vishanti_bakery | product_template | 7 / 7 | PASS |
| vishanti_bakery | product_product | 7 / 7 | PASS |
| vishanti_bakery | res_partner | 6 / 6 | PASS |
| vishanti_bakery | mrp_bom | 1 / 1 | PASS |
| vishanti_bakery | mrp_bom_line | 3 / 3 | PASS |
| vishanti_bakery | mrp_production | 1 / 1 | PASS |
| vishanti_bakery | purchase_order | 1 / 1 | PASS |
| vishanti_bakery | purchase_order_line | 1 / 1 | PASS |
| vishanti_bakery | stock_picking | 3 / 3 | PASS |
| vishanti_bakery | stock_move | 10 / 10 | PASS |
| vishanti_bakery | stock_move_line | 10 / 10 | PASS |
| vishanti_bakery | stock_quant | 15 / 15 | PASS |
| vishanti_bakery | pos_config | 1 / 1 | PASS |
| vishanti_bakery | pos_session | 1 / 1 | PASS |
| vishanti_bakery | pos_order | 2 / 2 | PASS |
| vishanti_bakery | pos_order_line | 2 / 2 | PASS |
| vishanti_bakery | pos_payment | 2 / 2 | PASS |
| vishanti_bakery | account_move | 2 / 2 | PASS |
| vishanti_bakery | account_move_line | 4 / 4 | PASS |

Both volumes retained their names, creation timestamps and mountpoints:
`leswebz-odoo-assignment_postgres_data` at `/var/lib/postgresql/data`,
and `leswebz-odoo-assignment_odoo_data` at `/var/lib/odoo`.
These are Docker-managed storage, not files in the Git repository.
The read-only `./custom-addons` bind mount retained the same source and destination.
Its manifest checksum matched the host source. Mount ordering in Docker's JSON
changed; the actual mount sets were identical.

Full filestore checksums were identical before/after: **17 house files and 471
bakery files**. Each checksum includes every relative filename, file size and
file content hash. Raw checksum evidence is in
[system-test-evidence.json](system-test-evidence.json).

The database identities remained `thimo_guesthouse` OID **16397** and
`vishanti_bakery` OID **19646**, with different Odoo UUIDs. Both were reopened
through browser logins after restart. A computer reboot was not performed;
the executed persistence test was the requested container down/up cycle.

## End-to-end quantities

| CHAIN | ACTUAL EVIDENCE | RESULT |
|---|---|---|
| Booking → Confirm | confirmed / reserved | PASS |
| Confirmed → Check In | checked_in / occupied | PASS |
| Checked In → Check Out | checked_out / available | PASS |
| Confirmed → Cancel | cancelled / available; replacement on same dates accepted | PASS |
| Croissant ingredients | Done MO consumes 1 kg Flour, 0.20 kg Sugar, 0.05 kg Yeast only | PASS |
| Croissant finished stock | WH/MO/00003 adds 10 Units; WH/POS/00001 delivers 1; final 9 | PASS |
| Coca-Cola incoming stock | P00001 received by WH/IN/00001; 24 Units Vendors → Stock | PASS |
| Coca-Cola outgoing stock | WH/POS/00002 delivers 2 Units Stock → Customers; final 22 | PASS |
| Actual POS payment | LSL 15 + LSL 36 Cash; both orders Posted | PASS |
| Session closure | Vishanti Bakery/00001 Closed & Posted; cash 51; difference 0 | PASS |

Final ingredient stock: **Flour 9 kg; Sugar 1.80 kg; Yeast 0.45 kg**.
Finished goods have no inventory adjustment moves; their balances result from
manufacture/receipt and POS deliveries. The movement ledger and all individual
expected/actual checks are retained in the JSON evidence.

## README command review

README has the requested title and all 14 requested sections. All **12 Bash
blocks passed `bash -n`**. Template copying and mode 600 were exercised safely
in a temporary directory; no live credential file was overwritten. Referenced
source files, service names, addon name and target databases were checked.

| COMMAND / PROCEDURE | VALIDATION | STATUS |
|---|---|---|
| git clone REPOSITORY_URL | Shell syntax valid; actual URL/committed project absent | NOT VERIFIED |
| cd leswebz-odoo-assignment | Correct project directory name; depends on clone succeeding | NOT VERIFIED after clone |
| cp example files; chmod 600 .env | Source paths exist; copies and permissions tested in /tmp | PASS |
| Editing local passwords | Blank .env example and master placeholder verified; distinct local credentials checked without printing values | PASS |
| docker compose config --quiet | Executed, exit 0 | PASS |
| docker compose up -d --wait --wait-timeout 180 | Executed; both services healthy | PASS |
| docker compose ps | Executed before and after restart | PASS |
| docker compose down | Executed; both named volumes and data retained | PASS |
| docker compose stop / stop odoo | Services/options match actual Compose project; exercised during earlier development; not rerun in this pass | PASS command review |
| Odoo install -i / upgrade -u commands | Used during implementation; paths/modules/databases verified; Odoo server CLI flags inspected; not repeated over live data | PASS command review |
| Guest House demo loader | Earlier successful initial load; existing partial set intentionally not reloaded | PASS prior execution; not rerun |
| Bakery setup script | Earlier successful setup/idempotence tests; existing completed data not reset | PASS prior execution; not rerun |
| Guest House runtime verification | Current run: 60 PASS, transaction rolled back | PASS |
| Bakery audit | Current run: 68 PASS, read-only | PASS |
| docker compose logs --tail=100 odoo db | Executed; startup/registry/backend logs reviewed | PASS |
| docker compose logs -f odoo | Actual service/option valid; following logs is interactive and was not left running | PASS command review |
| curl health URL | Executed; pass and db_server_status true | PASS |
| down -v warning | Documented as destructive; intentionally never executed | PASS documentation |

A fresh-clone, fresh-volume recreation is **NOT VERIFIED**. The README states
this limitation and uses an explicit URL placeholder; it does not invent a
remote or claim a clone passed. Backup restoration is also **NOT VERIFIED** in
this final pass.

## Git and security findings

| SEVERITY | FINDING | ACTION / STATUS |
|---|---|---|
| BLOCKER | Repository submission has no committed project: zero tracked files and no commits | Commit reviewed source before handoff; no Git metadata changed by this review |
| HIGH | No remote or published URL; recipient cannot clone; clean installation not verified | Supply/configure the actual repository URL, publish source and test a fresh clone |
| MEDIUM | None identified beyond the handoff gaps above | No application/security defect requiring architecture changes found |
| LOW | Local Odoo config mode 644 allows other local users to read it | Needed for current container readability; ignored, localhost-only setup; restrict appropriately if shared |
| LOW, fixed | Runtime verifier assumed exactly five unchanged booking samples | Check assignment minimum, varied dates/statuses and original counts after rollback; 60 checks passed |
| LOW | Original draft/guest and empty next POS session are absent compared with earlier reports | Current data recorded; no restoration required for assignment workflows |

Security checks:

- `.env`, local Odoo config, admin credential JSON, all backups/receipt images,
  logs and Python caches are ignored. No sensitive file is tracked.
- Local environment and admin credential files are mode 600. Example passwords
  are blank/placeholders; real local PostgreSQL/master/admin credentials are
  nonempty and distinct. No credential values are included in this report.
- Known local credential strings and common private-key/API-token patterns were
  scanned across Git-visible files with zero findings. Password-related source
  assignments are environment-variable/psql references, not hardcoded secrets.
- Backup dumps and filestore archives were preserved under ignored `backups/`.
  PostgreSQL/Odoo generated data lives in named volumes, outside the repository.
- No unexpected project `dockercompose`, temporary or local-volume directories
  were present. Test helpers/browser profile reside in `/tmp`.
- The only IDE file is `.vscode/extensions.json`; it contains one extension
  recommendation and no credentials or private settings.
- All 15 source Python files parsed and all 8 XML files parsed; manifest-referenced
  files exist. Actual imports and views were additionally exercised in Odoo.
- Odoo's database role is not a PostgreSQL superuser. PostgreSQL has no host
  mapping; Odoo is bound to 127.0.0.1.

## Files changed and outstanding work

Changed `README.md` and
`custom-addons/thimo_guesthouse/tests/verify_runtime.py`.
Added `docs/system-test-results.md` and `docs/system-test-evidence.json`.
No architecture or business feature changes, bakery custom addon, persistent
test bookings, data deletions, commits or remote publication were performed.

**No mandatory runtime workflow remains failing or unverified.** Submission is
blocked by repository handoff, not application behaviour. Commit the reviewed
source, publish/configure its remote URL, replace the README clone placeholder
and verify installation from that clone. Restore/reboot testing are additional
unverified checks, not failures of the requested container persistence test.
