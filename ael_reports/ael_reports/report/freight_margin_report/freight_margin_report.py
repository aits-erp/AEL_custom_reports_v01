# import frappe
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

#     invoice_names = [d.invoice for d in invoices]
#     placeholders  = ", ".join(["%s"] * len(invoice_names))

#     items = frappe.db.sql(f"""
#         SELECT
#             sii.parent          AS invoice,
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

#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     result = []
#     for inv in invoices:
#         inv["indent"] = 0
#         result.append(inv)

#         for itm in item_map.get(inv.invoice, []):
#             child = {
#                 "indent": 1,

#                 # ── BEFORE buy: only invoice col has item name (tree label) ──
#                 # all other columns before buy are empty
#                 "invoice":             itm.item_name or itm.item_code,
#                 "customer":            "",
#                 "sales_order":         "",
#                 "purchase_order":      "",
#                 "purchase_invoice":    "",
#                 "origin_country":      "",
#                 "destination_country": "",
#                 "mode":                "",
#                 "cbm":                 None,   # None so Float column shows blank
#                 "weight":              None,   # None so Float column shows blank
#                 "job_no":              "",

#                 # ── FROM buy onwards: show item values ────────────────────
#                 "buy":                 0,
#                 "sell":                itm.amount or 0,
#                 "gross_margin":        0,
#                 "gross_percentage":    0,
#                 "commission":          0,
#                 "net_margin":          0,
#             }
#             result.append(child)

#     return result


# import frappe
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

#             -- ── commission: read directly from Sales Invoice custom field ──
#             IFNULL(si.custom_commission, 0) AS commission,

#             (
#                 SUM(sii.base_net_amount) -
#                 SUM(sii.qty * IFNULL({val_sub}, 0)) -
#                 IFNULL(si.custom_commission, 0)
#             ) AS net_margin

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

#     invoice_names = [d.invoice for d in invoices]
#     placeholders  = ", ".join(["%s"] * len(invoice_names))

#     items = frappe.db.sql(f"""
#         SELECT
#             sii.parent          AS invoice,
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

#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     result = []
#     for inv in invoices:
#         inv["indent"] = 0
#         result.append(inv)

#         for itm in item_map.get(inv.invoice, []):
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
#                 "buy":                 0,
#                 "sell":                itm.amount or 0,
#                 "gross_margin":        0,
#                 "gross_percentage":    0,
#                 "commission":          0,
#                 "net_margin":          0,
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
            po_ref.purchase_order            AS purchase_order,
            pi_ref.purchase_invoice          AS purchase_invoice,

            si.custom_country_of_origin      AS origin_country,
            si.custom_country_of_destination AS destination_country,
            si.custom_mode                   AS mode,

            si.custom_total_cbm              AS cbm,
            si.custom_total_weight           AS weight,
            si.custom_job_no                 AS job_no,

            SUM(sii.base_net_amount)         AS sell,

            IFNULL(pi_doc.total, 0)          AS buy,

            (
                SUM(sii.base_net_amount) -
                IFNULL(pi_doc.total, 0)
            ) AS gross_margin,

            CASE
                WHEN SUM(sii.base_net_amount) > 0 THEN
                    (
                        SUM(sii.base_net_amount) -
                        IFNULL(pi_doc.total, 0)
                    ) / SUM(sii.base_net_amount) * 100
                ELSE 0
            END AS gross_percentage,

            IFNULL(si.custom_commission, 0) AS commission,

            (
                SUM(sii.base_net_amount) -
                IFNULL(pi_doc.total, 0) -
                IFNULL(si.custom_commission, 0)
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

        LEFT JOIN `tabPurchase Invoice` pi_doc
            ON pi_doc.name = pi_ref.purchase_invoice
           AND pi_doc.docstatus = 1

        WHERE si.docstatus = 1
        {where_clause}
        GROUP BY si.name
        ORDER BY si.posting_date DESC
    """

    invoices = frappe.db.sql(query, values, as_dict=True)

    if not invoices:
        return []

    # "Total Based": collapsed, parent rows only, no child items
    total_amount_view = filters.get("total_amount_view", "Invoice Based")
    if total_amount_view == "Total Based":
        for inv in invoices:
            inv["indent"] = 0
        return invoices

    # "Invoice Based": expandable child item rows
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
                "buy":                 0,
                "sell":                itm.amount or 0,
                "gross_margin":        0,
                "gross_percentage":    0,
                "commission":          0,
                "net_margin":          0,
            }
            result.append(child)

    return result