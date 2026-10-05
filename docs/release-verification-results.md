# Clean installation and final release verification

Verified on **5 October 2026** from private GitHub source commit **8b1313e**.
All **51 mandatory acceptance items pass**. See the
[acceptance checklist](user-acceptance-results.md) and
[expected/actual evidence](release-verification-evidence.json).

## Isolation and preservation

An actual HTTPS clone of
`https://github.com/KSeutloali/leswebz-odoo-assignment.git` was installed with
fresh local passwords. The validation checkout is inside ignored `backups/`.
Its Compose project was `leswebz-release-validation`, with separate named
`leswebz-release-validation_postgres_data` and
`leswebz-release-validation_odoo_data` volumes. A local override published
Odoo at `127.0.0.1:18069`; application source and pinned images were unchanged.

The working deployment continued serving `localhost:8069`. No working database
was reset, upgraded or restarted, and no new business transaction was created
there. No volume was removed. The validation services were stopped after testing,
with their databases, containers and volumes retained.

The original Guest House tables had identical before/after checksums:

| TABLE | ROWS | BEFORE AND AFTER MD5 |
|---|---:|---|
| Room Types | 3 | c443448721b1db84f2d4df1defe6ec02 |
| Rooms | 5 | 96913f5592569056b99f2c92574e1afd |
| Bookings | 6 | dd37db76891758fc96575c0f71b05b5e |

Checksums use `md5(jsonb_agg(to_jsonb(t) ORDER BY id)::text)`.
The working deployment has five guest Contacts, six bookings and five rooms.
Its bakery retains nine croissants and 22 Coca-Cola bottles, with the completed
manufacturing, purchasing, receipt and two posted POS sales.

## Executed installation

The README sequence was exercised: clone; copy and fill local config templates;
validate Compose; start and wait for healthy services; create both databases
through Odoo's database-management HTTP endpoint; install Guest House; load its
demo; install standard `stock,purchase,mrp,point_of_sale`; run bakery setup;
restart the validation Odoo service; complete both sales in the actual POS
frontend; reconcile cash; run the read-only bakery audit.

Database creation used English, Lesotho and no standard demo data. The two
databases have distinct identities: OID **16389** for `thimo_guesthouse` and
**19638** for `vishanti_bakery`. The initialized `odoo` PostgreSQL role has
`CREATEDB` and is **not** a superuser. House tables/module remain isolated from
bakery. The fresh bakery installed 65 official Community modules including
dependencies; the four assignment applications required no custom bakery addon
or additional Sales Management installation.

For isolation, validation commands used this prefix in the cloned directory:

```text
docker compose -p leswebz-release-validation \
  -f docker-compose.yml -f compose.release-check.yml
```

The override changed only the published web port. The README's normal deployment
remains one Odoo server and two databases at localhost:8069. Earlier actual
module-upgrade and safe restart tests remain recorded in the system report;
they were not repeated against the working databases during this release check.

## Test results

| TEST | EXPECTED | ACTUAL | RESULT |
|---|---|---|---|
| Actual GitHub clone | Complete tracked source at the tested commit | Clone succeeded at 8b1313e | PASS |
| Fresh Compose startup | PostgreSQL/Odoo healthy on separate storage | Both healthy; PostgreSQL has no published host port | PASS |
| Fresh Guest House install | Python, models, ACL, sequence and XML load | Installation exited 0; browser views loaded | PASS |
| Fresh Guest House demo | 3 types, exactly 5 rooms, 5 fictional guests and 5 valid bookings | All counts and relationships verified | PASS |
| Guest House ORM suite | Lifecycle, room state, dates, totals, overlap, cancellation and security checks pass | 60 PASS, 0 FAIL; temporary test writes rolled back | PASS |
| Guest House browser suite | Menus, Developer Mode, forms and valid buttons work | 20 PASS, 0 FAIL; no new saved booking | PASS |
| Fresh bakery setup | Standard apps, correct BoM, production, purchase and receipt | 35 PASS, 0 FAIL | PASS |
| Manufacturing ingredient movement | Flour 10→9 kg; Sugar 2→1.80 kg; Yeast 0.50→0.45 kg | Exact before/after values and Done moves | PASS |
| Manufacturing finished movement | Croissant 0→10 | 10 produced, finished move Done | PASS |
| Coca-Cola purchase/receipt | PO confirmation leaves stock 0; receipt increases to 24 | 0→0→24; receipt Done | PASS |
| Actual Croissant frontend sale | 1 unit, LSL 15 Cash; stock 10→9 | Payment Successful; stock 9 immediately | PASS |
| Actual Coca-Cola frontend sale | 2 units, LSL 36 Cash; stock 24→22 | Payment Successful; stock 22 immediately | PASS |
| POS cash/session reconciliation | Opening 0, closing 51, difference 0, orders/accounting posted | Closed & Posted; 51 cash, zero difference; balanced entry | PASS |
| Fresh bakery document/stock audit | Completed documents, payments, deliveries and quants agree | 68 PASS, 0 FAIL | PASS |
| Original services and data | Healthy on 8069; existing business data retained | Health, table checksums, bakery audit and separate volumes verified | PASS |
| Git/README/secret review | Accurate commands and links; no real credentials in source/index/history | Review passed; final documentation changes ready for the suggested commit | PASS |

Full individual EXPECTED/ACTUAL/PASS rows are retained in the JSON evidence.
Prior actual down/up persistence verification remains in
[system results](system-test-results.md); no volumes were removed in either test.

The final review scanned **43 Git-visible files**, **41 index blobs** and
**44 historical blobs across two commits**, checking both working and validation
passwords plus common token/private-key patterns: **zero findings**. All private
inputs and backups remain ignored and untracked. All **14 README sections**,
**12 Bash blocks** and **37 local documentation links** passed review.

## Log review and limits

The working deployment had no recent unexpected warnings or errors. During fresh
database creation, cron briefly skipped a database while module installation
was pending. Stopping validation Odoo at 14:39 UTC interrupted standard
auto-vacuum, producing closed-cursor errors after the shutdown message. This
cleanup job was explicitly rerun afterward and finished successfully. Following
the validation service's restart, health requests, POS operations and database
queries succeeded without further unexpected application errors.

PostgreSQL's initial local-socket trust warning is from the official image's
initialization; its port is not exposed. The first clone attempt encountered a
missing local GitHub credential-helper executable, which was restored without
altering credentials. Docker Desktop could not bind-mount the first checkout
under `/tmp`, so the new checkout was moved into the Docker-shared, ignored
`backups/` directory. Neither issue required an application/source change.

Backup restoration and a full computer reboot were not performed in this release
pass. They are not outstanding mandatory acceptance items. Repository access is
private; an assessor cloning it must be given access. Final documentation/evidence
changes have not been committed or tagged by this review.

**READY FOR SUBMISSION.**
