# # Copyright (c) 2026, Sukku

# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():

#     return [
#         {"label": "Customer Name", "fieldname": "customer", "fieldtype": "Data", "width": 180},
#         {"label": "Invoice Number", "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},

#         {"label": "Origin Country", "fieldname": "origin_country", "fieldtype": "Data", "width": 140},
#         {"label": "Destination Country", "fieldname": "destination_country", "fieldtype": "Data", "width": 160},
#         {"label": "Mode", "fieldname": "mode", "fieldtype": "Data", "width": 100},

#         {"label": "CBM", "fieldname": "cbm", "fieldtype": "Float", "width": 100},
#         {"label": "Weight", "fieldname": "weight", "fieldtype": "Float", "width": 100},

#         {"label": "Job No", "fieldname": "job_no", "fieldtype": "Data", "width": 140},

#         {"label": "BUY", "fieldname": "buy", "fieldtype": "Currency", "width": 120},
#         {"label": "SELL", "fieldname": "sell", "fieldtype": "Currency", "width": 120},

#         {"label": "Gross Margin", "fieldname": "gross_margin", "fieldtype": "Currency", "width": 130},
#         {"label": "Gross Percent", "fieldname": "gross_percentage", "fieldtype": "Percent", "width": 120},

#         {"label": "Commission", "fieldname": "commission", "fieldtype": "Currency", "width": 120},
#         {"label": "Net Margin", "fieldname": "net_margin", "fieldtype": "Currency", "width": 130},
#     ]


# def get_data(filters):

#     conditions = []
#     values = {}

#     if filters.get("company"):
#         conditions.append("si.company = %(company)s")
#         values["company"] = filters.get("company")

#     if filters.get("from_date"):
#         conditions.append("si.posting_date >= %(from_date)s")
#         values["from_date"] = filters.get("from_date")

#     if filters.get("to_date"):
#         conditions.append("si.posting_date <= %(to_date)s")
#         values["to_date"] = filters.get("to_date")

#     if filters.get("customer"):
#         conditions.append("si.customer = %(customer)s")
#         values["customer"] = filters.get("customer")

#     if filters.get("sales_invoice"):
#         conditions.append("si.name = %(sales_invoice)s")
#         values["sales_invoice"] = filters.get("sales_invoice")

#     if filters.get("item_group"):
#         conditions.append("sii.item_group = %(item_group)s")
#         values["item_group"] = filters.get("item_group")

#     if filters.get("warehouse"):
#         conditions.append("sii.warehouse = %(warehouse)s")
#         values["warehouse"] = filters.get("warehouse")

#     if filters.get("project"):
#         conditions.append("sii.project = %(project)s")
#         values["project"] = filters.get("project")

#     # Invoice Type
#     if filters.get("invoice_type") == "Credit Note":
#         conditions.append("si.is_return = 1")
#     else:
#         conditions.append("IFNULL(si.is_return, 0) = 0")

#     if not filters.get("include_returned"):
#         conditions.append("IFNULL(si.is_return, 0) = 0")

#     where_clause = ""
#     if conditions:
#         where_clause = " AND " + " AND ".join(conditions)

#     query = """
#         SELECT
#             si.customer,
#             si.name AS invoice,

#             si.custom_country_of_origin AS origin_country,
#             si.custom_country_of_destination AS destination_country,
#             si.custom_mode AS mode,

#             si.custom_total_cbm AS cbm,
#             si.custom_total_weight AS weight,
#             si.custom_job_no AS job_no,

#             SUM(sii.base_net_amount) AS sell,

#             SUM(
#                 sii.qty * IFNULL((
#                     SELECT sle.valuation_rate
#                     FROM `tabStock Ledger Entry` sle
#                     WHERE sle.voucher_no = si.name
#                     AND sle.item_code = sii.item_code
#                     ORDER BY sle.posting_date DESC, sle.posting_time DESC
#                     LIMIT 1
#                 ), 0)
#             ) AS buy,

