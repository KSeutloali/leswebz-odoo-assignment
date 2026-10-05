# Bakery implementation and functional test results

Verified on 5 October 2026 using **Odoo Community 19.0-20260926**, PostgreSQL 16.15 and database **vishanti_bakery**. The standard-module installation, 35 setup checks, 68 document/stock audit checks, 12 backend browser checks and both complete cash-paid frontend sales passed. Detailed expected/actual results follow. Initial failed manufacturing setup attempts were rolled back and corrected before the successful demonstration; they are recorded below.

No custom bakery addon or custom model was created. Only `stock`, `purchase`, `mrp` and `point_of_sale` were selected for installation. Odoo enabled their official dependencies and auto-install integrations, including `purchase_stock`, `stock_account`, `mrp_account` and `pos_mrp`. All four requested apps have LGPL-3 licences; no OEEL-1 Enterprise module is installed. Sales Management was already installed before this work (its module update timestamp predates the bakery installation); it was not selected as an additional bakery app. The Guest House addon remains uninstalled in this database.

Exactly five active business products were created. Odoo automatically created its standard Tips and Down Payment products during app installation; both unused products were archived. All five goods track inventory by quantity. Raw materials use kg; Croissant and Coca-Cola 1L use Units. Components are purchasable, not sold in POS; Croissant is manufactured and sold; Coca-Cola is purchased and resold. Demo product tax lines are empty so the arithmetic uses the stated LSL prices.

| Product | Unit | Cost LSL/unit | Sale LSL/unit | Buy | POS |
|---|---|---|---|---|---|
| Flour | kg | 20 | — | Yes | No |
| Sugar | kg | 30 | — | Yes | No |
| Yeast | kg | 100 | — | Yes | No |
| Croissant | Units | 3.10 | 15 | No | Yes |
| Coca-Cola 1L | Units | 12 | 18 | Yes | Yes |

Vendor: **Demo Mountain Beverages**, fictional, with no private personal contact information. A standard supplier price of LSL 12 is linked to Coca-Cola 1L.

## Measured production quantities

BoM **VBAK-CROISSANT-10** produces **10 Croissants** using only **1 kg Flour, 0.20 kg Sugar and 0.05 kg Yeast**. Type Manufacture, strict consumption, no other ingredient or by-product. Opening quantities were established through standard inventory adjustments for the three components only.

| Product | BEFORE MRP | AFTER MRP | DIFFERENCE | Unit |
|---|---|---|---|---|
| Flour | 10 | 9 | −1 | kg |
| Sugar | 2 | 1.80 | −0.20 | kg |
| Yeast | 0.50 | 0.45 | −0.05 | kg |
| Croissant | 0 | 10 | +10 | Units |

The changes resulted from completing **WH/MO/00003**. Its three component moves and one finished-product move are Done. The two failed earlier setup attempts persisted no products, quants or orders; references can have gaps because Odoo sequences are not rolled back.

## Measured receipt and POS quantities

| Stage | BEFORE | Movement | AFTER | Cause |
|---|---|---|---|---|
| Coca-Cola PO confirmation | 0 | 0 | 0 | P00001 confirmed; creates expected receipt |
| Coca-Cola receipt validation | 0 | +24 | 24 | WH/IN/00001 Done |
| Croissant POS sale | 10 | −1 | 9 | Vishanti Bakery - 000001 → WH/POS/00001 |
| Coca-Cola POS sale | 24 | −2 | 22 | Vishanti Bakery - 000002 → WH/POS/00002 |

