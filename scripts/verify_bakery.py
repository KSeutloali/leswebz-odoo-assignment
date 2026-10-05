"""Read-only Odoo-shell audit of the completed standard bakery workflows.

No products, orders, payments, or stock quantities are modified. All quantities
are checked against posted document moves as well as actual stock on hand.
"""
import json


assert env.cr.dbname == "vishanti_bakery", "Use the bakery database only."
results = []


def check(test, expected, actual):
    row = {"test": test, "expected": expected, "actual": actual,
           "result": "PASS" if expected == actual else "FAIL"}
    results.append(row)
    assert expected == actual, row


modules = env["ir.module.module"].search([
    ("name", "in", ["stock", "purchase", "mrp", "point_of_sale"]),
])
check("Four required applications installed", ["installed"] * 4, modules.mapped("state"))
check("Required modules use Community licences", ["LGPL-3"] * 4, modules.mapped("license"))
check("No Enterprise modules installed", 0,
      env["ir.module.module"].search_count([("state", "=", "installed"), ("license", "=", "OEEL-1")]))
check("Guest House module not installed in bakery", "uninstalled",
      env["ir.module.module"].search([("name", "=", "thimo_guesthouse")]).state)
check("Currency is LSL", "LSL", env.company.currency_id.name)
codes = {"Flour": "VBAK-FLOUR", "Sugar": "VBAK-SUGAR", "Yeast": "VBAK-YEAST",
         "Croissant": "VBAK-CROISSANT", "Coca-Cola 1L": "VBAK-COLA-1L"}
products = {}
for name, code in codes.items():
    product = env["product.product"].search([("default_code", "=", code)])
    check(f"{name} exists", 1, len(product))
    products[name] = product
    check(f"{name} tracks quantities", ["consu", True, "none"],
          [product.type, product.is_storable, product.tracking])
check("Exactly five active business products", 5, env["product.template"].search_count([]))
check("Ingredient units", ["kg"] * 3, [products[name].uom_id.name for name in ("Flour", "Sugar", "Yeast")])
check("Finished product units", ["Units"] * 2, [products[name].uom_id.name for name in ("Croissant", "Coca-Cola 1L")])
check("POS availability", ["Coca-Cola 1L", "Croissant"],
      sorted(env["product.template"].search([("available_in_pos", "=", True)]).mapped("name")))
check("Ingredient purchasing/selling settings", [[True, False]] * 3,
      [[products[name].purchase_ok, products[name].sale_ok] for name in ("Flour", "Sugar", "Yeast")])
check("Croissant manufactured and sellable", [False, True],
      [products["Croissant"].purchase_ok, products["Croissant"].sale_ok])
check("Coca-Cola purchasable and sellable", [True, True],
      [products["Coca-Cola 1L"].purchase_ok, products["Coca-Cola 1L"].sale_ok])

bom = env["mrp.bom"].search([("code", "=", "VBAK-CROISSANT-10")])
check("Exactly one Croissant BoM", 1, len(bom))
check("BoM contains ONLY Flour, Sugar and Yeast", ["Flour", "Sugar", "Yeast"],
      sorted(bom.bom_line_ids.mapped("product_id.name")))
check("BoM quantities per 10 croissants", {"Flour": 1, "Sugar": 0.20, "Yeast": 0.05},
      {line.product_id.name: line.product_qty for line in bom.bom_line_ids})
check("BoM output and consumption policy", [10, "normal", "strict"],
      [bom.product_qty, bom.type, bom.consumption])
mo = env["mrp.production"].search([("origin", "=", "VBAK-DEMO-MANUFACTURE")])
check("Manufacturing Order complete", [1, "done", 10], [len(mo), mo.state, mo.qty_produced])
check("MRP consumed only required ingredients", ["Flour", "Sugar", "Yeast"],
      sorted(mo.move_raw_ids.mapped("product_id.name")))
check("Actual MRP consumption", {"Flour": 1, "Sugar": 0.20, "Yeast": 0.05},
      {move.product_id.name: round(move.quantity, 4) for move in mo.move_raw_ids})
check("Ingredient stock moves Done", ["done"] * 3, mo.move_raw_ids.mapped("state"))
check("Finished Croissant stock move", [1, "done", 10],
      [len(mo.move_finished_ids), mo.move_finished_ids.state, mo.move_finished_ids.quantity])

vendor = env["res.partner"].search([("ref", "=", "VBAK-DEMO-VENDOR")])
check("Fictional vendor exists", [1, "Demo Mountain Beverages", True],
      [len(vendor), vendor.name, vendor.supplier_rank > 0])
