# Likely assessor questions and concise answers

These answers describe this project's actual implementation.

| QUESTION | ANSWER |
|---|---|
| Why Docker Compose? | It defines Odoo, PostgreSQL, their network, mounts and healthchecks together. Pinned images and local configuration make the environment easier to repeat. |
| Why PostgreSQL? | Odoo stores its relational data in PostgreSQL. Transactions, constraints and indexes protect the data; our date-range exclusion constraint also prevents conflicting reservations. |
| Why two databases? | The assignment separates two businesses. Each database has independent users, settings, installed modules and records, while sharing one Odoo server. |
| Why use res.partner for guests? | It reuses standard Contacts, identity fields and permissions. A guest flag and booking relationship add the required Guest House integration. |
| Why custom code for Guest House? | The assignment needs specific room models, rates and booking transitions. A small custom module implements those requirements while reusing Contacts and Odoo's framework. |
| Why not custom code for Bakery? | Standard Community Inventory, Purchase, MRP and POS implement all required bakery workflows. Setup scripts configure and call these standard models; they do not introduce a bakery addon or custom business model. |
| What is the difference between Inventory and Purchase? | Purchase handles vendors, RFQs and purchase orders. Inventory handles physical quantities, locations, receipts, deliveries and stock movements. |
| What is the difference between a Purchase Order and a Receipt? | A PO records the confirmed order. Its receipt records goods arriving. Validating the receipt increases physical on-hand stock; PO confirmation alone does not. |
| What is a Bill of Materials? | It defines components and quantities required for an output quantity. Our BoM produces 10 croissants using exactly 1 kg flour, 0.20 kg sugar and 0.05 kg yeast. |
| What does a Manufacturing Order do? | It executes production for a product and quantity using its BoM. Completing it posts component consumption and finished-product stock moves. |
| Why does raw-material stock decrease? | The completed MO moves the consumed ingredients from WH/Stock to the Production location. |
| Why does finished stock increase? | The completed MO moves its produced croissants from Production into WH/Stock. |
| Why does POS reduce stock? | These products track quantities, and this POS is configured to update stock at payment. Each paid order creates a completed outgoing delivery from Stock to Customers. |
| How does persistence work? | Named Docker volumes retain PostgreSQL data and Odoo's filestore/sessions outside the containers. The custom addon source stays on the host bind mount. The actual down/up test preserved all sampled data and attachments. |
| Why is docker compose down -v dangerous? | It removes the named volumes containing the databases and filestore. Normal down without -v retains them. |
| What is Developer Mode used for? | It exposes technical tools for inspecting models, fields, views and record identifiers. It helps development and troubleshooting; it does not grant additional access rights. |
| How does custom-addons work? | Compose mounts host custom-addons at /mnt/extra-addons, included in Odoo's addon discovery path. The module is installed per database. Host edits supply the source; Python changes require restart and model/view/data changes require upgrade. |
| How was the Odoo ORM used? | Models define fields and relationships. create/write and workflow methods validate changes; computed fields calculate nights, totals and room state. ACLs control who can use models. PostgreSQL constraints provide additional integrity protection. |
| How are overlapping room reservations prevented? | For the same room, confirmed and checked-in stays overlap if existing check-in is before the new check-out and existing check-out is after the new check-in. Python checks reject conflicts; a PostgreSQL GiST exclusion constraint protects concurrent writes. Checkout is exclusive, adjacent stays are allowed, and cancelled bookings do not block dates. |

Source/evidence:
[Booking model](../custom-addons/thimo_guesthouse/models/booking.py),
[Room model](../custom-addons/thimo_guesthouse/models/room.py),
[Partner integration](../custom-addons/thimo_guesthouse/models/res_partner.py),
[Compose](../docker-compose.yml),
[bakery stock/payment evidence](bakery-evidence.json),
[acceptance checklist](user-acceptance-results.md).

Current release answer if asked: **the runtime requirements passed; the complete
README installation and fresh setup reproduction remain unverified.** The Git
worktree and initial commit exist; the final documentation commit and actual
clone source are pending.
