# Odoo Local Development & Business Implementation

## Architecture

Ubuntu hosts one Odoo Community server and PostgreSQL through Docker Compose.
Verified versions: **Odoo 19.0-20260926**, **PostgreSQL 16.15**, Compose **2.32.4**.
Official `odoo:19.0` and `postgres:16` images are pinned by digest.

| Component | Service / storage |
|---|---|
| Web server | `odoo`, published at `127.0.0.1:8069` |
| PostgreSQL | `db`, internal port 5432; no published host port |
| Database persistence | `leswebz-odoo-assignment_postgres_data` → `/var/lib/postgresql/data` |
| Filestore and sessions | `leswebz-odoo-assignment_odoo_data` → `/var/lib/odoo` |
| Custom source | Host `./custom-addons` → `/mnt/extra-addons`, read-only |
| Local configuration | `config/odoo.conf` → `/etc/odoo/odoo.conf`, read-only |

The separate Odoo databases are `thimo_guesthouse` and `vishanti_bakery`.
Each has its own users, applications, records and filestore directory beneath
`/var/lib/odoo/filestore/<database-name>`. PostgreSQL also retains its maintenance
database and templates.

## Prerequisites

- Ubuntu, Git, a text editor and browser.
- Docker Engine or Docker Desktop running, with Docker Compose v2 and permission
  to run Docker commands.
- Port 8069 available; internet access for the first image download.

## Project Structure

```text
leswebz-odoo-assignment/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── .vscode/extensions.json
├── config/
│   ├── init-odoo.sh
│   ├── odoo.conf.example
│   ├── odoo.conf              # local, ignored
│   └── database-admins.json   # optional local credential record, ignored
├── custom-addons/
│   ├── .gitkeep
│   └── thimo_guesthouse/      # models, views, security, sequence, demo, tests
├── scripts/
│   ├── setup_bakery.py
│   └── verify_bakery.py
├── docs/                     # assessment guides and actual test evidence
├── .env                      # local, ignored
└── backups/                  # local, ignored
```

## Installation

The source repository is private; GitHub access is required to clone it.
A fresh-clone installation has not been verified.

```bash
git clone https://github.com/KSeutloali/leswebz-odoo-assignment.git leswebz-odoo-assignment
cd leswebz-odoo-assignment
cp .env.example .env
cp config/odoo.conf.example config/odoo.conf
chmod 600 .env
```

Edit `.env` before starting. Supply different local values for
`POSTGRES_PASSWORD` and `ODOO_DB_PASSWORD`; single-quote values containing
Compose interpolation characters such as `$`. In `config/odoo.conf`, replace
`REPLACE_WITH_LOCAL_MASTER_PASSWORD` with a third local password. The container's
Odoo user must be able to read this configuration file.

```bash
docker compose config --quiet
docker compose up -d --wait --wait-timeout 180
docker compose ps
```

Complete Database Setup, Guest House Module and Bakery below. Compose starts
servers; database creation and application setup are explicit steps. The
PostgreSQL initialization script creates the non-superuser `odoo` role with
`CREATEDB` permission only when its data volume is first initialized.

## Starting

From the project directory, with Docker running:

```bash
docker compose up -d --wait --wait-timeout 180
docker compose ps
```

Containers use `restart: unless-stopped`. Docker must start after a computer
reboot; explicitly stopped containers need the start command above.

## Stopping

```bash
docker compose stop
```

This keeps containers and volumes. `docker compose down` removes containers and
the network while retaining named volumes.

## Restarting

```bash
docker compose down
docker compose up -d --wait --wait-timeout 180
```

**`docker compose down -v` removes persistent volumes and destroys their database
and filestore contents. Do not use it during normal operation.**

The safe down/up sequence passed: all 23 sampled business tables and both
filestores retained identical checksums, and both services became healthy.

## Accessing Odoo

Open http://localhost:8069. Select a database at
http://localhost:8069/web/database/selector, or use:

- http://localhost:8069/web/login?db=thimo_guesthouse
- http://localhost:8069/web/login?db=vishanti_bakery

Use separate browser profiles for simultaneous sessions. Enable Developer Mode
from Settings or add `?debug=1` to a backend URL. Its browser flag and developer
menu were verified after restart.

## Database Setup

On a **fresh installation**, use http://localhost:8069/web/database/manager to
create exactly `thimo_guesthouse` and `vishanti_bakery`. Enter the local master
password, use English and Lesotho, leave standard demonstration data disabled,
and choose an administrator login and a distinct password for each database.
Both databases already exist in the current workspace; do not recreate them.

