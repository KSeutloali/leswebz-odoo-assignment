# Live demonstration plan — 14 minutes

This is a plan for the assessed presentation. **No new bookings, manufacturing
orders, purchase orders, receipts or sales were created while preparing it.**
During the live presentation, create new documents and retain them as evidence;
keep all existing completed demo history.

Assessment priorities: Environment/engineering **20%**, Guest House **25%**,
Bakery **35%**, Quality/README/demo **20%**. Bakery receives **7½ minutes** of the
14-minute presentation because it carries the highest weighting.

## Preparation before the clock starts

- Resolve the two release checks in [user acceptance results](user-acceptance-results.md).
  Until then, describe delivery verification as pending.
- Log into the two databases in separate browser profiles. Keep the terminal at
  the project root. Preload Guest House Bookings/Rooms/Room Types, bakery Stock,
  BoM, Manufacturing Orders, Purchase Orders and POS Dashboard.
- Confirm room **101** is Available and has no booking conflicting with the
  chosen dates. Use existing fictional **Demo Guest Bravo** and a two-night stay.
- Read actual stock immediately before presenting. The current baseline is
  Flour **9 kg**, Sugar **1.80 kg**, Yeast **0.45 kg**, Croissant **9 Units**,
  Coca-Cola **22 Units**. Record it on the worksheet below. If transactions have
  occurred since this document, use the newly observed BEFORE values.
- Use one new MO for **10 Croissants**, one new PO for **24 Coca-Cola bottles**,
  and separate POS orders for **1 Croissant** and **2 Coca-Cola bottles**.
- Leave the existing Done MO, validated receipt and Posted sales unchanged.
  Do not reset stock, use finished-stock adjustments or rerun setup to stage a demo.
- Keep actual credentials off screen. Show example config, never local secret
  files or full resolved Compose output. Use `docker compose config --quiet`.

## 1. Environment — 0:00–1:00

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| Terminal, project root | Run docker compose config --quiet, then docker compose ps | Validation succeeds; db and odoo healthy; Odoo at 127.0.0.1:8069 | “Compose starts Odoo Community and PostgreSQL as two local services.” | Actual service status and pinned images in docker-compose.yml |
| IDE project tree and Compose volumes | Show custom-addons, config examples and the two named volume declarations | Custom module source exists; database and filestore have persistent storage | “Named volumes retain database and attachment data when containers are recreated. Custom source stays in this host directory.” | postgres_data, odoo_data and the earlier restart checksum results |

Use these verified commands:

```bash
docker compose config --quiet
docker compose ps
```

Show the earlier persistence test report; a restart is already verified and need
not interrupt this short presentation.

## 2. Databases — 1:00–1:30

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| Database selector, then the two logged-in browser profiles | Show thimo_guesthouse and vishanti_bakery; open each profile | Guest House in one database; standard bakery apps in the other | “One Odoo server hosts two separate databases. Each has its own users, installed apps and records.” | Selector names; different PostgreSQL OIDs/UUIDs in the test report; house addon absent from bakery |

Selector: http://localhost:8069/web/database/selector.
Do not create or delete databases during the presentation.

## 3. Guest House — 1:30–4:30

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| Guest House → Rooms; Configuration → Room Types; Guests; Bookings | Show 5 rooms, all 3 types, a fictional Contact and the existing 4 bookings | Requirements of at least 5 rooms / 3 bookings met; types and guest relationships visible | “Guests reuse Odoo Contacts. Room types supply capacity and an LSL nightly rate.” | Standard 450, Deluxe 650, Family 900; four varied booking statuses |
| Bookings → New | Select Demo Guest Bravo, room 101 and a two-night stay with valid dates; Save | Draft; rate LSL 450, 2 nights, total LSL 900; generated reference | “The booking copies the room's default rate and calculates nights and total.” | Saved reference, dates, rate, nights and total |
| Booking form, then Rooms | Click Confirm; show room 101 | Booking Confirmed; room Reserved | “Confirmation reserves this room. Active overlapping stays are rejected.” | Booking status and room status |
| Same booking, then Rooms | Click Check In; show room 101 | Booking Checked In; room Occupied | “Check-in records occupancy and updates both records.” | Checked In status and Occupied room |
| Same booking, then Rooms | Click Check Out; show room 101 | Booking Checked Out; room Available when no other reservation remains | “Checkout releases the room while retaining the booking history.” | Checked Out status and Available room |

Use dates based on the actual presentation day. Save the generated reference;
do not edit dates or rates after confirmation. The new checked-out booking remains
in history. Cancellation and overlap rejection are already verified; point to
those acceptance checks if asked, keeping the live demonstration within time.

## 4. Croissant — 4:30–8:30

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| Inventory → Reporting → Stock | Record Flour, Sugar, Yeast and Croissant on hand BEFORE | Current baseline: 9 kg / 1.80 kg / 0.45 kg / 9 Units | “These are the actual balances immediately before this new production.” | On-hand quantities, not forecast quantities; worksheet |
| Manufacturing → Products → Bills of Materials | Open VBAK-CROISSANT-10 | Output 10; exactly Flour 1 kg, Sugar 0.20 kg and Yeast 0.05 kg | “This BoM contains precisely the three ingredients required by the assignment.” | Three component rows, quantities and output |
| Manufacturing → Operations → Manufacturing Orders → New | Select Croissant, quantity 10 and the existing BoM; Save, Confirm, then Produce All (or Produce if displayed) | New MO Done, 10 produced, exact component consumption | “Completing production consumes the components and posts ten finished croissants into stock.” | New MO reference; Components; quantity produced; Done stock moves |
| Inventory → Reporting → Stock | Refresh and compare all four products AFTER manufacturing | Flour 8 kg; Sugar 1.60 kg; Yeast 0.40 kg; Croissant 19 Units, using the baseline above | “The changes match the BoM: minus 1, 0.20 and 0.05 kilograms, plus ten finished units.” | Refreshed on hand and the new MO's stock moves |
| Point of Sale → Dashboard → Vishanti Bakery | Open register using its displayed/correct opening cash; sell 1 Croissant; Payment → Cash → Validate | Successful paid order for LSL 15 | “The finished product is sold through standard Odoo POS.” | Paid receipt and order reference |
| Inventory → Reporting → Stock, Croissant | Refresh after payment | Croissant 19 → 18 immediately | “This register updates stock at payment. Its outgoing delivery removes one croissant.” | On hand 18; linked Done POS delivery |