#             (
#                 SUM(sii.base_net_amount) -
#                 SUM(
#                     sii.qty * IFNULL((
#                         SELECT sle.valuation_rate
#                         FROM `tabStock Ledger Entry` sle
#                         WHERE sle.voucher_no = si.name
#                         AND sle.item_code = sii.item_code
#                         ORDER BY sle.posting_date DESC, sle.posting_time DESC
#                         LIMIT 1
#                     ), 0)
#                 )
#             ) AS gross_margin,

#             CASE 
#                 WHEN SUM(sii.base_net_amount) > 0 THEN
#                     (
#                         (
#                             SUM(sii.base_net_amount) -
#                             SUM(
#                                 sii.qty * IFNULL((
#                                     SELECT sle.valuation_rate
#                                     FROM `tabStock Ledger Entry` sle
#                                     WHERE sle.voucher_no = si.name
#                                     AND sle.item_code = sii.item_code
#                                     ORDER BY sle.posting_date DESC, sle.posting_time DESC
#                                     LIMIT 1
#                                 ), 0)
#                             )
#                         ) / SUM(sii.base_net_amount)
#                     ) * 100
#                 ELSE 0
#             END AS gross_percentage,

#             (SUM(sii.base_net_amount) * 0.02) AS commission,

#             (
#                 (
#                     SUM(sii.base_net_amount) -
#                     SUM(
#                         sii.qty * IFNULL((
#                             SELECT sle.valuation_rate
#                             FROM `tabStock Ledger Entry` sle
#                             WHERE sle.voucher_no = si.name
#                             AND sle.item_code = sii.item_code
#                             ORDER BY sle.posting_date DESC, sle.posting_time DESC
#                             LIMIT 1
#                         ), 0)
#                     )
#                 )
#                 - (SUM(sii.base_net_amount) * 0.02)
#             ) AS net_margin

#         FROM `tabSales Invoice` si

#         LEFT JOIN `tabSales Invoice Item` sii 
#             ON sii.parent = si.name

#         WHERE si.docstatus = 1
#     """ + where_clause + """
#         GROUP BY si.name
#         ORDER BY si.posting_date DESC
#     """

#     return frappe.db.sql(query, values, as_dict=True)





# # Copyright (c) 2026, Sukku

# import frappe


# def execute(filters=None):
#     columns = get_columns()
#     data = get_data(filters or {})
#     return columns, data


# def get_columns():
#     return [
#         {"label": "Customer Name",      "fieldname": "customer",          "fieldtype": "Data",     "width": 180},
#         {"label": "Invoice Number",     "fieldname": "invoice",           "fieldtype": "Link",     "options": "Sales Invoice", "width": 160},

#         # ── NEW reference columns ──────────────────────────────────────
#         {"label": "Sales Order",        "fieldname": "sales_order",       "fieldtype": "Link",     "options": "Sales Order",    "width": 150},
#         {"label": "Purchase Order",     "fieldname": "purchase_order",    "fieldtype": "Link",     "options": "Purchase Order", "width": 150},
#         {"label": "Purchase Invoice",   "fieldname": "purchase_invoice",  "fieldtype": "Link",     "options": "Purchase Invoice","width": 160},
#         # ──────────────────────────────────────────────────────────────

#         {"label": "Origin Country",     "fieldname": "origin_country",    "fieldtype": "Data",     "width": 140},
#         {"label": "Destination Country","fieldname": "destination_country","fieldtype": "Data",    "width": 160},
#         {"label": "Mode",               "fieldname": "mode",              "fieldtype": "Data",     "width": 100},

#         {"label": "CBM",                "fieldname": "cbm",               "fieldtype": "Float",    "width": 100},
#         {"label": "Weight",             "fieldname": "weight",            "fieldtype": "Float",    "width": 100},

#         {"label": "Job No",             "fieldname": "job_no",            "fieldtype": "Data",     "width": 140},

