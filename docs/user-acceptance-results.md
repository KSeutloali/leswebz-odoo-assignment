# User acceptance and release assessment

Assessed on **5 October 2026** against the original assignment only:
**49 PASS / 0 FAIL / 2 NOT VERIFIED** across **51 items**.

**RELEASE READINESS NOT DECLARED.** The two incomplete delivery checks are the
complete README installation command sequence and fresh setup reproduction.
There is no verified mandatory business-workflow failure.

## Verification basis

This final pass was non-destructive: Compose validation, service health, HTTP
health, live database queries, Guest House registry/model/form loading, the
68-check read-only bakery audit, Git/secret checks and README syntax/link review.
No database reset, volume removal, restart, module upgrade or new persistent
demo transaction was performed.

Earlier actual tests are reused explicitly where indicated: **60 Guest House
live ORM checks**, **20 Guest House browser checks**, **12 bakery browser checks**
and the executed persistence restart. This pass confirmed that the Guest House
room types, rooms and booking table checksums still match that tested dataset.
The bakery audit passed all 68 checks again against current documents and quants.
No PASS below is based solely on source presence for a required behaviour.

Evidence:
[system report](system-test-results.md),
[system expected/actual JSON](system-test-evidence.json),
[Guest House results](guesthouse-test-results.md),
[bakery results](bakery-test-results.md),
[bakery before/after JSON](bakery-evidence.json).

## Environment

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Odoo runs locally | PASS | Fresh health request returned pass at localhost:8069; Odoo service healthy. |
| PostgreSQL runs locally | PASS | db service healthy; fresh queries and both Odoo registries connected successfully. |
| Docker Compose works | PASS | Fresh docker compose config --quiet exited 0; docker compose ps succeeded. |
| Developer Mode available | PASS | Earlier actual browser verification: odoo.debug = 1 and developer menu rendered; 20 house browser checks passed. |
| custom-addons exists | PASS | Host custom-addons/thimo_guesthouse exists; container sees the manifest at /mnt/extra-addons. |
| Git repository exists | PASS | git rev-parse returned true; initial commit 21d7f46 now exists. No remote is configured. |
| Persistence works after restart | PASS | Earlier actual down/up test: all 23 sampled tables and both filestores unchanged; both volumes retained. Not repeated in this non-destructive pass. |

## Databases

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| thimo_guesthouse exists | PASS | Fresh query: PostgreSQL OID 16397; current registry and booking form load. |
| vishanti_bakery exists | PASS | Fresh query: PostgreSQL OID 19646; fresh read-only audit connects and passes. |
| Databases remain separate | PASS | Different OIDs and UUIDs. House addon uninstalled in bakery; no bakery booking table. |

## Guest House

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Guest supported | PASS | Four current fictional res.partner guest Contacts; is_guest field exists in the live registry. |
| Room supported | PASS | Five live room records; room model loaded. |
| Room Type supported | PASS | Standard, Deluxe and Family records; room-type model loaded. |
| Rate supported | PASS | Live defaults LSL 450 / 650 / 900; booking rate, nights and total verified in the 60-check live suite. |
| Booking supported | PASS | Four current records; live booking model and form view load. |
| At least 5 rooms | PASS | Fresh actual count: 5. |
| At least 3 bookings | PASS | Fresh actual count: 4. |
| Booking confirmation works | PASS | Prior live TEST 2: confirmed / reserved; temporary writes rolled back. |
| Check-in works | PASS | Prior live TEST 3: checked_in / occupied. |
| Room becomes occupied | PASS | Prior live check-in observed occupied; current room 201 also occupied. |
| Check-out works | PASS | Prior live TEST 4: checked_out / available. |
| Room becomes available | PASS | Prior live checkout observed available with no remaining reservation; current room 101 available. |
| Booking statuses update correctly | PASS | Live suite observed draft → confirmed → checked_in → checked_out, plus confirmed → cancelled; invalid transitions rejected. |

## Bakery applications

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Inventory | PASS | Fresh audit: stock installed, Community LGPL-3. |
| Purchase | PASS | Fresh audit: purchase installed, Community LGPL-3. |
| Manufacturing | PASS | Fresh audit: mrp installed, Community LGPL-3. |
| Point of Sale | PASS | Fresh audit: point_of_sale installed; register, paid orders and posted session present. |

## Croissant

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Flour exists | PASS | Fresh audit: tracked VBAK-FLOUR, kg; 9 kg on hand. |
| Sugar exists | PASS | Fresh audit: tracked VBAK-SUGAR, kg; 1.80 kg on hand. |
| Yeast exists | PASS | Fresh audit: tracked VBAK-YEAST, kg; 0.45 kg on hand. |
| Croissant exists | PASS | Fresh audit: tracked VBAK-CROISSANT, Units; POS enabled; 9 on hand. |
| BoM contains only Flour, Sugar and Yeast | PASS | Fresh audit: exactly these three lines, 1 / 0.20 / 0.05 kg per 10 croissants. |
| Manufacturing works | PASS | Fresh audit: WH/MO/00003 Done; quantity produced 10; three component moves and finished move Done. |
| Flour decreases | PASS | Actual MO consumes 1 kg; recorded before/after 10 → 9 kg; current moves and quant agree. |
| Sugar decreases | PASS | Actual MO consumes 0.20 kg; recorded 2 → 1.80 kg; current moves and quant agree. |
| Yeast decreases | PASS | Actual MO consumes 0.05 kg; recorded 0.50 → 0.45 kg; current moves and quant agree. |
| Croissant stock increases | PASS | Done finished move adds 10 Units, Production → WH/Stock; recorded 0 → 10. |
| Croissant can be sold through POS | PASS | Actual frontend sale previously completed; fresh audit confirms one unit, LSL 15 paid Cash, order Posted. |
| POS sale decreases Croissant stock | PASS | Linked WH/POS/00001 Done: one unit Stock → Customers; 10 → 9; no finished-stock adjustment. |

