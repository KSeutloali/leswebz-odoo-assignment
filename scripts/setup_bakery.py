"""Odoo 19 standard-model setup, executed through `odoo shell`.

Targets vishanti_bakery only. No addon, custom model, or stock SQL is used.
Initial component stock is an inventory adjustment. All later movements are
posted by normal MRP and receipt validation. POS sales are completed separately.
The shell provides env. A completed setup is preserved on repeat runs.
"""
import json
from datetime import timedelta

from odoo import Command, fields
from odoo.exceptions import UserError


MODULES = ["stock", "purchase", "mrp", "point_of_sale"]
MO_ORIGIN = "VBAK-DEMO-MANUFACTURE"
PO_ORIGIN = "VBAK-DEMO-PURCHASE"


def main(env):
    if env.cr.dbname != "vishanti_bakery":
        raise UserError("Run this script only against vishanti_bakery.")
    env.cr.execute("SELECT pg_advisory_xact_lock(%s)", [19000524])
    installed = env["ir.module.module"].search([
        ("name", "in", MODULES), ("state", "=", "installed"),
    ])
    if len(installed) != 4:
        raise UserError("Install stock, purchase, mrp and point_of_sale first.")
    Production = env["mrp.production"]
    Purchase = env["purchase.order"]
    existing_mo = Production.search([("origin", "=", MO_ORIGIN)])
    existing_po = Purchase.search([("origin", "=", PO_ORIGIN)])
    if existing_mo or existing_po:
        if (len(existing_mo) == len(existing_po) == 1 and existing_mo.state == "done"
                and existing_po.state == "purchase" and len(existing_po.picking_ids) == 1 and all(
            receipt.state == "done" for receipt in existing_po.picking_ids
        )):
            print("BAKERY_SETUP_ALREADY_EXISTS=" + json.dumps({
                "manufacturing_order": existing_mo.name, "purchase_order": existing_po.name,
                "message": "Existing documents and stock preserved; no duplicate production or receipt.",
            }))
            return
        raise UserError("A partial demonstration exists; review it before running setup again.")
    Product = env["product.template"]
    if Product.with_context(active_test=False).search_count([("default_code", "like", "VBAK-%")]):
        raise UserError("Bakery product codes already exist; review rather than replace their stock.")

    results = []

    def check(test, expected, actual):
        row = {"test": test, "expected": expected, "actual": actual,
               "result": "PASS" if expected == actual else "FAIL"}
        results.append(row)
        if expected != actual:
            raise AssertionError(row)

    company = env.company
    currency = env.ref("base.LSL")
    currency.active = True
    company.write({"name": "Vishanti Bakery", "currency_id": currency.id,
                   "country_id": env.ref("base.ls").id,
                   "account_fiscal_country_id": env.ref("base.ls").id,
                   "point_of_sale_update_stock_quantities": "real"})
    check("Required Community applications installed", sorted(MODULES), sorted(installed.mapped("name")))
    check("Bakery currency", "LSL", company.currency_id.name)
    check("Fiscal country", "Lesotho", company.account_fiscal_country_id.name)
    warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
    assert warehouse
    location = warehouse.lot_stock_id
    kg, units = env.ref("uom.product_uom_kgm"), env.ref("uom.product_uom_unit")
    buy = env.ref("purchase_stock.route_warehouse0_buy")
    manufacture = env.ref("mrp.route_warehouse0_manufacture")
    for xmlid in ("point_of_sale.product_product_tip", "pos_sale.default_downpayment_product"):
        technical = env.ref(xmlid, raise_if_not_found=False)
        if technical:
            technical.product_tmpl_id.active = False

    specs = [
        ("Flour", "VBAK-FLOUR", kg, 20, 0, True, False, buy),
        ("Sugar", "VBAK-SUGAR", kg, 30, 0, True, False, buy),
        ("Yeast", "VBAK-YEAST", kg, 100, 0, True, False, buy),
        ("Croissant", "VBAK-CROISSANT", units, 3.10, 15, False, True, manufacture),
        ("Coca-Cola 1L", "VBAK-COLA-1L", units, 12, 18, True, True, buy),
    ]
    products = {}
    for name, code, uom, cost, price, purchasable, sellable, route in specs:
        template = Product.create({
            "name": name, "default_code": code, "type": "consu", "is_storable": True,
            "tracking": "none", "uom_id": uom.id, "standard_price": cost,
            "list_price": price, "purchase_ok": purchasable, "sale_ok": sellable,
            "available_in_pos": sellable, "company_id": company.id,
            "purchase_method": "receive", "route_ids": [Command.set(route.ids)],
            "taxes_id": [Command.clear()], "supplier_taxes_id": [Command.clear()],
        })
        products[name] = template.product_variant_id
        check(f"{name} exists and tracks inventory", True, template.is_storable and template.tracking == "none")
    check("Active business products", 5, Product.search_count([]))
    vendor = env["res.partner"].create({
        "name": "Demo Mountain Beverages", "is_company": True,
        "supplier_rank": 1, "ref": "VBAK-DEMO-VENDOR",
    })
    env["product.supplierinfo"].create({
        "partner_id": vendor.id, "product_tmpl_id": products["Coca-Cola 1L"].product_tmpl_id.id,
        "product_uom_id": units.id, "min_qty": 1, "price": 12,
        "currency_id": currency.id, "delay": 0, "company_id": company.id,
    })
    check("Fictional Coca-Cola vendor", True, vendor.supplier_rank > 0 and vendor.is_company)

    quantities = {"Flour": 1, "Sugar": 0.20, "Yeast": 0.05}
    bom = env["mrp.bom"].create({
        "code": "VBAK-CROISSANT-10", "product_tmpl_id": products["Croissant"].product_tmpl_id.id,
        "product_id": products["Croissant"].id, "product_qty": 10,
        "product_uom_id": units.id, "type": "normal", "consumption": "strict",
        "company_id": company.id,
        "bom_line_ids": [Command.create({"product_id": products[name].id,
                                         "product_qty": quantity, "product_uom_id": kg.id})
                         for name, quantity in quantities.items()],
    })
    check("Croissant BoM ingredients ONLY", ["Flour", "Sugar", "Yeast"],
          sorted(bom.bom_line_ids.mapped("product_id.name")))
    check("BoM batch size", 10, bom.product_qty)
    check("BoM quantities in kg", quantities,
          {line.product_id.name: line.product_qty for line in bom.bom_line_ids})

    def stock():
        env.flush_all()
        env.invalidate_all()
        return {name: round(product.with_context(location=location.id).qty_available, 4)
                for name, product in products.items()}

    initial = {"Flour": 10, "Sugar": 2, "Yeast": 0.50}
    for name, quantity in initial.items():
        quant = env["stock.quant"].with_context(inventory_mode=True).create({
            "product_id": products[name].id, "location_id": location.id,
            "inventory_quantity": quantity,
        })
        quant.with_context(inventory_name="Vishanti demo opening stock").action_apply_inventory()
    before_mrp = stock()
    check("Starting stock recorded", {**initial, "Croissant": 0, "Coca-Cola 1L": 0}, before_mrp)
    mo = Production.create({
        "product_id": products["Croissant"].id, "product_qty": 10,
        "product_uom_id": units.id, "bom_id": bom.id, "origin": MO_ORIGIN,
        "picking_type_id": warehouse.manu_type_id.id, "company_id": company.id,
    })
    mo.action_confirm()
    check("Manufacturing Order confirms", "confirmed", mo.state)
    mo.action_assign()
    mo.qty_producing = 10
    # Record component consumption. MRP posts the finished move itself; marking
    # it picked here would count the quantity as already produced in Odoo 19.
    for move in mo.move_raw_ids:
        move.quantity = move.product_uom_qty
        move.picked = True
    mo.with_context(skip_redirection=True).button_mark_done()
    check("Manufacturing Order completes", "done", mo.state)
    after_mrp = stock()
    expected_after = {"Flour": 9, "Sugar": 1.80, "Yeast": 0.45, "Croissant": 10, "Coca-Cola 1L": 0}
    for name in products:
        check(f"Stock after MRP: {name}", expected_after[name], after_mrp[name])
    check("MRP owns ingredient and finished stock moves", True,
          len(mo.move_raw_ids) == 3 and len(mo.move_finished_ids) == 1
          and all(move.state == "done" for move in mo.move_raw_ids | mo.move_finished_ids))

    before_po = stock()["Coca-Cola 1L"]
    po = Purchase.create({
        "partner_id": vendor.id, "currency_id": currency.id, "origin": PO_ORIGIN,
        "company_id": company.id,
        "order_line": [Command.create({
            "product_id": products["Coca-Cola 1L"].id, "name": "Coca-Cola 1L",
            "product_qty": 24, "product_uom_id": units.id, "price_unit": 12,
            "date_planned": fields.Datetime.now() + timedelta(hours=1),
            "tax_ids": [Command.clear()],
        })],
    })
    check("RFQ created", "draft", po.state)
    po.button_confirm()
    check("Purchase Order confirmed", "purchase", po.state)
    after_po = stock()["Coca-Cola 1L"]
    check("PO confirmation does not change physical stock", before_po, after_po)
    receipts = po.picking_ids
    check("PO creates receipt", 1, len(receipts))
    check("Receipt pending before validation", True, receipts.state not in ("done", "cancel"))
    before_receipt = stock()["Coca-Cola 1L"]
    for move in receipts.move_ids:
        move.quantity = move.product_uom_qty
        move.picked = True
    receipts.button_validate()
    check("Receipt validated", "done", receipts.state)
    after_receipt = stock()["Coca-Cola 1L"]
    check("Receipt increases stock by 24", 24, after_receipt - before_receipt)
    check("Coca-Cola stock after receipt", 24, after_receipt)
    check("PO received quantity", 24, po.order_line.qty_received)

    cash_journal = env["account.journal"].create({
        "name": "Bakery Cash", "code": "BCSH", "type": "cash", "company_id": company.id,
    })
    cash = env["pos.payment.method"].create({
        "name": "Cash", "journal_id": cash_journal.id, "company_id": company.id,
    })
    config = env["pos.config"].create({
        "name": "Vishanti Bakery", "company_id": company.id,
        "picking_type_id": warehouse.pos_type_id.id,
        "cash_control": True, "payment_method_ids": [Command.set(cash.ids)],
        "iface_tipproduct": False,
    })
    config.with_user(env.ref("base.user_admin")).open_ui()
    session = config.current_session_id
    check("POS session created", True, bool(session))
    check("POS has only Cash payment", ["Cash"], session.payment_method_ids.mapped("name"))
    check("POS updates stock in real time", False, session.update_stock_at_closing)
    pos_products = Product.search([("available_in_pos", "=", True)])
    check("Only required sale products in POS", ["Coca-Cola 1L", "Croissant"], sorted(pos_products.mapped("name")))
    env.flush_all()
    evidence = {
        "database": env.cr.dbname, "company": company.name, "currency": currency.name,
        "recorded_at_utc": fields.Datetime.now().isoformat(), "tests": results,
        "products": {name: {"id": product.id, "template_id": product.product_tmpl_id.id,
                            "uom": product.uom_id.name, "cost": product.standard_price,
                            "sale_price": product.lst_price} for name, product in products.items()},
        "vendor": {"id": vendor.id, "name": vendor.name},
        "bom": {"id": bom.id, "reference": bom.code, "output": 10, "ingredients_kg": quantities},
        "manufacturing": {"id": mo.id, "reference": mo.name, "before": before_mrp, "after": after_mrp,
                          "difference": {name: round(after_mrp[name] - before_mrp[name], 4) for name in products}},
        "purchase": {"id": po.id, "reference": po.name, "before_confirmation": before_po,
                     "after_confirmation": after_po, "total_lsl": po.amount_total},
        "receipt": {"id": receipts.id, "reference": receipts.name,
                    "before": before_receipt, "after": after_receipt, "quantity": 24},
        "pos": {"config_id": config.id, "session_id": session.id, "cash_method_id": cash.id},
        "location": {"id": location.id, "name": location.complete_name},
    }
    env.cr.commit()
    print("BAKERY_SETUP_EVIDENCE=" + json.dumps(evidence, default=str))


main(env)
