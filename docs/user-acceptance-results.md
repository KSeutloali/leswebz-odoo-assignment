# User acceptance and release assessment

Assessed on **5 October 2026** against the original assignment only:
**51 PASS / 0 FAIL / 0 NOT VERIFIED** across **51 items**.

**READY FOR SUBMISSION.** The README installation and fresh setup checks passed
against an actual GitHub clone. No mandatory requirement remains incomplete.

## Verification basis

The working deployment received read-only checks: Compose validation, service and
HTTP health, live database queries, Guest House registry/model/form loading,
the 68-check bakery audit, Git/secret checks and README syntax/link review.
Its databases were not reset, upgraded or restarted, and no new persistent
business transactions were created there. No volumes were removed.

The private GitHub source was cloned at **8b1313e** and installed using fresh
credentials, a separate Compose project, separate volumes and localhost:18069.
This clean installation passed **60 Guest House ORM checks**, **20 Guest House
browser checks**, **35 bakery setup checks**, actual frontend POS sales and
**68 bakery audit checks**. New setup/sale records were confined to that
validation deployment, which was stopped afterward with its volumes retained.

The earlier executed persistence restart and bakery backend browser checks are
reused explicitly. Original Guest House type, room and booking checksums were
identical before/after the isolated verification. The original bakery retained
its posted documents and stock balances. No behavioural PASS is based only on
source presence.

Evidence:
[clean-install report](release-verification-results.md),
[clean-install expected/actual JSON](release-verification-evidence.json),
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
| Developer Mode available | PASS | Fresh browser verification: odoo.debug = 1 and developer menu rendered; 20 house browser checks passed. |
| custom-addons exists | PASS | Host custom-addons/thimo_guesthouse exists; container sees the manifest at /mnt/extra-addons. |
| Git repository exists | PASS | Repository has two commits, HEAD 8b1313e and a private GitHub origin; actual HTTPS clone succeeded. |
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
| Guest supported | PASS | Five current res.partner guest Contacts; guest field exists in the live registry. Fresh demo also created five fictional guests. |
| Room supported | PASS | Five live room records; room model loaded. |
| Room Type supported | PASS | Standard, Deluxe and Family records; room-type model loaded. |
| Rate supported | PASS | Live defaults LSL 450 / 650 / 900; booking rate, nights and total verified in the 60-check live suite. |
| Booking supported | PASS | Six current records; live booking model and form view load. Fresh demo created five samples. |
| At least 5 rooms | PASS | Fresh actual count: 5. |
| At least 3 bookings | PASS | Fresh actual count on the working deployment: 6. |
| Booking confirmation works | PASS | Clean-install TEST 2: confirmed / reserved; temporary writes rolled back. |
| Check-in works | PASS | Clean-install TEST 3: checked_in / occupied. |
| Room becomes occupied | PASS | Clean-install check-in observed occupied; working room 201 also occupied. |
| Check-out works | PASS | Clean-install TEST 4: checked_out / available. |
| Room becomes available | PASS | Clean-install checkout observed available with no remaining reservation; working room 101 available. |
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
| README commands verified | PASS | Actual GitHub clone and documented database/module/setup/POS/audit steps passed on clean storage; 12 Bash blocks parse and local links resolve. Validation used an isolated project and port; earlier upgrade/restart commands have actual test evidence. |
| No secrets committed | PASS | Private files ignored and untracked. Known-credential and common-token/private-key scans clear in working source, index and committed history. |
| Setup reproducible | PASS | Cloned source at 8b1313e installed from templates with fresh passwords and volumes: two databases, custom Guest House, four standard bakery apps, manufacture, receipt and paid POS deliveries verified. |

## Final non-destructive release check

| CHECK | ACTUAL | RESULT |
|---|---|---|
| docker compose config --quiet | Exit 0; avoids printing resolved credentials | PASS |
| docker compose ps | db and odoo healthy; Odoo published only at 127.0.0.1:8069 | PASS |
| Git status | HEAD 8b1313e; actual private origin; only final documentation/evidence changes pending the suggested commit; sensitive paths ignored | PASS |
| Module loads | Three custom models registered; partner guest field present; actual booking form architecture loads | PASS |
| Databases accessible | Both queried through PostgreSQL; both Odoo registries successfully used | PASS |
| Mandatory workflows verified | Fresh house lifecycle, constraints and security; fresh manufacturing, purchasing, POS frontend sales and posted stock audit | PASS |
| README accuracy | Actual clone URL, current versions, services, counts, quantities, limits and credential handling reviewed; clean install verified | PASS |
| Secrets absent from submission source | Known credentials scan clear; private inputs/backups ignored; no sensitive file tracked | PASS scoped review |
| Recent service logs | Working services have no recent warnings/errors. Fresh installation recovered from a shutdown-interrupted standard cleanup job; explicit rerun passed, with no subsequent unexpected errors | PASS |

## Release handoff

No mandatory item remains incomplete. Suggested final commit:
`docs: finalize acceptance and verify clean installation`.
Optional tag after that commit: `v1.0.0`. This review did not commit, push or tag.
A backup restore exercise and full computer reboot are outside the original
mandatory checklist and are not claimed as tested here.

The working Guest House currently has **5 rooms / 6 bookings / 5 guest Contacts**.
Bakery stock remains **Flour 9 kg / Sugar 1.80 kg / Yeast 0.45 kg /
Croissant 9 Units / Coca-Cola 22 Units**.

## Submission contents

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
