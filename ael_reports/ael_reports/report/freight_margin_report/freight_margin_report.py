
# import frappe
# from frappe.utils import flt
# from collections import defaultdict


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():
#     return [
#         {"label": "Invoice Number",      "fieldname": "invoice",            "fieldtype": "Link",     "options": "Sales Invoice", "width": 160},
#         {"label": "Customer Name",       "fieldname": "customer",           "fieldtype": "Data",     "width": 180},
#         {"label": "Sales Order",         "fieldname": "sales_order",        "fieldtype": "Link",     "options": "Sales Order",     "width": 150},
#         {"label": "Purchase Order",      "fieldname": "purchase_order",     "fieldtype": "Link",     "options": "Purchase Order",  "width": 150},
#         {"label": "Purchase Invoice",    "fieldname": "purchase_invoice",   "fieldtype": "Link",     "options": "Purchase Invoice","width": 160},
#         {"label": "Origin Country",      "fieldname": "origin_country",     "fieldtype": "Data",     "width": 140},
#         {"label": "Destination Country", "fieldname": "destination_country","fieldtype": "Data",     "width": 160},
#         {"label": "Mode",                "fieldname": "mode",               "fieldtype": "Data",     "width": 100},
#         {"label": "CBM",                 "fieldname": "cbm",                "fieldtype": "Float",    "width": 100},
#         {"label": "Weight",              "fieldname": "weight",             "fieldtype": "Float",    "width": 100},
#         {"label": "Job No",              "fieldname": "job_no",             "fieldtype": "Data",     "width": 140},
#         {"label": "BUY",                 "fieldname": "buy",                "fieldtype": "Currency", "width": 120},
#         {"label": "SELL",                "fieldname": "sell",               "fieldtype": "Currency", "width": 120},
#         {"label": "Gross Margin",        "fieldname": "gross_margin",       "fieldtype": "Currency", "width": 130},
#         {"label": "Gross Percent",       "fieldname": "gross_percentage",   "fieldtype": "Percent",  "width": 120},
#         {"label": "Commission",          "fieldname": "commission",         "fieldtype": "Currency", "width": 120},
#         {"label": "Net Margin",          "fieldname": "net_margin",         "fieldtype": "Currency", "width": 130},
#     ]


# def get_data(filters):

#     conditions = []
#     values = {}

#     if filters.get("company"):
#         conditions.append("si.company = %(company)s")
#         values["company"] = filters["company"]

#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#         values["from_date"] = filters["from_date"]

#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#         values["to_date"] = filters["to_date"]

#     if filters.get("customer"):
#         conditions.append("si.customer = %(customer)s")
#         values["customer"] = filters["customer"]

#     if filters.get("sales_invoice"):
#         conditions.append("si.name = %(sales_invoice)s")
#         values["sales_invoice"] = filters["sales_invoice"]

#     if filters.get("item_group"):
#         conditions.append("sii.item_group = %(item_group)s")
#         values["item_group"] = filters["item_group"]

#     if filters.get("warehouse"):
#         conditions.append("sii.warehouse = %(warehouse)s")
#         values["warehouse"] = filters["warehouse"]

#     if filters.get("project"):
#         conditions.append("sii.project = %(project)s")
#         values["project"] = filters["project"]

#     if filters.get("invoice_type") == "Credit Note":
#         conditions.append("si.is_return = 1")
#     else:
#         conditions.append("IFNULL(si.is_return, 0) = 0")

#     if not filters.get("include_returned"):
#         conditions.append("IFNULL(si.is_return, 0) = 0")

#     where_clause = (" AND " + " AND ".join(conditions)) if conditions else ""

#     query = f"""
#         SELECT
#             si.name                          AS invoice,
#             si.customer,

#             so_ref.sales_order               AS sales_order,
#             po_ref.purchase_order            AS purchase_order,
#             pi_ref.purchase_invoice          AS purchase_invoice,

#             si.custom_country_of_origin      AS origin_country,
#             si.custom_country_of_destination AS destination_country,
#             si.custom_mode                   AS mode,

#             si.custom_total_cbm              AS cbm,
#             si.custom_total_weight           AS weight,
#             si.custom_job_no                 AS job_no,

#             SUM(sii.base_net_amount)         AS sell,
#             IFNULL(si.custom_commission, 0)  AS commission

#         FROM `tabSales Invoice` si

#         LEFT JOIN `tabSales Invoice Item` sii
#             ON sii.parent = si.name