The **database master password** (`admin_passwd`) authorizes server-wide database
operations. The **Odoo administrator login/password** authenticates a user within
one database. The **PostgreSQL passwords** in `.env` connect the services and
are not browser login details. Optional ignored `config/database-admins.json`
records local logins; Odoo does not read it.

The `dbfilter` allows only the two assignment names. Check their separate
PostgreSQL identities:

```bash
docker compose exec -T db psql -U postgres -d postgres -c \
  "SELECT oid, datname FROM pg_database WHERE datname IN ('thimo_guesthouse', 'vishanti_bakery') ORDER BY datname;"
```

Two distinct OIDs and different Odoo `database.uuid` values were verified.
The Guest House module and tables exist only in `thimo_guesthouse`.

Before important changes, pause writes and take a database-manager ZIP backup
including the filestore. Keep backups in ignored `backups/` and copy important
ones to another device. Restore with matching Odoo and addon versions. A database
dump alone excludes filestore attachments. Restore testing was not performed in
this final system pass.

## Guest House Module

`custom-addons/thimo_guesthouse` provides Room Types (capacity, description,
default nightly rate), Rooms (number, type, state), Guests (standard
`res.partner` Contacts), Rates (LSL snapshots on bookings) and Bookings
(reference, guest, room, dates, nights, total, status).

Navigation: **Guest House → Bookings / Rooms / Guests / Configuration → Room Types**.
Receptionists manage bookings and guest Contacts; Managers also configure rooms
and types. Public, portal and unassigned internal users cannot read bookings.

For a fresh guest-house database:

```bash
docker compose stop odoo
docker compose run --rm --no-deps -T odoo odoo \
  -d thimo_guesthouse -i thimo_guesthouse --without-demo \
  --stop-after-init --no-http --max-cron-threads=0
docker compose run --rm --no-deps -T odoo odoo shell \
  -d thimo_guesthouse --no-http --max-cron-threads=0 \
  < custom-addons/thimo_guesthouse/demo/load_demo.py
docker compose up -d --wait --wait-timeout 180
```

The loader uses Odoo demo XML to create three types, five rooms, five fictional
Contacts and five bookings. Standard rooms 101/102 cost LSL 450 nightly; Deluxe
201/202 cost LSL 650; Family 301 costs LSL 900. Dates are relative to first load.
Complete samples are preserved on repeat loads; partial/deleted samples require
review rather than automatic replacement. **The current live dataset has five
rooms, four guests and four bookings** after an original draft and its guest
were removed.

Workflow: **Draft → Confirmed → Checked In → Checked Out**.
Room states: **Available → Reserved → Occupied → Available**.
Confirmed bookings can be cancelled. Checkout/cancellation keeps a room Reserved
when another confirmed stay remains. Maintenance prevents reservation.
Room status summarizes occupancy; date-specific availability uses booking dates.

Checkout must be after check-in. Nights equal the date difference; total equals
nights × rate. Confirmed/checked-in stays cannot overlap; adjacent stays are
allowed because checkout is exclusive. Cancelled bookings do not block dates.
Critical fields are frozen after Draft; invalid server transitions are rejected.

Restart Odoo after Python changes. After model, XML or data changes, upgrade:

```bash
docker compose stop odoo
docker compose run --rm --no-deps -T odoo odoo \
  -d thimo_guesthouse -u thimo_guesthouse --without-demo \
  --stop-after-init --no-http --max-cron-threads=0
docker compose up -d --wait --wait-timeout 180
```

## Bakery

`vishanti_bakery` uses standard Community Inventory (`stock`), Purchase
(`purchase`), Manufacturing (`mrp`) and Point of Sale (`point_of_sale`), with
official dependencies. There is no custom bakery addon. Sales Management was
already installed in this workspace before bakery setup.

For a fresh bakery database:

```bash
docker compose stop odoo
docker compose run --rm --no-deps -T odoo odoo \
  -d vishanti_bakery -i stock,purchase,mrp,point_of_sale --without-demo \
  --stop-after-init --no-http --max-cron-threads=0
docker compose run --rm --no-deps -T odoo odoo shell \
  -d vishanti_bakery --no-http --max-cron-threads=0 \
  < scripts/setup_bakery.py
docker compose up -d --wait --wait-timeout 180
```

