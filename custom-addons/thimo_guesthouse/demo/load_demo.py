"""Run through `odoo shell` to opt in on a database created without demos.

The shell provides `env`. Normal demo-enabled installations use the manifest
instead. Loading is atomic and repeat runs preserve the existing records.
"""
from xml.etree import ElementTree

from odoo.exceptions import UserError
from odoo.tools import convert_file, file_open


def load_demo(env):
    module = "thimo_guesthouse"
    filename = "demo/guesthouse_demo.xml"
    if env.cr.dbname != "thimo_guesthouse":
        raise UserError("Load these samples only into the thimo_guesthouse database.")
    installed = env["ir.module.module"].search([
        ("name", "=", module), ("state", "=", "installed"),
    ])
    if not installed:
        raise UserError("Install thimo_guesthouse before loading its samples.")
    with file_open(f"{module}/{filename}", env=env) as source:
        root = ElementTree.parse(source).getroot()
    xmlids = [f"{module}.{record.attrib['id']}" for record in root.iter("record")]
    existing = [env.ref(xmlid, raise_if_not_found=False) for xmlid in xmlids]
    if all(existing):
        print("Guest House samples already exist; no records changed.")
        return
    if any(existing):
        raise UserError("Some sample records are missing. Restore or review them before reloading.")
    if env["thimo.guesthouse.room"].with_context(active_test=False).search_count([]):
        raise UserError("Samples require an empty room list, so they create exactly five initial rooms.")
    with env.cr.savepoint():
        convert_file(env, module, filename, {}, mode="init")
        env.flush_all()
    env.cr.commit()
    print("Loaded 3 room types, 5 rooms, 5 fictional guests and 5 bookings.")


load_demo(env)