#         LEFT JOIN (
#             SELECT parent AS invoice, MIN(sales_order) AS sales_order
#             FROM `tabSales Invoice Item`
#             WHERE sales_order IS NOT NULL AND sales_order != ''
#             GROUP BY parent
#         ) so_ref ON so_ref.invoice = si.name

#         LEFT JOIN (
#             SELECT sales_order, MIN(parent) AS purchase_order
#             FROM `tabPurchase Order Item`
#             WHERE sales_order IS NOT NULL AND sales_order != ''
#             GROUP BY sales_order
#         ) po_ref ON po_ref.sales_order = so_ref.sales_order

#         LEFT JOIN (
#             SELECT purchase_order, MIN(parent) AS purchase_invoice
#             FROM `tabPurchase Invoice Item`
#             WHERE purchase_order IS NOT NULL AND purchase_order != ''
#             GROUP BY purchase_order
#         ) pi_ref ON pi_ref.purchase_order = po_ref.purchase_order

#         WHERE si.docstatus = 1
#         {where_clause}
#         GROUP BY si.name
#         ORDER BY si.posting_date DESC
#     """

#     invoices = frappe.db.sql(query, values, as_dict=True)

#     if not invoices:
#         return []

#     # ── Collect all job_no values (= sales_order on PO item) ──────────
#     job_nos = [d.job_no for d in invoices if d.job_no]

#     invoice_names   = [d.invoice for d in invoices]
#     placeholders_si = ", ".join(["%s"] * len(invoice_names))

#     # ── Fetch SI items ─────────────────────────────────────────────────
#     items = frappe.db.sql(f"""
#         SELECT
#             sii.parent          AS invoice,
#             sii.item_code,
#             sii.item_name,
#             sii.qty,
#             sii.uom,
#             sii.rate,
#             sii.base_net_amount AS amount,
#             sii.item_group,
#             sii.warehouse
#         FROM `tabSales Invoice Item` sii
#         WHERE sii.parent IN ({placeholders_si})
#         ORDER BY sii.parent, sii.idx
#     """, tuple(invoice_names), as_dict=True)

#     # ── Fetch PO items matched by sales_order = job_no ────────────────
#     # key: sales_order (job_no) → amount
#     po_buy_map = {}
#     if job_nos:
#         placeholders_jo = ", ".join(["%s"] * len(job_nos))
#         po_items = frappe.db.sql(f"""
#             SELECT
#                 poi.sales_order,
#                 poi.amount
#             FROM `tabPurchase Order Item` poi
#             WHERE poi.sales_order IN ({placeholders_jo})
#               AND poi.docstatus != 2
#         """, tuple(job_nos), as_dict=True)

#         for poi in po_items:
#             so = poi.sales_order
#             # accumulate in case multiple PO item rows share same sales_order
#             po_buy_map[so] = po_buy_map.get(so, 0.0) + flt(poi.amount)

#     # ── item map grouped by invoice ───────────────────────────────────
#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     # ── Attach buy per invoice using job_no → PO item amount ──────────
#     for inv in invoices:
#         job_no     = inv.job_no or ""
#         buy        = flt(po_buy_map.get(job_no, 0))
#         sell       = flt(inv.sell or 0)
#         commission = flt(inv.commission or 0)

#         inv["buy"]              = buy
#         inv["gross_margin"]     = sell - buy
#         inv["gross_percentage"] = ((sell - buy) / sell * 100) if sell else 0
#         inv["net_margin"]       = sell - buy - commission

#     # ── Total Based: parent rows only ─────────────────────────────────
#     total_amount_view = filters.get("total_amount_view", "Invoice Based")
#     if total_amount_view == "Total Based":
#         for inv in invoices:
#             inv["indent"] = 0
#         return invoices

#     # ── Invoice Based: expandable child item rows ──────────────────────
#     result = []
#     for inv in invoices:
#         inv["indent"] = 0
#         result.append(inv)

#         job_no  = inv.job_no or ""
#         # for child rows buy is the same matched amount (one job_no per invoice)
#         item_buy_total = flt(po_buy_map.get(job_no, 0))
#         inv_items      = item_map.get(inv.invoice, [])
#         item_count     = len(inv_items) or 1

#         for itm in inv_items:
#             item_sell      = flt(itm.amount or 0)
#             # distribute buy proportionally across items by their sell share
#             inv_sell       = flt(inv.sell or 0)
#             if inv_sell:
#                 item_buy = item_buy_total * (item_sell / inv_sell)
#             else:
#                 item_buy = item_buy_total / item_count

#             item_gross     = item_sell - item_buy
#             item_gross_pct = (item_gross / item_sell * 100) if item_sell else 0.0