Setup uses standard models/actions: component opening stock, a completed
manufacturing order, confirmed PO, validated receipt and a Cash POS register.
It refuses other databases and preserves completed setup on repeat runs.

**Croissant:** the BoM produces 10 Units using **only** 1 kg flour, 0.20 kg sugar
and 0.05 kg yeast. Manufacturing consumes these ingredients and adds 10
croissants. Selling one through POS at LSL 15 cash reduces stock from 10 to 9.

**Coca-Cola 1L:** purchase 24 Units from fictional Demo Mountain Beverages at
LSL 12 each. PO confirmation creates an expected receipt; validating it adds 24
bottles to physical stock. Selling two through POS at LSL 18 each reduces stock
from 24 to 22.

The completed demonstration has one Done MO, one confirmed PO, one Done receipt,
two Posted POS orders and one Closed & Posted session: LSL 51 cash, zero difference.
Final stock: Flour 9 kg, Sugar 1.80 kg, Yeast 0.45 kg, Croissant 9 Units, Coca-Cola
22 Units. Actual Done moves and payments were audited after restart.

## Demo Procedure

1. Log into `thimo_guesthouse`; show the five rooms and their types.
2. Create a Draft booking for an available room and fictional guest on
   non-overlapping future dates. Show its rate, nights and total.
3. Click Confirm, Check In and Check Out, inspecting the room after each action.
   Demonstrate Cancel on a separate confirmed booking.
4. Log into `vishanti_bakery`. Show BoM `VBAK-CROISSANT-10`, Done MO
   `WH/MO/00003`, PO `P00001`, receipt `WH/IN/00001`, POS orders, their linked
   deliveries and current stock/movement history.
5. On a **fresh bakery setup**, open Vishanti Bakery in POS with zero cash, sell
   1 Croissant and 2 Coca-Cola in separate Cash orders, and Validate each.
   Close with LSL 51 counted cash. Further sales change the existing baseline.

Guest House checks roll back all temporary test writes:

```bash
docker compose run --rm --no-deps -T odoo odoo shell \
  -d thimo_guesthouse --no-http --max-cron-threads=0 \
  < custom-addons/thimo_guesthouse/tests/verify_runtime.py
```

Audit the completed initial bakery demonstration without changing records:

```bash
docker compose run --rm --no-deps -T odoo odoo shell \
  -d vishanti_bakery --no-http --max-cron-threads=0 \
  < scripts/verify_bakery.py
```

The bakery audit expects the initial two-sale balances; additional transactions
require reviewing expected values. See [system results](docs/system-test-results.md),
[Guest House results](docs/guesthouse-test-results.md),
[bakery results](docs/bakery-test-results.md) and the
[bakery assessment guide](docs/bakery-assessment-guide.md). Earlier reports
describe their original test datasets; the system report records the current state.

For assessment, use the [acceptance checklist](docs/user-acceptance-results.md),
[14-minute live demonstration plan](docs/live-demonstration-plan.md) and
[assessor questions](docs/assessor-questions.md). The plan records expected new
transaction quantities separately from the existing completed demonstration.

## Troubleshooting

```bash
docker compose config --quiet
docker compose ps
docker compose logs --tail=100 odoo db
docker compose logs -f odoo
curl --fail 'http://localhost:8069/web/health?db_server_status=1'
```

Actual service names are `odoo` and `db`. An unhealthy database blocks startup.
Create local configuration and fill password variables before starting. Changing
`.env` does not change existing PostgreSQL role passwords; initialization runs
only on an empty data volume. A missing Guest House menu in the bakery is
expected. In the guest-house database, check installation and user permissions.
Edit addon source on the host because its container mount is read-only.

## Security

Local `.env`, `config/odoo.conf`, `config/database-admins.json`, `backups/`,
logs and Python caches are ignored. Examples contain placeholders only. Supply
passwords locally; do not copy credentials into source or documentation. Local
environment/login files have mode 600. Odoo config is readable for the container
user and must remain ignored; restrict access appropriately on a shared machine.

The review found no known local credentials or common private-key/API-token
patterns in Git-visible files and committed source. No sensitive file is tracked.
The source repository is hosted on GitHub. Fresh-clone installation verification
remains pending.

PostgreSQL is not published, and Odoo binds to localhost. Avoid sharing full
`docker compose config` output because it resolves passwords; validate using
`docker compose config --quiet`. Keep database backups outside Git.