#         {"label": "BUY",                "fieldname": "buy",               "fieldtype": "Currency", "width": 120},
#         {"label": "SELL",               "fieldname": "sell",              "fieldtype": "Currency", "width": 120},

#         {"label": "Gross Margin",       "fieldname": "gross_margin",      "fieldtype": "Currency", "width": 130},
#         {"label": "Gross Percent",      "fieldname": "gross_percentage",  "fieldtype": "Percent",  "width": 120},

#         {"label": "Commission",         "fieldname": "commission",        "fieldtype": "Currency", "width": 120},
#         {"label": "Net Margin",         "fieldname": "net_margin",        "fieldtype": "Currency", "width": 130},
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

#     # ── valuation-rate subquery (reused 4×) ───────────────────────────
#     val_sub = """(
#         SELECT sle.valuation_rate
#         FROM `tabStock Ledger Entry` sle
#         WHERE sle.voucher_no = si.name
#           AND sle.item_code  = sii.item_code
#         ORDER BY sle.posting_date DESC, sle.posting_time DESC
#         LIMIT 1
#     )"""

#     query = f"""
#         SELECT
#             si.customer,
#             si.name               AS invoice,

#             /* ── reference chain ── */
#             so_ref.sales_order    AS sales_order,
#             po_ref.purchase_order AS purchase_order,
#             pi_ref.purchase_invoice AS purchase_invoice,

#             si.custom_country_of_origin      AS origin_country,
#             si.custom_country_of_destination AS destination_country,
#             si.custom_mode                   AS mode,

#             si.custom_total_cbm    AS cbm,
#             si.custom_total_weight AS weight,
#             si.custom_job_no       AS job_no,

#             SUM(sii.base_net_amount) AS sell,

#             SUM(sii.qty * IFNULL({val_sub}, 0)) AS buy,

#             (
#                 SUM(sii.base_net_amount) -
#                 SUM(sii.qty * IFNULL({val_sub}, 0))
#             ) AS gross_margin,

#             CASE
#                 WHEN SUM(sii.base_net_amount) > 0 THEN
#                     (
#                         SUM(sii.base_net_amount) -
#                         SUM(sii.qty * IFNULL({val_sub}, 0))
#                     ) / SUM(sii.base_net_amount) * 100
#                 ELSE 0
#             END AS gross_percentage,

#             (SUM(sii.base_net_amount) * 0.02) AS commission,

#             (
#                 SUM(sii.base_net_amount) -
#                 SUM(sii.qty * IFNULL({val_sub}, 0)) -
#                 SUM(sii.base_net_amount) * 0.02
#             ) AS net_margin

#         FROM `tabSales Invoice` si

#         LEFT JOIN `tabSales Invoice Item` sii
#             ON sii.parent = si.name

#         /* ── Sales Order: first SO reference found on any SI item ── */
#         LEFT JOIN (
#             SELECT
#                 parent AS invoice,
#                 MIN(sales_order) AS sales_order
#             FROM `tabSales Invoice Item`
#             WHERE sales_order IS NOT NULL AND sales_order != ''
#             GROUP BY parent
#         ) so_ref ON so_ref.invoice = si.name

#         /* ── Purchase Order: walk SO → PO ── */
#         LEFT JOIN (
#             SELECT
#                 so.name   AS sales_order,
#                 poi.parent AS purchase_order
#             FROM `tabSales Order`   so
#             JOIN `tabPurchase Order Item` poi ON poi.sales_order = so.name
#             GROUP BY so.name, poi.parent
#         ) po_chain ON po_chain.sales_order = so_ref.sales_order

#         LEFT JOIN (
#             SELECT sales_order, MIN(parent) AS purchase_order
#             FROM `tabPurchase Order Item`
#             WHERE sales_order IS NOT NULL AND sales_order != ''
#             GROUP BY sales_order
#         ) po_ref ON po_ref.sales_order = so_ref.sales_order