**PO confirmation and goods receipt are separate events.** Confirming a PO creates the incoming receipt with expected quantities. It does not by itself add the goods to physical on-hand stock; validating the receipt does. The measured values here were 0 after confirmation and 24 after receipt validation. [Odoo's purchase workflow](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase/manage_deals/rfq.html).

Both sales were entered and paid in the actual Chrome POS frontend. The Croissant receipt showed Payment Successful, 1 unit and LSL 15 Cash. The Coca-Cola receipt showed Payment Successful, 2 units and LSL 36 Cash. Reads immediately after each payment verified the stock decrease before session closing. The session uses real-time stock updates, so each paid order generated its completed outgoing delivery immediately.

Session **Vishanti Bakery/00001** is **Closed & Posted**: opening cash 0, cash payments 51, counted closing cash 51, difference 0. Its balanced accounting entry **POSS/2026/10/0001** is Posted. Both orders are Posted (`state=done`). Odoo automatically prepared an empty next session in Opening Control with the previous cash balance; it has no sale or stock movement.

Final stock: **Flour 9 kg; Sugar 1.80 kg; Yeast 0.45 kg; Croissant 9 Units; Coca-Cola 1L 22 Units.** All reserved quantities are zero. Every figure agrees with the sum of Done stock movements. Croissant and Coca-Cola have **zero inventory adjustments**; their final balances were not manually forced.

## Required assignment tests

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Croissant 1: Flour exists | One tracked Flour product | One tracked Flour product | PASS |
| Croissant 2: Sugar exists | One tracked Sugar product | One tracked Sugar product | PASS |
| Croissant 3: Yeast exists | One tracked Yeast product | One tracked Yeast product | PASS |
| Croissant 4: Croissant exists | One tracked, POS-enabled Croissant product | One tracked, POS-enabled Croissant product | PASS |
| Croissant 5: BoM ingredients ONLY | Flour / Sugar / Yeast | Flour / Sugar / Yeast; three lines | PASS |
| Croissant 6: MO confirms/processes | Confirmed then Done; produce 10 | Confirmed then Done; produced 10 | PASS |
| Croissant 7: Flour decreases | 10 → 9 kg; −1 kg | 10 → 9 kg; −1 kg | PASS |
| Croissant 8: Sugar decreases | 2 → 1.80 kg; −0.20 kg | 2 → 1.80 kg; −0.20 kg | PASS |
| Croissant 9: Yeast decreases | 0.50 → 0.45 kg; −0.05 kg | 0.50 → 0.45 kg; −0.05 kg | PASS |
| Croissant 10: Finished stock increases | 0 → 10 Units from MO | 0 → 10 Units; MO finished move Done | PASS |
| Croissant 11: POS sale succeeds | 1 unit; LSL 15 cash paid | Payment Successful; paid 15; order posted | PASS |
| Croissant 12: POS decreases stock | 10 → 9 Units; −1 | 10 → 9; linked WH/POS/00001 Done | PASS |
| Coca-Cola 1: Vendor exists | Fictional supplier | Demo Mountain Beverages; supplier rank 1 | PASS |
| Coca-Cola 2: Product exists | Tracked Units; Buy and POS enabled | Tracked Units; Buy and POS enabled | PASS |
| Coca-Cola 3: RFQ/PO works | RFQ with 24 units at LSL 12 | P00001 created as Draft; 24 × 12 = 288 | PASS |
| Coca-Cola 4: PO confirms | Purchase state; physical stock remains 0 | Purchase state; stock 0 before and after | PASS |
| Coca-Cola 5: Receipt exists | One incoming receipt | WH/IN/00001 created | PASS |
| Coca-Cola 6: Receipt validates | Done; receive 24 units | Done; received 24 units | PASS |
| Coca-Cola 7: Receipt increases stock | 0 → 24; +24 | 0 → 24; Vendors → WH/Stock move Done | PASS |
| Coca-Cola 8: Appears in POS | Coca-Cola tile available | Coca-Cola 1L tile visible and selectable | PASS |
| Coca-Cola 9: POS sale succeeds | 2 units; LSL 36 cash paid | Payment Successful; paid 36; order posted | PASS |
| Coca-Cola 10: POS decreases stock | 24 → 22; −2 | 24 → 22; linked WH/POS/00002 Done | PASS |

## Setup/action checks

These checks were executed around the actual standard model actions, recording stock immediately before and after manufacturing, PO confirmation and receipt validation.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Required Community applications installed | mrp / point_of_sale / purchase / stock | mrp / point_of_sale / purchase / stock | PASS |
| Bakery currency | LSL | LSL | PASS |
| Fiscal country | Lesotho | Lesotho | PASS |
| Flour exists and tracks inventory | true | true | PASS |
| Sugar exists and tracks inventory | true | true | PASS |
| Yeast exists and tracks inventory | true | true | PASS |
| Croissant exists and tracks inventory | true | true | PASS |
| Coca-Cola 1L exists and tracks inventory | true | true | PASS |
| Active business products | 5 | 5 | PASS |
| Fictional Coca-Cola vendor | true | true | PASS |
| Croissant BoM ingredients ONLY | Flour / Sugar / Yeast | Flour / Sugar / Yeast | PASS |
| BoM batch size | 10 | 10 | PASS |
| BoM quantities in kg | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | PASS |
| Starting stock recorded | {"Flour":10,"Sugar":2,"Yeast":0.5,"Croissant":0,"Coca-Cola 1L":0} | {"Flour":10,"Sugar":2,"Yeast":0.5,"Croissant":0,"Coca-Cola 1L":0} | PASS |
| Manufacturing Order confirms | confirmed | confirmed | PASS |
| Manufacturing Order completes | done | done | PASS |
| Stock after MRP: Flour | 9 | 9 | PASS |
| Stock after MRP: Sugar | 1.8 | 1.8 | PASS |
| Stock after MRP: Yeast | 0.45 | 0.45 | PASS |
| Stock after MRP: Croissant | 10 | 10 | PASS |
| Stock after MRP: Coca-Cola 1L | 0 | 0 | PASS |
| MRP owns ingredient and finished stock moves | true | true | PASS |
| RFQ created | draft | draft | PASS |
| Purchase Order confirmed | purchase | purchase | PASS |
| PO confirmation does not change physical stock | 0 | 0 | PASS |
| PO creates receipt | 1 | 1 | PASS |
| Receipt pending before validation | true | true | PASS |
| Receipt validated | done | done | PASS |
| Receipt increases stock by 24 | 24 | 24 | PASS |
| Coca-Cola stock after receipt | 24 | 24 | PASS |
| PO received quantity | 24 | 24 | PASS |
| POS session created | true | true | PASS |
| POS has only Cash payment | Cash | Cash | PASS |
| POS updates stock in real time | false | false | PASS |
| Only required sale products in POS | Coca-Cola 1L / Croissant | Coca-Cola 1L / Croissant | PASS |

## Read-only audit of posted documents and stock

The standalone audit reads the final Odoo records and actual quants, verifies linked payments and transfers, and reconstructs on-hand stock from the movement ledger.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Four required applications installed | installed / installed / installed / installed | installed / installed / installed / installed | PASS |
| Required modules use Community licences | LGPL-3 / LGPL-3 / LGPL-3 / LGPL-3 | LGPL-3 / LGPL-3 / LGPL-3 / LGPL-3 | PASS |
| No Enterprise modules installed | 0 | 0 | PASS |
| Guest House module not installed in bakery | uninstalled | uninstalled | PASS |
| Currency is LSL | LSL | LSL | PASS |
| Flour exists | 1 | 1 | PASS |
| Flour tracks quantities | consu / true / none | consu / true / none | PASS |
| Sugar exists | 1 | 1 | PASS |
| Sugar tracks quantities | consu / true / none | consu / true / none | PASS |
| Yeast exists | 1 | 1 | PASS |
| Yeast tracks quantities | consu / true / none | consu / true / none | PASS |
| Croissant exists | 1 | 1 | PASS |
| Croissant tracks quantities | consu / true / none | consu / true / none | PASS |
| Coca-Cola 1L exists | 1 | 1 | PASS |
| Coca-Cola 1L tracks quantities | consu / true / none | consu / true / none | PASS |
| Exactly five active business products | 5 | 5 | PASS |
| Ingredient units | kg / kg / kg | kg / kg / kg | PASS |
| Finished product units | Units / Units | Units / Units | PASS |
| POS availability | Coca-Cola 1L / Croissant | Coca-Cola 1L / Croissant | PASS |
| Ingredient purchasing/selling settings | [true,false] / [true,false] / [true,false] | [true,false] / [true,false] / [true,false] | PASS |
| Croissant manufactured and sellable | false / true | false / true | PASS |
| Coca-Cola purchasable and sellable | true / true | true / true | PASS |
| Exactly one Croissant BoM | 1 | 1 | PASS |
| BoM contains ONLY Flour, Sugar and Yeast | Flour / Sugar / Yeast | Flour / Sugar / Yeast | PASS |
| BoM quantities per 10 croissants | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | PASS |
| BoM output and consumption policy | 10 / normal / strict | 10 / normal / strict | PASS |
| Manufacturing Order complete | 1 / done / 10 | 1 / done / 10 | PASS |
| MRP consumed only required ingredients | Flour / Sugar / Yeast | Flour / Sugar / Yeast | PASS |
| Actual MRP consumption | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | {"Flour":1,"Sugar":0.2,"Yeast":0.05} | PASS |
| Ingredient stock moves Done | done / done / done | done / done / done | PASS |
| Finished Croissant stock move | 1 / done / 10 | 1 / done / 10 | PASS |
| Fictional vendor exists | 1 / Demo Mountain Beverages / true | 1 / Demo Mountain Beverages / true | PASS |
| Purchase Order confirmed | 1 / purchase | 1 / purchase | PASS |
| PO ordered and received quantities | 24 / 24 | 24 / 24 | PASS |
| Coca-Cola purchasing price and total | 12 / 288 | 12 / 288 | PASS |
| Purchase receipt exists and Done | 1 / done | 1 / done | PASS |
| Receipt stock movement | 24 / supplier / internal | 24 / supplier / internal | PASS |
| Receipt linked to Purchase Order | 1 | 1 | PASS |
| Two completed POS orders | done / done | done / done | PASS |
| Croissant POS sale succeeds | 1 | 1 | PASS |
| Croissant POS quantity sold | 1 | 1 | PASS |
| Croissant POS payment completed | 15 / 15 / Cash | 15 / 15 / Cash | PASS |
| Croissant POS owns a Done delivery | 1 / done | 1 / done | PASS |
| Croissant POS stock movement | 1 / internal / customer | 1 / internal / customer | PASS |
| Coca-Cola 1L POS sale succeeds | 1 | 1 | PASS |
| Coca-Cola 1L POS quantity sold | 2 | 2 | PASS |
| Coca-Cola 1L POS payment completed | 36 / 36 / Cash | 36 / 36 / Cash | PASS |
| Coca-Cola 1L POS owns a Done delivery | 1 / done | 1 / done | PASS |
| Coca-Cola 1L POS stock movement | 2 / internal / customer | 2 / internal / customer | PASS |
| Demo POS session Closed and Posted | 1 / closed / posted | 1 / closed / posted | PASS |
| POS opening/closing cash and difference | 0 / 51 / 0 | 0 / 51 / 0 | PASS |
| POS paid cash total | 51 | 51 | PASS |
| POS accounting entry balances | 0 | 0 | PASS |
| Final stock: Flour | 9 | 9 | PASS |
| Flour stock agrees with posted movement ledger | 9 | 9 | PASS |
| Flour has only initial stock adjustment | 1 | 1 | PASS |
| Final stock: Sugar | 1.8 | 1.8 | PASS |
| Sugar stock agrees with posted movement ledger | 1.8 | 1.8 | PASS |
| Sugar has only initial stock adjustment | 1 | 1 | PASS |
| Final stock: Yeast | 0.45 | 0.45 | PASS |
| Yeast stock agrees with posted movement ledger | 0.45 | 0.45 | PASS |
| Yeast has only initial stock adjustment | 1 | 1 | PASS |
| Final stock: Croissant | 9 | 9 | PASS |
| Croissant stock agrees with posted movement ledger | 9 | 9 | PASS |
| Croissant has no inventory adjustments | 0 | 0 | PASS |
| Final stock: Coca-Cola 1L | 22 | 22 | PASS |
| Coca-Cola 1L stock agrees with posted movement ledger | 22 | 22 | PASS |
| Coca-Cola 1L has no inventory adjustments | 0 | 0 | PASS |

## Browser verification

All four app screens, the inventory report/history, BoM, MO, PO, receipt, two POS orders and the closed session were opened in headless Chrome without an Odoo error dialog.

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Inventory product screen | true | true | PASS |
| Inventory Stock screen | true | true | PASS |
| BoM browser ingredient rows | 3 | 3 | PASS |
| BoM browser only required ingredients | true | true | PASS |
| Manufacturing browser Done state | true | true | PASS |
| Purchase browser vendor and product | true | true | PASS |
| Inventory browser validated receipt | true | true | PASS |
| Inventory movement history | true | true | PASS |
| POS dashboard loads configuration | true | true | PASS |
| POS orders screen | 2 | 2 | PASS |
| POS closed session screen | true | true | PASS |
| Backend uncaught JavaScript exceptions | 0 | 0 | PASS |

POS stock arrays below mean **before / after / difference**:

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| POS frontend product tiles | Croissant and Coca-Cola 1L | Croissant and Coca-Cola 1L | PASS |
| POS opening control | Zero opening cash; register opens | Zero opening cash; opening popup completed | PASS |
| Croissant UI cash payment | 1 unit; LSL 15; Payment Successful | 1 unit; LSL 15; Payment Successful | PASS |
| Croissant stock immediately after POS | 10 / 9 / -1 | 10 / 9 / -1 | PASS |
| Coca-Cola UI cash payment | 2 units; LSL 36; Payment Successful | 2 units; LSL 36; Payment Successful | PASS |
| Coca-Cola stock immediately after POS | 24 / 22 / -2 | 24 / 22 / -2 | PASS |
| Both POS orders paid before session close | paid / paid | paid / paid | PASS |
| Cash session closing through UI | LSL 51 counted; zero difference; Closed & Posted | LSL 51 counted; zero difference; Closed & Posted | PASS |

## Foundation and isolation checks

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Standard-app install | CLI exits 0; required apps loaded | CLI exited 0; 78 installed standard modules loaded | PASS |
| Install log | No warning/error/critical/fatal/panic | 362 lines checked; zero severity matches | PASS |
| Workflow/server logs | No warning/error/critical/fatal/panic | 478 lines checked; zero severity matches | PASS |
| Idempotent setup rerun | One MO, one PO; no reset or duplicate stock | One MO, one PO; stocks remained 9/1.80/0.45/9/22 | PASS |
| Guest House records preserved | Original room types, rooms, bookings and guest Contacts unchanged | All four before/after record checksums identical | PASS |
| Compose configuration | Valid | docker compose config --quiet exited 0 | PASS |
| Odoo/PostgreSQL health | Health pass; database server available | status pass; db_server_status true | PASS |
| Script/evidence validation | Both Python scripts parse; valid evidence with five products and ten posted moves | Both scripts parsed; JSON validated with five products and ten posted moves | PASS |
| Git-visible credential scan | No known local passwords or master/service credentials | 36 Git-visible files scanned; no credential values found | PASS |
| Local evidence exclusions | Database backup and both receipt screenshots ignored by Git | All three paths confirmed ignored | PASS |
| Final service and document state | Healthy services; five active products; MO Done; PO confirmed; two posted paid orders | Both services healthy; five active products; MO Done; PO Purchase; both orders Posted with LSL 15/36 paid | PASS |

The four record checksums cover all columns of the Guest House room types, rooms, bookings and guest Contacts. They are identical before and after the bakery work. All write-capable setup/actions explicitly targeted vishanti_bakery; no Guest House installation, upgrade, login or business write was performed.

## Corrected setup issue

| TEST | EXPECTED | ACTUAL | PASS / FAIL |
|---|---|---|---|
| Initial manufacturing completion attempt | MO Done; finished move +10 | MO became Cancelled when automation pre-marked the finished move picked; full transaction rolled back | FAIL — fixed |
| Diagnostic manufacturing retry | MO Done; identify the finished-quantity issue | MO Cancelled; confirmed the picked finished move was counted as already produced; full setup rolled back again | FAIL — fixed |
| Corrected manufacturing completion | Let standard MRP post the finished move | MO Done; three ingredient moves Done; finished move +10; measured stocks correct | PASS |

The setup now records component consumption and lets Odoo's standard MRP completion method post finished production. No standard module source was patched. The initial browser navigation attempted the pre-existing Sales Products action, whose Sales filter hid raw materials; verification was corrected to use the actual Inventory action. The POS driver was also corrected to click the inner New Order button. Those browser selectors did not require application changes.

No unresolved bakery issue was found in the verified initial demonstration. New sales, receipts or production will legitimately change the recorded balances and the audit's initial-demo expectations.

## Evidence and assessment

See [the assessment guide](bakery-assessment-guide.md) for exact menu paths, live document links and how to show historical BEFORE values. [bakery-evidence.json](bakery-evidence.json) retains the measured snapshots, document IDs, POS payment quantities and the complete posted stock-movement ledger. Current on-hand stock is the final state, not a historical before value. Receipt screenshots are kept in Git-ignored backups.

Reproduction and audit commands are in the project README. The setup script refuses other databases, preserves completed records on rerun and does not reset final stock. The audit script is read-only. No bakery custom module is needed for any required feature.