## Coca-Cola

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Vendor exists | PASS | Fresh audit: fictional Demo Mountain Beverages, supplier enabled. |
| Coca-Cola 1L exists | PASS | Fresh audit: tracked VBAK-COLA-1L, Units, purchasable and POS enabled. |
| Purchase Order works | PASS | Fresh audit: P00001 confirmed, 24 Units at LSL 12, total LSL 288. |
| Receipt works | PASS | Fresh audit: linked WH/IN/00001 Done; received 24. |
| Receipt increases inventory | PASS | Actual Done move adds 24 Units Vendors → Stock; recorded 0 → 24, whereas PO confirmation left on-hand unchanged. |
| Coca-Cola can be sold through POS | PASS | Actual frontend sale previously completed; fresh audit confirms two bottles, LSL 36 paid Cash, order Posted. |
| POS sale decreases inventory | PASS | Linked WH/POS/00002 Done: two Units Stock → Customers; 24 → 22; current stock/ledger agree. |

## Delivery

| ITEM | RESULT | ACTUAL EVIDENCE |
|---|---|---|
| Source/custom module present | PASS | Manifest, package, models, security, XML views, sequence, demo and tests present; registry imports and form load. |
| README present | PASS | README.md exists with the requested title and all 14 sections. |
| README commands verified | NOT VERIFIED | All 12 Bash blocks parse and local paths resolve; runtime/setup commands have evidence, but git clone REPOSITORY_URL remains a placeholder and has not run. |
| No secrets committed | PASS | Private files ignored and untracked. Known-credential and common-token/private-key scans clear in working source, index and committed history. |
| Setup reproducible | NOT VERIFIED | Source, pinned images, templates and setup scripts exist and were used locally; a complete fresh-copy/clone installation has not been exercised. |

## Final non-destructive release check

| CHECK | ACTUAL | RESULT |
|---|---|---|
| docker compose config --quiet | Exit 0; avoids printing resolved credentials | PASS |
| docker compose ps | db and odoo healthy; Odoo published only at 127.0.0.1:8069 | PASS |
| Git status | Initial commit 21d7f46 contains 41 source files; final README, acceptance report and assessor-answer updates remain uncommitted; no remote; sensitive paths ignored | PASS inspection; final documentation handoff pending |
| Module loads | Three custom models registered; partner guest field present; actual booking form architecture loads | PASS |
| Databases accessible | Both queried through PostgreSQL; both Odoo registries successfully used | PASS |
| Mandatory workflows verified | Prior live house state tests; current posted bakery document/stock audit | PASS |
| README accuracy | Current versions, services, quantities, limits and credential handling accurate; clone placeholder disclosed | PASS accuracy; full installation NOT VERIFIED |
| Secrets absent from submission source | Known credentials scan clear; private inputs/backups ignored; no sensitive file tracked | PASS scoped review |
| Recent service logs | Successful health requests and normal PostgreSQL checkpoints; no unexpected errors observed | PASS |

The Git repository **exists**, and the initial source commit was created during
this review, so that original checkbox passes. A hosted remote, tag, backup restore test and computer
reboot are not independent mandatory items in the original assignment. The
current README nevertheless starts with a clone placeholder, and there is no
verified clean installation, so the two delivery checks remain open.

## Remaining release work

1. Commit the final README/report updates. Initial source commit **21d7f46** was
   created during this review; this agent did not change the Git index or create
   that commit. A checkout now contains the application source.
2. Supply an actual clone source and replace README's `REPOSITORY_URL` placeholder.
   A hosted remote can provide this; a supplied local Git repository is another
   valid handoff.
3. Exercise the documented installation using fresh local credentials and
   separate clean storage, preserving the existing two working databases.
   Verify both databases, module installation, bakery setup and workflows there.
4. Record that result, then reassess the two NOT VERIFIED items.

These are delivery gaps; no architecture redesign or additional business feature
is required. The working Guest House currently has **5 rooms / 4 bookings**.
Bakery stock remains **Flour 9 kg / Sugar 1.80 kg / Yeast 0.45 kg /
Croissant 9 Units / Coca-Cola 22 Units**.

## Submission contents after verification

Include:

- `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`.
- `config/init-odoo.sh` and `config/odoo.conf.example`.
- `custom-addons/`, including the complete `thimo_guesthouse` module.
- `scripts/setup_bakery.py` and `scripts/verify_bakery.py`.
- `docs/`, including acceptance results, test evidence, demonstration plan and
  assessor answers.

`.vscode/extensions.json` is optional, contains an extension recommendation and
has no credentials.

Exclude `.env`, `config/odoo.conf`, `config/database-admins.json`,
`backups/`, database dumps, receipt images containing access codes, runtime logs,
Python caches and Docker volume contents. Passwords must be supplied locally by
the recipient. Keep the working databases and volumes in place.

See the [14-minute demonstration plan](live-demonstration-plan.md) and
[assessor questions and answers](assessor-questions.md).