#         /* ── Purchase Invoice: walk PO → PI ── */
#         LEFT JOIN (
#             SELECT
#                 poi_item.purchase_order AS purchase_order,
#                 MIN(pi_item.parent)     AS purchase_invoice
#             FROM (
#                 SELECT DISTINCT parent AS purchase_order
#                 FROM `tabPurchase Invoice Item`
#                 WHERE purchase_order IS NOT NULL AND purchase_order != ''
#             ) poi_item
#             JOIN `tabPurchase Invoice Item` pi_item
#                 ON pi_item.purchase_order = poi_item.purchase_order
#             GROUP BY poi_item.purchase_order
#         ) pi_ref ON pi_ref.purchase_order = po_ref.purchase_order

#         WHERE si.docstatus = 1
#         {where_clause}
#         GROUP BY si.name
#         ORDER BY si.posting_date DESC
#     """

#     invoices = frappe.db.sql(query, values, as_dict=True)

#     # ── Fetch item rows for expandable child rows ──────────────────────
#     if not invoices:
#         return invoices

#     invoice_names = [d.invoice for d in invoices]
#     placeholders  = ", ".join(["%s"] * len(invoice_names))

#     items = frappe.db.sql(f"""
#         SELECT
#             sii.parent        AS invoice,
#             sii.item_code,
#             sii.item_name,
#             sii.description,
#             sii.qty,
#             sii.uom,
#             sii.rate,
#             sii.base_net_amount AS amount,
#             sii.item_group,
#             sii.warehouse
#         FROM `tabSales Invoice Item` sii
#         WHERE sii.parent IN ({placeholders})
#         ORDER BY sii.parent, sii.idx
#     """, tuple(invoice_names), as_dict=True)

#     # Build lookup: invoice → [items]
#     from collections import defaultdict
#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     # ── Build tree: parent rows + indented child rows ──────────────────
#     result = []
#     for inv in invoices:
#         inv["indent"] = 0
#         result.append(inv)

#         for itm in item_map.get(inv.invoice, []):
#             child = {
#                 "indent":             1,
#                 "customer":           itm.item_name or itm.item_code,
#                 "invoice":            "",
#                 "sales_order":        "",
#                 "purchase_order":     "",
#                 "purchase_invoice":   "",
#                 "origin_country":     itm.item_group  or "",
#                 "destination_country":itm.warehouse   or "",
#                 "mode":               itm.uom         or "",
#                 "cbm":                0,
#                 "weight":             0,
#                 "job_no":             itm.item_code   or "",
#                 "buy":                0,
#                 "sell":               itm.amount      or 0,
#                 "gross_margin":       0,
#                 "gross_percentage":   0,
#                 "commission":         0,
#                 "net_margin":         0,
#             }
#             result.append(child)

#     return result



# Copyright (c) 2026, Sukku