The current Odoo 19 standard manufacturing view includes **Confirm**, **Produce**
and **Produce All**. If a consumption/production dialog appears, confirm output
10 and consumption 1 / 0.20 / 0.05 kg, complete the dialog and verify **Done**.
Do not proceed on a draft or partly produced MO. Use the new document reference;
the existing `WH/MO/00003` is historical evidence and is already Done.

Keep this POS session open for the Coca-Cola sale. After the Croissant receipt,
choose **New Order** before the next product.

## 5. Coca-Cola 1L — 8:30–12:00

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| Purchase → Orders → Purchase Orders → New | Choose Demo Mountain Beverages; add 24 Coca-Cola 1L at LSL 12; Save | RFQ for LSL 288; supplier/product linked | “Purchase records what we order from the vendor.” | Vendor, quantity, unit price and total |
| Purchase Order; Inventory → Reporting → Stock | Confirm the PO and read Coca-Cola on hand | PO confirmed and receipt created; physical on hand remains 22 before receipt | “Confirming a purchase order does not mean the goods have physically arrived.” | PO status, Receipt smart button and unchanged on hand |
| PO's Receipt smart button, or Inventory → Operations → Receipts | Open its new receipt; enter/verify received quantity 24 and Validate | Receipt Done; Coca-Cola on hand 22 → 46 | “The validated receipt moves twenty-four bottles from Vendors into Stock.” | Receipt reference, Done state, received quantity and refreshed stock |
| Existing open POS session | New Order; sell 2 Coca-Cola 1L; Payment → Cash → Validate | Successful LSL 36 paid order | “The received bottles can now be sold through POS.” | Receipt/order: 2 × LSL 18 = LSL 36 |
| Inventory → Reporting → Stock, Coca-Cola | Refresh after payment | Coca-Cola 46 → 44 | “The sale's outgoing delivery removes two bottles.” | On hand 44 and the linked Done POS delivery |

Use the new PO's own receipt; existing `P00001` and `WH/IN/00001` are completed
history. Receipt references are generated, so record the new ones rather than
assuming their numbers.

## 6. Engineering quality — 12:00–14:00

| SCREEN | ACTION | EXPECTED RESULT | WHAT I SHOULD SAY | EVIDENCE TO POINT TO |
|---|---|---|---|---|
| POS → Close Register; Sessions | Reconcile the actual counted cash and close this new session | Orders Posted; session Closed & Posted; difference 0 | “The session reconciles cash and posts the sales. Stock already moved at payment.” | Two payments totalling LSL 51, closing difference and linked accounting entry |
| IDE; terminal Git status; README and acceptance report | Show complete module, Compose, .gitignore, example config and README; run git status --short | Required source visible; secrets excluded; current delivery state disclosed | “The custom module is limited to Guest House; bakery uses standard apps. Templates and scripts support recreation, and the report records what has actually been verified.” | Module tree; standard app names; README commands; ignore rules and release checklist |

Opening cash is **O**, the amount actually entered when opening this register.
For these two exact Cash sales, counted closing cash should be **O + LSL 51**,
assuming no other cash movements. If opening is LSL 51, closing is **LSL 102**.
A fresh register opened at zero closes at LSL 51. Never assume the existing
register should open at zero: the previous completed session closed with LSL 51.

If the initial commit/clean installation is still pending, say so plainly; do not
claim a verified release. Do not display `.env`, local `odoo.conf` or
`database-admins.json`. Show `.env.example` and `odoo.conf.example` instead.

## Quantity worksheet

These are **planned** results for the new presentation transactions, using the
currently verified baseline. They have not been executed during release preparation.

| PRODUCT | LIVE BEFORE | AFTER NEW MO | AFTER NEW RECEIPT | AFTER ITS POS SALE |
|---|---|---|---|---|
| Flour kg | 9 | 8 | 8 | 8 |
| Sugar kg | 1.80 | 1.60 | 1.60 | 1.60 |
| Yeast kg | 0.45 | 0.40 | 0.40 | 0.40 |
| Croissant Units | 9 | 19 | 19 | 18 |
| Coca-Cola Units | 22 | 22 | 46 | 44 |

Record the observed times and generated booking / MO / PO / receipt / POS
references. Show actual refreshed stock around each action. Do not label an old
historical snapshot as the current BEFORE balance.

The initial bakery audit expects 9 croissants and 22 bottles. Successful new
presentation transactions change those expected balances; an unchanged baseline
audit will then report differences. Preserve the new history and reconcile its
moves rather than resetting stock to make the old audit pass.

If an action fails, keep the error visible, check the document/state/quantity,
and use [assessor answers](assessor-questions.md) and actual prior evidence to
explain the verified behaviour. A historical walkthrough supports evidence but
should be described as history rather than a newly executed action.
