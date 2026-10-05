# Bakery assessment walkthrough

Log in to [vishanti_bakery](http://localhost:8069/web/login?db=vishanti_bakery) using its existing local administrator credentials. Keep this database selected while using the links. Company: **Vishanti Bakery**; currency: **LSL**, displayed as **M**.

The initial demonstration is complete. Current stock screens show quantities after both sales. Historical BEFORE values are recorded in [the test report](bakery-test-results.md) and [evidence JSON](bakery-evidence.json), and can be corroborated with the named moves in Inventory → Reporting → Moves History. Do not present current stock as an earlier balance.

## Croissant

The BoM produces 10 croissants from **only 1 kg Flour, 0.20 kg Sugar and 0.05 kg Yeast**.

| Show | Exact screen/document | Evidence |
|---|---|---|
| Raw-material stock before production | Inventory → Reporting → [Moves History](http://localhost:8069/odoo/moves-history); filter Reference = `Vishanti demo opening stock` | Three opening adjustments into WH/Stock: Flour 10 kg, Sugar 2 kg, Yeast 0.50 kg. These were the measured starting balances. |
| Croissant before production | Manufacturing BEFORE snapshot in the report/evidence | 0 Units; no opening Croissant adjustment or earlier stock movement exists. |
| BoM | Manufacturing → Products → Bills of Materials → [VBAK-CROISSANT-10](http://localhost:8069/odoo/boms/3) | Output 10 Units. Exactly three component lines: Flour 1 kg, Sugar 0.20 kg, Yeast 0.05 kg. |
| Manufacturing Order | Manufacturing → Operations → Manufacturing Orders → [WH/MO/00003](http://localhost:8069/odoo/manufacturing/3) | Done; 10 produced; Components tab shows the three consumed quantities. |
| Production stock movements | Moves History; filter Reference = `WH/MO/00003` | WH/Stock → Production: Flour 1 kg, Sugar 0.20 kg, Yeast 0.05 kg. Production → WH/Stock: 10 Croissants. |
| Raw-material stock after production | Inventory → Reporting → [Stock](http://localhost:8069/odoo/stock-report) | Flour 9 kg, Sugar 1.80 kg, Yeast 0.45 kg. These remained unchanged during POS sales. |
| Croissant stock increase | Moves History, Reference = `WH/MO/00003`, Product = Croissant | Incoming +10 Units. The recorded AFTER-MRP stock was 10. |
| POS sale | Point of Sale → Orders → Orders → [Vishanti Bakery - 000001](http://localhost:8069/odoo/pos-orders/1) | 1 Croissant, LSL 15, Cash fully paid; Posted after session closing. |
| POS stock movement | Order's linked transfer, or Inventory → Operations → Deliveries → [WH/POS/00001](http://localhost:8069/odoo/deliveries/2) | Done; WH/Stock → Customers; 1 Croissant. |
| Croissant stock decrease | Inventory → Reporting → Stock, Product = Croissant | Current 9 Units: 10 before POS − 1 sold = 9. |

## Coca-Cola 1L

Vendor: **Demo Mountain Beverages**, a fictional company. Purchase price **LSL 12/bottle**; selling price **LSL 18/bottle**. Units mean individual 1 L bottles.

| Show | Exact screen/document | Evidence |
|---|---|---|
| Vendor | Purchase → Orders → Vendors; search Demo Mountain Beverages | Fictional vendor also linked on the PO and product Purchase tab. |
| Purchase Order | Purchase → Orders → Purchase Orders → [P00001](http://localhost:8069/odoo/purchase-orders/1) | 24 × Coca-Cola 1L at LSL 12 = LSL 288; created as an RFQ, then confirmed. |
| Stock before receipt | Purchase/receipt BEFORE snapshots in the report/evidence | Physical stock 0 before PO confirmation, 0 after confirmation, and 0 immediately before validating receipt. |
| Receipt | P00001's Receipt smart button, or Inventory → Operations → Receipts → [WH/IN/00001](http://localhost:8069/odoo/receipts/1) | Done, quantity 24, Vendors → WH/Stock, linked to P00001. |
| Stock increase after receipt | Moves History; Reference = `WH/IN/00001`, Product = Coca-Cola 1L | Incoming +24 Units. Recorded stock immediately after receipt was 24. |
| POS sale | Point of Sale → Orders → Orders → [Vishanti Bakery - 000002](http://localhost:8069/odoo/pos-orders/2) | 2 bottles × LSL 18 = LSL 36; Cash fully paid; Posted. |
| POS stock movement | Order's linked transfer, or Inventory → Operations → Deliveries → [WH/POS/00002](http://localhost:8069/odoo/deliveries/3) | Done; WH/Stock → Customers; 2 bottles. |
| Stock after sale | Inventory → Reporting → Stock, Product = Coca-Cola 1L | Current 22 Units: 24 before POS − 2 sold = 22. |

## Which document causes inventory movement?

| Action/document | Physical inventory effect |
|---|---|
| Opening inventory adjustments | Establish only the three raw-material starting balances. |
| Confirm PO P00001 | Creates an expected receipt; physical on-hand stock remains 0. |
| Validate receipt WH/IN/00001 | Adds 24 Coca-Cola bottles to WH/Stock. |
| Complete MO WH/MO/00003 | Consumes the three ingredients and adds 10 Croissants. |
| Validate each fully paid POS order | Creates/completes its linked WH/POS delivery, removing 1 Croissant or 2 bottles. Stock updates in real time. |
| Close POS session | Posts sales/cash accounting; stock deliveries were already completed at payment. |

Open Point of Sale → Orders → Sessions → [Vishanti Bakery/00001](http://localhost:8069/odoo/pos-sessions/1) to show Closed & Posted, opening cash 0, closing cash 51 and difference 0. The posted entry is **POSS/2026/10/0001**.

Receipt screenshots are stored outside Git at `backups/bakery-croissant-receipt.png` and `backups/bakery-cola-receipt.png`.

## A new live transaction

For another live sale, open Point of Sale → Dashboard → Vishanti Bakery → Open Register. The previous completed session closed with LSL 51; use the opening cash actually displayed and entered rather than assuming a new session already exists. Complete a new cash order and reconcile its counted cash when closing.

For another production demonstration, record current raw/finished stock, create a new MO for 10 Croissants using the same BoM, confirm it, record consumption and complete it. A new Coca-Cola RFQ/PO likewise changes physical stock only when its receipt is validated.

Further production, receipts or sales change these balances. The audit script verifies the initial completed demonstration and does not reset stock or manufacture again. Repeating from the original opening balances requires a fresh bakery database or a reviewed restore. Keep `thimo_guesthouse` unchanged.