import frappe
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"label": "Customer Name",       "fieldname": "customer",           "fieldtype": "Data",     "width": 180},
        {"label": "Invoice Number",      "fieldname": "invoice",            "fieldtype": "Link",     "options": "Sales Invoice", "width": 160},

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

    val_sub = """(
        SELECT sle.valuation_rate
        FROM `tabStock Ledger Entry` sle
        WHERE sle.voucher_no = si.name
          AND sle.item_code  = sii.item_code
        ORDER BY sle.posting_date DESC, sle.posting_time DESC
        LIMIT 1
    )"""

    query = f"""
        SELECT
            si.customer,
            si.name                          AS invoice,

            so_ref.sales_order               AS sales_order,
            po_ref.purchase_order            AS purchase_order,
            pi_ref.purchase_invoice          AS purchase_invoice,

            si.custom_country_of_origin      AS origin_country,
            si.custom_country_of_destination AS destination_country,
            si.custom_mode                   AS mode,

            si.custom_total_cbm              AS cbm,
            si.custom_total_weight           AS weight,
            si.custom_job_no                 AS job_no,

            SUM(sii.base_net_amount)         AS sell,

            SUM(sii.qty * IFNULL({val_sub}, 0)) AS buy,

            (
                SUM(sii.base_net_amount) -
                SUM(sii.qty * IFNULL({val_sub}, 0))
            ) AS gross_margin,

            CASE
                WHEN SUM(sii.base_net_amount) > 0 THEN
                    (
                        SUM(sii.base_net_amount) -
                        SUM(sii.qty * IFNULL({val_sub}, 0))
                    ) / SUM(sii.base_net_amount) * 100
                ELSE 0
            END AS gross_percentage,

            (SUM(sii.base_net_amount) * 0.02) AS commission,

            (
                SUM(sii.base_net_amount) -
                SUM(sii.qty * IFNULL({val_sub}, 0)) -
                SUM(sii.base_net_amount) * 0.02
            ) AS net_margin

        FROM `tabSales Invoice` si

        LEFT JOIN `tabSales Invoice Item` sii
            ON sii.parent = si.name

        LEFT JOIN (
            SELECT parent AS invoice, MIN(sales_order) AS sales_order
            FROM `tabSales Invoice Item`
            WHERE sales_order IS NOT NULL AND sales_order != ''
            GROUP BY parent
        ) so_ref ON so_ref.invoice = si.name

        LEFT JOIN (
            SELECT sales_order, MIN(parent) AS purchase_order
            FROM `tabPurchase Order Item`
            WHERE sales_order IS NOT NULL AND sales_order != ''
            GROUP BY sales_order
        ) po_ref ON po_ref.sales_order = so_ref.sales_order

        LEFT JOIN (
            SELECT purchase_order, MIN(parent) AS purchase_invoice
            FROM `tabPurchase Invoice Item`
            WHERE purchase_order IS NOT NULL AND purchase_order != ''
            GROUP BY purchase_order
        ) pi_ref ON pi_ref.purchase_order = po_ref.purchase_order

        WHERE si.docstatus = 1
        {where_clause}
        GROUP BY si.name
        ORDER BY si.posting_date DESC
    """

    invoices = frappe.db.sql(query, values, as_dict=True)

    if not invoices:
        return []

    invoice_names = [d.invoice for d in invoices]
    placeholders  = ", ".join(["%s"] * len(invoice_names))

    items = frappe.db.sql(f"""
        SELECT
            sii.parent          AS invoice,
            sii.item_code,
            sii.item_name,
            sii.description,
            sii.qty,
            sii.uom,
            sii.rate,
            sii.base_net_amount AS amount,
            sii.item_group,
            sii.warehouse
        FROM `tabSales Invoice Item` sii
        WHERE sii.parent IN ({placeholders})
        ORDER BY sii.parent, sii.idx
    """, tuple(invoice_names), as_dict=True)

    item_map = defaultdict(list)
    for item in items:
        item_map[item.invoice].append(item)

    result = []
    for inv in invoices:
        inv["indent"] = 0
        result.append(inv)

        for itm in item_map.get(inv.invoice, []):
            child = {
                "indent":             1,
                # first column gets item name — Frappe tree arrow always on col 1
                "customer":           itm.item_name or itm.item_code,
                # invoice is a Link field — must stay blank on child rows
                "invoice":            "",
                "sales_order":        "",
                "purchase_order":     "",
                "purchase_invoice":   "",
                "origin_country":     itm.item_group or "",
                "destination_country":itm.warehouse  or "",
                "mode":               itm.uom        or "",
                "cbm":                itm.qty        or 0,
                "weight":             0,
                "job_no":             itm.item_code  or "",
                "buy":                0,
                "sell":               itm.amount     or 0,
                "gross_margin":       0,
                "gross_percentage":   0,
                "commission":         0,
                "net_margin":         0,
            }
            result.append(child)

    return result