#             child = {
#                 "indent":              1,
#                 "invoice":             itm.item_name or itm.item_code,
#                 "customer":            "",
#                 "sales_order":         "",
#                 "purchase_order":      "",
#                 "purchase_invoice":    "",
#                 "origin_country":      "",
#                 "destination_country": "",
#                 "mode":                "",
#                 "cbm":                 None,
#                 "weight":              None,
#                 "job_no":              "",
#                 "buy":                 item_buy,
#                 "sell":                item_sell,
#                 "gross_margin":        item_gross,
#                 "gross_percentage":    item_gross_pct,
#                 "commission":          0,
#                 "net_margin":          item_gross,
#             }
#             result.append(child)

#     return result


import frappe
from frappe.utils import flt
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Invoice Number",      "fieldname": "invoice",            "fieldtype": "Link",     "options": "Sales Invoice", "width": 160},
        {"label": "Customer Name",       "fieldname": "customer",           "fieldtype": "Data",     "width": 180},
        {"label": "Sales Order",         "fieldname": "sales_order",        "fieldtype": "Link",     "options": "Sales Order",     "width": 150},
        {"label": "Purchase Order",      "fieldname": "purchase_order",     "fieldtype": "Link",     "options": "Purchase Order",  "width": 150},
        {"label": "Purchase Invoice",    "fieldname": "purchase_invoice",   "fieldtype": "Link",     "options": "Purchase Invoice","width": 160},
        {"label": "Origin Country",      "fieldname": "origin_country",     "fieldtype": "Data",     "width": 140},
        {"label": "Destination Country", "fieldname": "destination_country","fieldtype": "Data",     "width": 160},
        {"label": "Mode",                "fieldname": "mode",               "fieldtype": "Data",     "width": 100},
        {"label": "CBM",                 "fieldname": "cbm",                "fieldtype": "Float",    "width": 100},
        {"label": "Weight",              "fieldname": "weight",             "fieldtype": "Float",    "width": 100},
        {"label": "Job No",              "fieldname": "job_no",             "fieldtype": "Data",     "width": 140},
        {"label": "BUY",                 "fieldname": "buy",                "fieldtype": "Currency", "width": 120},
        {"label": "SELL",                "fieldname": "sell",               "fieldtype": "Currency", "width": 120},
        {"label": "Gross Margin",        "fieldname": "gross_margin",       "fieldtype": "Currency", "width": 130},
        {"label": "Gross Percent",       "fieldname": "gross_percentage",   "fieldtype": "Percent",  "width": 120},
        {"label": "Commission",          "fieldname": "commission",         "fieldtype": "Currency", "width": 120},
        {"label": "Net Margin",          "fieldname": "net_margin",         "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):

    conditions = []
    values = {}

    if filters.get("company"):
        conditions.append("si.company = %(company)s")
        values["company"] = filters["company"]

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters["to_date"]

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters["customer"]

    if filters.get("sales_invoice"):
        conditions.append("si.name = %(sales_invoice)s")
        values["sales_invoice"] = filters["sales_invoice"]

    if filters.get("item_group"):
        conditions.append("sii.item_group = %(item_group)s")
        values["item_group"] = filters["item_group"]

    if filters.get("warehouse"):
        conditions.append("sii.warehouse = %(warehouse)s")
        values["warehouse"] = filters["warehouse"]

    if filters.get("project"):
        conditions.append("sii.project = %(project)s")
        values["project"] = filters["project"]

    if filters.get("invoice_type") == "Credit Note":
        conditions.append("si.is_return = 1")
    else:
        conditions.append("IFNULL(si.is_return, 0) = 0")

    if not filters.get("include_returned"):
        conditions.append("IFNULL(si.is_return, 0) = 0")

    where_clause = (" AND " + " AND ".join(conditions)) if conditions else ""

    query = f"""
        SELECT
            si.name                          AS invoice,
            si.customer,

            so_ref.sales_order               AS sales_order,

            si.custom_country_of_origin      AS origin_country,
            si.custom_country_of_destination AS destination_country,
            si.custom_mode                   AS mode,

            si.custom_total_cbm              AS cbm,
            si.custom_total_weight           AS weight,
            si.custom_job_no                 AS job_no,

            SUM(sii.base_net_amount)         AS sell,
            IFNULL(si.custom_commission, 0)  AS commission

        FROM `tabSales Invoice` si

        LEFT JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name

        LEFT JOIN (
            SELECT parent AS invoice, MIN(sales_order) AS sales_order
            FROM `tabSales Invoice Item`
            WHERE sales_order IS NOT NULL AND sales_order != ''
            GROUP BY parent
        ) so_ref ON so_ref.invoice = si.name

        WHERE si.docstatus = 1
        {where_clause}
        GROUP BY si.name
        ORDER BY si.posting_date DESC
    """

    invoices = frappe.db.sql(query, values, as_dict=True)

    if not invoices:
        return []

    invoice_names = [d.invoice     for d in invoices]
    job_nos       = [d.job_no      for d in invoices if d.job_no]
    sales_orders  = [d.sales_order for d in invoices if d.sales_order]

    placeholders_si = ", ".join(["%s"] * len(invoice_names))

    # ── Fetch SI items ─────────────────────────────────────────────────
    items = frappe.db.sql(f"""
        SELECT
            sii.parent          AS invoice,
            sii.item_code,
            sii.item_name,
            sii.qty,
            sii.uom,
            sii.rate,
            sii.base_net_amount AS amount,
            sii.item_group,
            sii.warehouse
        FROM `tabSales Invoice Item` sii
        WHERE sii.parent IN ({placeholders_si})
        ORDER BY sii.parent, sii.idx
    """, tuple(invoice_names), as_dict=True)

    # ── Build amended SO lookup ────────────────────────────────────────
    # For each job_no, also find amended versions of that SO
    # e.g. LCLIMP0482 → also check LCLIMP0482-1, LCLIMP0482-2 etc.
    # We collect ALL SO names (original + amended) that map to each job_no
    # job_no_to_so_names: job_no → set of all SO names including amended
    job_no_to_so_names = defaultdict(set)

    if job_nos:
        placeholders_jn = ", ".join(["%s"] * len(job_nos))

        # find the original SO and all its amendments
        so_chain_rows = frappe.db.sql(f"""
            SELECT
                so.name,
                IFNULL(so.amended_from, so.name) AS root_so
            FROM `tabSales Order` so
            WHERE (
                so.name IN ({placeholders_jn})
                OR so.amended_from IN ({placeholders_jn})
                OR so.amended_from IN (
                    SELECT name FROM `tabSales Order`
                    WHERE amended_from IN ({placeholders_jn})
                )
            )
            AND so.docstatus != 2
        """, tuple(job_nos) * 3, as_dict=True)

        # group by root: root_so → all active SO names in that chain
        root_to_names = defaultdict(set)
        for row in so_chain_rows:
            root_to_names[row.root_so].add(row.name)

        # for each job_no, find which root it belongs to
        # then map job_no → all SO names in that chain
        for jn in job_nos:
            # job_no itself may be the root or an amended version
            for root, names in root_to_names.items():
                if jn in names or jn == root:
                    job_no_to_so_names[jn].update(names)
            # fallback: if nothing found, just use the job_no itself
            if not job_no_to_so_names[jn]:
                job_no_to_so_names[jn].add(jn)

    # ── Collect all active SO names across all invoices ────────────────
    all_so_names = set()
    for so_set in job_no_to_so_names.values():
        all_so_names.update(so_set)
    # also include direct sales_order from SI items
    all_so_names.update(s for s in sales_orders if s)

    # ── Fetch all non-cancelled POs per SO name ────────────────────────
    # so_to_pos: so_name → [list of non-cancelled PO names]
    so_to_pos = defaultdict(list)
    if all_so_names:
        placeholders_so = ", ".join(["%s"] * len(all_so_names))
        po_rows = frappe.db.sql(f"""
            SELECT DISTINCT
                poi.sales_order,
                po.name     AS purchase_order
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po
                ON po.name = poi.parent
            WHERE poi.sales_order IN ({placeholders_so})
              AND po.docstatus != 2
            ORDER BY po.creation ASC
        """, tuple(all_so_names), as_dict=True)

        for row in po_rows:
            if row.purchase_order not in so_to_pos[row.sales_order]:
                so_to_pos[row.sales_order].append(row.purchase_order)

    # ── Fetch Purchase Invoice per non-cancelled PO ────────────────────
    all_po_names = list({po for pos in so_to_pos.values() for po in pos})

    po_to_pi = {}
    if all_po_names:
        placeholders_po = ", ".join(["%s"] * len(all_po_names))
        pi_rows = frappe.db.sql(f"""
            SELECT DISTINCT
                pii.purchase_order,
                pi.name AS purchase_invoice
            FROM `tabPurchase Invoice Item` pii
            JOIN `tabPurchase Invoice` pi
                ON pi.name = pii.parent
            WHERE pii.purchase_order IN ({placeholders_po})
              AND pi.docstatus != 2
            ORDER BY pi.creation ASC
        """, tuple(all_po_names), as_dict=True)

        for row in pi_rows:
            if row.purchase_order not in po_to_pi:
                po_to_pi[row.purchase_order] = row.purchase_invoice

    # ── Fetch PO item amounts: (so_name, po_name) → amount ────────────
    po_buy_map = defaultdict(float)
    if all_so_names and all_po_names:
        placeholders_so2 = ", ".join(["%s"] * len(all_so_names))
        placeholders_po2 = ", ".join(["%s"] * len(all_po_names))
        po_items = frappe.db.sql(f"""
            SELECT
                poi.sales_order,
                poi.parent      AS purchase_order,
                SUM(poi.amount) AS amount
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po ON po.name = poi.parent
            WHERE poi.sales_order IN ({placeholders_so2})
              AND poi.parent    IN ({placeholders_po2})
              AND po.docstatus  != 2
            GROUP BY poi.sales_order, poi.parent
        """, tuple(all_so_names) + tuple(all_po_names), as_dict=True)

        for poi in po_items:
            po_buy_map[(poi.sales_order, poi.purchase_order)] = flt(poi.amount)

    # ── item map grouped by invoice ───────────────────────────────────
    item_map = defaultdict(list)
    for item in items:
        item_map[item.invoice].append(item)

    # ── Build result ───────────────────────────────────────────────────
    total_amount_view = filters.get("total_amount_view", "Invoice Based")

    result = []
    for inv in invoices:
        job_no     = inv.job_no or ""
        sell       = flt(inv.sell or 0)
        commission = flt(inv.commission or 0)

        # get all SO names for this job_no (original + amended)
        so_names_for_job = job_no_to_so_names.get(job_no, {job_no} if job_no else set())

        # collect all non-cancelled POs across all SO names for this job
        po_list = []
        so_used_per_po = {}  # po_name → so_name (for buy lookup)
        for so_name in so_names_for_job:
            for po_name in so_to_pos.get(so_name, []):
                if po_name not in po_list:
                    po_list.append(po_name)
                    so_used_per_po[po_name] = so_name

        if not po_list:
            # no PO — single row blank PO/PI
            inv_row = dict(inv)
            inv_row["indent"]           = 0
            inv_row["purchase_order"]   = ""
            inv_row["purchase_invoice"] = ""
            inv_row["buy"]              = 0.0
            inv_row["gross_margin"]     = sell
            inv_row["gross_percentage"] = 100.0 if sell else 0
            inv_row["net_margin"]       = sell - commission
            result.append(inv_row)

            if total_amount_view == "Invoice Based":
                _append_children(result, inv, item_map, 0.0, sell)
        else:
            for po_name in po_list:
                so_name = so_used_per_po.get(po_name, job_no)
                pi_name = po_to_pi.get(po_name, "")
                buy     = flt(po_buy_map.get((so_name, po_name), 0))

                inv_row = dict(inv)
                inv_row["indent"]           = 0
                inv_row["purchase_order"]   = po_name
                inv_row["purchase_invoice"] = pi_name
                inv_row["buy"]              = buy
                inv_row["gross_margin"]     = sell - buy
                inv_row["gross_percentage"] = ((sell - buy) / sell * 100) if sell else 0
                inv_row["net_margin"]       = sell - buy - commission
                result.append(inv_row)

                if total_amount_view == "Invoice Based":
                    _append_children(result, inv, item_map, buy, sell)

    return result


def _append_children(result, inv, item_map, buy_total, sell_total):
    inv_items  = item_map.get(inv.invoice, [])
    item_count = len(inv_items) or 1

    for itm in inv_items:
        item_sell = flt(itm.amount or 0)

        if sell_total:
            item_buy = buy_total * (item_sell / sell_total)
        else:
            item_buy = buy_total / item_count

        item_gross     = item_sell - item_buy
        item_gross_pct = (item_gross / item_sell * 100) if item_sell else 0.0

        child = {
            "indent":              1,
            "invoice":             itm.item_name or itm.item_code,
            "customer":            "",
            "sales_order":         "",
            "purchase_order":      "",
            "purchase_invoice":    "",
            "origin_country":      "",
            "destination_country": "",
            "mode":                "",
            "cbm":                 None,
            "weight":              None,
            "job_no":              "",
            "buy":                 item_buy,
            "sell":                item_sell,
            "gross_margin":        item_gross,
            "gross_percentage":    item_gross_pct,
            "commission":          0,
            "net_margin":          item_gross,
        }
        result.append(child)