po = env["purchase.order"].search([("origin", "=", "VBAK-DEMO-PURCHASE")])
check("Purchase Order confirmed", [1, "purchase"], [len(po), po.state])
check("PO ordered and received quantities", [24, 24], [po.order_line.product_qty, po.order_line.qty_received])
check("Coca-Cola purchasing price and total", [12, 288], [po.order_line.price_unit, po.amount_total])
receipt = po.picking_ids
check("Purchase receipt exists and Done", [1, "done"], [len(receipt), receipt.state])
check("Receipt stock movement", [24, "supplier", "internal"],
      [receipt.move_ids.quantity, receipt.move_ids.location_id.usage, receipt.move_ids.location_dest_id.usage])
check("Receipt linked to Purchase Order", po.id, receipt.purchase_id.id)

config = env["pos.config"].search([("name", "=", "Vishanti Bakery")])
orders = env["pos.order"].search([("config_id", "=", config.id), ("state", "!=", "cancel")])
check("Two completed POS orders", ["done", "done"], sorted(orders.mapped("state")))
pos_details = []
expected_sales = {"Croissant": (1, 15), "Coca-Cola 1L": (2, 36)}
for name, (quantity, total) in expected_sales.items():
    order = orders.filtered(lambda order: order.lines.product_id == products[name])
    check(f"{name} POS sale succeeds", 1, len(order))
    check(f"{name} POS quantity sold", quantity, sum(order.lines.mapped("qty")))
    check(f"{name} POS payment completed", [total, total, "Cash"],
          [order.amount_total, order.amount_paid, order.payment_ids.payment_method_id.name])
    check(f"{name} POS owns a Done delivery", [1, "done"], [len(order.picking_ids), order.picking_ids.state])
    outgoing = order.picking_ids.move_ids
    check(f"{name} POS stock movement", [quantity, "internal", "customer"],
          [sum(outgoing.mapped("quantity")), outgoing.location_id.usage, outgoing.location_dest_id.usage])
    pos_details.append({"product": name, "order_id": order.id, "order": order.name,
                        "ticket": order.pos_reference, "sold": quantity, "paid_lsl": order.amount_paid,
                        "delivery_id": order.picking_ids.id, "delivery": order.picking_ids.name})
session = orders.session_id
check("Demo POS session Closed and Posted", [1, "closed", "posted"],
      [len(session), session.state, session.move_id.state])
check("POS opening/closing cash and difference", [0, 51, 0],
      [session.cash_register_balance_start, session.cash_register_balance_end_real,
       session.cash_register_difference])
check("POS paid cash total", 51, sum(orders.payment_ids.mapped("amount")))
check("POS accounting entry balances", 0, round(sum(session.move_id.line_ids.mapped("balance")), 2))

location = env["stock.warehouse"].search([("company_id", "=", env.company.id)], limit=1).lot_stock_id
location_ids = env["stock.location"].search([("id", "child_of", location.id)]).ids
expected_stock = {"Flour": 9, "Sugar": 1.80, "Yeast": 0.45, "Croissant": 9, "Coca-Cola 1L": 22}
stocks = {}
ledger = []
for name, product in products.items():
    moves = env["stock.move"].search([("product_id", "=", product.id), ("state", "=", "done")])
    net = 0
    for move in moves:
        quantity = move.product_uom._compute_quantity(move.quantity, product.uom_id)
        delta = quantity * (int(move.location_dest_id.id in location_ids) - int(move.location_id.id in location_ids))
        net += delta
        ledger.append({"product": name, "move_id": move.id, "reference": move.reference,
                       "quantity": round(quantity, 4), "difference": round(delta, 4),
                       "from": move.location_id.complete_name, "to": move.location_dest_id.complete_name,
                       "state": move.state})
    actual = round(product.with_context(location=location.id).qty_available, 4)
    stocks[name] = actual
    check(f"Final stock: {name}", expected_stock[name], actual)
    check(f"{name} stock agrees with posted movement ledger", round(net, 4), actual)
    adjustments = moves.filtered(lambda move: "inventory" in (move.location_id.usage, move.location_dest_id.usage))
    if name in ("Croissant", "Coca-Cola 1L"):
        check(f"{name} has no inventory adjustments", 0, len(adjustments))
    else:
        check(f"{name} has only initial stock adjustment", 1, len(adjustments))

print("BAKERY_AUDIT=" + json.dumps({"database": env.cr.dbname, "tests": results,
      "stock": stocks, "ledger": ledger, "pos_orders": pos_details,
      "session": {"id": session.id, "name": session.name, "state": session.state,
                  "account_move_id": session.move_id.id, "account_move": session.move_id.name,
                  "cash_lsl": session.cash_register_balance_end_real}}, default=str))
