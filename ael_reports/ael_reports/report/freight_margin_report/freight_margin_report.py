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

#             IFNULL(pi_doc.total, 0)          AS buy,

#             (
#                 SUM(sii.base_net_amount) -
#                 IFNULL(pi_doc.total, 0)
#             ) AS gross_margin,

#             CASE
#                 WHEN SUM(sii.base_net_amount) > 0 THEN
#                     (
#                         SUM(sii.base_net_amount) -
#                         IFNULL(pi_doc.total, 0)
#                     ) / SUM(sii.base_net_amount) * 100
#                 ELSE 0
#             END AS gross_percentage,

#             IFNULL(si.custom_commission, 0) AS commission,

#             (
#                 SUM(sii.base_net_amount) -
#                 IFNULL(pi_doc.total, 0) -
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

#         LEFT JOIN `tabPurchase Invoice` pi_doc
#             ON pi_doc.name = pi_ref.purchase_invoice
#            AND pi_doc.docstatus = 1

#         WHERE si.docstatus = 1
#         {where_clause}
#         GROUP BY si.name
#         ORDER BY si.posting_date DESC
#     """

#     invoices = frappe.db.sql(query, values, as_dict=True)

#     if not invoices:
#         return []

#     # "Total Based": collapsed, parent rows only, no child items
#     total_amount_view = filters.get("total_amount_view", "Invoice Based")
#     if total_amount_view == "Total Based":
#         for inv in invoices:
#             inv["indent"] = 0
#         return invoices

#     # "Invoice Based": expandable child item rows
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

#     invoice_names   = [d.invoice          for d in invoices]
#     pi_names        = [d.purchase_invoice  for d in invoices if d.purchase_invoice]
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

#     # ── Fetch PI items: amount per (purchase_invoice, item_code) ──────
#     pi_buy_map = {}
#     if pi_names:
#         placeholders_pi = ", ".join(["%s"] * len(pi_names))
#         pi_items = frappe.db.sql(f"""
#             SELECT
#                 pii.parent    AS purchase_invoice,
#                 pii.item_code,
#                 pii.amount
#             FROM `tabPurchase Invoice Item` pii
#             WHERE pii.parent IN ({placeholders_pi})
#             ORDER BY pii.parent, pii.idx
#         """, tuple(pi_names), as_dict=True)

#         for pi in pi_items:
#             key = (pi.purchase_invoice, pi.item_code)
#             pi_buy_map[key] = pi_buy_map.get(key, 0.0) + flt(pi.amount)

#     # ── invoice → purchase_invoice lookup ─────────────────────────────
#     inv_to_pi = {d.invoice: d.purchase_invoice for d in invoices}

#     # ── item map grouped by invoice ───────────────────────────────────
#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     # ── Calculate buy per invoice summing matched PI item amounts ──────
#     inv_buy_map = {}
#     for inv in invoices:
#         pi_name = inv_to_pi.get(inv.invoice)
#         if not pi_name:
#             inv_buy_map[inv.invoice] = 0.0
#             continue
#         total_buy = 0.0
#         for itm in item_map.get(inv.invoice, []):
#             key = (pi_name, itm.item_code)
#             total_buy += pi_buy_map.get(key, 0.0)
#         inv_buy_map[inv.invoice] = total_buy

#     # ── Attach calculated fields ───────────────────────────────────────
#     for inv in invoices:
#         buy        = flt(inv_buy_map.get(inv.invoice, 0))
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

#         pi_name = inv_to_pi.get(inv.invoice)

#         for itm in item_map.get(inv.invoice, []):
#             item_buy       = flt(pi_buy_map.get((pi_name, itm.item_code), 0)) if pi_name else 0.0
#             item_sell      = flt(itm.amount or 0)
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

#     # ── Main invoice query — no PO/PI join here, done in Python ───────
#     query = f"""
#         SELECT
#             si.name                          AS invoice,
#             si.customer,

#             so_ref.sales_order               AS sales_order,

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

#         WHERE si.docstatus = 1
#         {where_clause}
#         GROUP BY si.name
#         ORDER BY si.posting_date DESC
#     """

#     invoices = frappe.db.sql(query, values, as_dict=True)

#     if not invoices:
#         return []

#     invoice_names   = [d.invoice for d in invoices]
#     job_nos         = [d.job_no  for d in invoices if d.job_no]
#     sales_orders    = [d.sales_order for d in invoices if d.sales_order]

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

#     # ── Fetch all non-cancelled POs per sales_order ────────────────────
#     # so_to_pos: sales_order → [list of non-cancelled PO names]
#     so_to_pos = defaultdict(list)
#     if sales_orders:
#         placeholders_so = ", ".join(["%s"] * len(sales_orders))
#         po_rows = frappe.db.sql(f"""
#             SELECT DISTINCT
#                 poi.sales_order,
#                 po.name  AS purchase_order
#             FROM `tabPurchase Order Item` poi
#             JOIN `tabPurchase Order` po
#                 ON po.name = poi.parent
#             WHERE poi.sales_order IN ({placeholders_so})
#               AND po.docstatus != 2
#             ORDER BY po.creation ASC
#         """, tuple(sales_orders), as_dict=True)

#         for row in po_rows:
#             so_to_pos[row.sales_order].append(row.purchase_order)

#     # ── Fetch Purchase Invoice per non-cancelled PO ────────────────────
#     # po_to_pi: purchase_order → purchase_invoice (non-cancelled)
#     all_po_names = []
#     for pos in so_to_pos.values():
#         all_po_names.extend(pos)
#     all_po_names = list(set(all_po_names))

#     po_to_pi = {}
#     if all_po_names:
#         placeholders_po = ", ".join(["%s"] * len(all_po_names))
#         pi_rows = frappe.db.sql(f"""
#             SELECT DISTINCT
#                 pii.purchase_order,
#                 pi.name AS purchase_invoice
#             FROM `tabPurchase Invoice Item` pii
#             JOIN `tabPurchase Invoice` pi
#                 ON pi.name = pii.parent
#             WHERE pii.purchase_order IN ({placeholders_po})
#               AND pi.docstatus != 2
#             ORDER BY pi.creation ASC
#         """, tuple(all_po_names), as_dict=True)

#         for row in pi_rows:
#             # keep first non-cancelled PI per PO
#             if row.purchase_order not in po_to_pi:
#                 po_to_pi[row.purchase_order] = row.purchase_invoice

#     # ── Fetch PO item amounts by job_no (sales_order) ─────────────────
#     # po_buy_map: (sales_order, purchase_order) → amount
#     po_buy_map = defaultdict(float)
#     if job_nos and all_po_names:
#         placeholders_jo = ", ".join(["%s"] * len(job_nos))
#         placeholders_po2 = ", ".join(["%s"] * len(all_po_names))
#         po_items = frappe.db.sql(f"""
#             SELECT
#                 poi.sales_order,
#                 poi.parent AS purchase_order,
#                 SUM(poi.amount) AS amount
#             FROM `tabPurchase Order Item` poi
#             JOIN `tabPurchase Order` po ON po.name = poi.parent
#             WHERE poi.sales_order IN ({placeholders_jo})
#               AND poi.parent    IN ({placeholders_po2})
#               AND po.docstatus  != 2
#             GROUP BY poi.sales_order, poi.parent
#         """, tuple(job_nos) + tuple(all_po_names), as_dict=True)

#         for poi in po_items:
#             po_buy_map[(poi.sales_order, poi.purchase_order)] = flt(poi.amount)

#     # ── item map grouped by invoice ───────────────────────────────────
#     item_map = defaultdict(list)
#     for item in items:
#         item_map[item.invoice].append(item)

#     # ── Build result ───────────────────────────────────────────────────
#     total_amount_view = filters.get("total_amount_view", "Invoice Based")

#     result = []
#     for inv in invoices:
#         so       = inv.sales_order or ""
#         job_no   = inv.job_no or ""
#         sell     = flt(inv.sell or 0)
#         commission = flt(inv.commission or 0)

#         # get all non-cancelled POs for this SO
#         po_list  = so_to_pos.get(so, [])

#         if not po_list:
#             # no PO at all — single row, blank PO/PI
#             buy = 0.0
#             inv_row = dict(inv)
#             inv_row["indent"]           = 0
#             inv_row["purchase_order"]   = ""
#             inv_row["purchase_invoice"] = ""
#             inv_row["buy"]              = buy
#             inv_row["gross_margin"]     = sell - buy
#             inv_row["gross_percentage"] = ((sell - buy) / sell * 100) if sell else 0
#             inv_row["net_margin"]       = sell - buy - commission
#             result.append(inv_row)

#             if total_amount_view == "Invoice Based":
#                 _append_children(result, inv, item_map, buy, sell)

#         else:
#             # one row per non-cancelled PO
#             for idx, po_name in enumerate(po_list):
#                 pi_name = po_to_pi.get(po_name, "")
#                 buy     = flt(po_buy_map.get((job_no, po_name), 0))

#                 inv_row = dict(inv)
#                 inv_row["indent"]           = 0
#                 inv_row["purchase_order"]   = po_name
#                 inv_row["purchase_invoice"] = pi_name
#                 inv_row["buy"]              = buy
#                 inv_row["gross_margin"]     = sell - buy
#                 inv_row["gross_percentage"] = ((sell - buy) / sell * 100) if sell else 0
#                 inv_row["net_margin"]       = sell - buy - commission
#                 result.append(inv_row)

#                 if total_amount_view == "Invoice Based":
#                     _append_children(result, inv, item_map, buy, sell)

#     return result


# def _append_children(result, inv, item_map, buy_total, sell_total):
#     """Append indented child item rows under a parent invoice row."""
#     inv_items  = item_map.get(inv.invoice, [])
#     item_count = len(inv_items) or 1

#     for itm in inv_items:
#         item_sell = flt(itm.amount or 0)

#         if sell_total:
#             item_buy = buy_total * (item_sell / sell_total)
#         else:
#             item_buy = buy_total / item_count

#         item_gross     = item_sell - item_buy
#         item_gross_pct = (item_gross / item_sell * 100) if item_sell else 0.0

#         child = {
#             "indent":              1,
#             "invoice":             itm.item_name or itm.item_code,
#             "customer":            "",
#             "sales_order":         "",
#             "purchase_order":      "",
#             "purchase_invoice":    "",
#             "origin_country":      "",
#             "destination_country": "",
#             "mode":                "",
#             "cbm":                 None,
#             "weight":              None,
#             "job_no":              "",
#             "buy":                 item_buy,
#             "sell":                item_sell,
#             "gross_margin":        item_gross,
#             "gross_percentage":    item_gross_pct,
#             "commission":          0,
#             "net_margin":          item_gross,
#         }
#         result.append(child)



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
    job_nos       = list(set([d.job_no      for d in invoices if d.job_no]))
    sales_orders  = list(set([d.sales_order for d in invoices if d.sales_order]))

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

    # ── Build SO amendment chain ───────────────────────────────────────
    # For each job_no find ALL SO names in amendment chain
    # including amended versions (LCLIMP0482, LCLIMP0482-1, LCLIMP0482-2)
    # so_name_to_job_no: any SO name → original job_no
    # job_no_to_all_so: job_no → set of all SO names in chain
    so_name_to_job_no = {}
    job_no_to_all_so  = defaultdict(set)

    if job_nos:
        placeholders_jn = ", ".join(["%s"] * len(job_nos))

        # Step 1: find all SOs whose name = job_no (direct match)
        # and all SOs that are amendments of job_no
        so_rows = frappe.db.sql(f"""
            SELECT name, amended_from
            FROM `tabSales Order`
            WHERE name IN ({placeholders_jn})
               OR amended_from IN ({placeholders_jn})
        """, tuple(job_nos) * 2, as_dict=True)

        for row in so_rows:
            # if this SO's name is a job_no → it is the root
            if row.name in job_nos:
                job_no_to_all_so[row.name].add(row.name)
                so_name_to_job_no[row.name] = row.name
            # if this SO was amended from a job_no → add it to that chain
            if row.amended_from and row.amended_from in job_nos:
                job_no_to_all_so[row.amended_from].add(row.name)
                so_name_to_job_no[row.name] = row.amended_from

        # Step 2: go one more level deep
        # e.g. LCLIMP0482 → LCLIMP0482-1 → LCLIMP0482-2
        level2_so = set()
        for so_set in job_no_to_all_so.values():
            level2_so.update(so_set)

        if level2_so:
            placeholders_l2 = ", ".join(["%s"] * len(level2_so))
            l2_rows = frappe.db.sql(f"""
                SELECT name, amended_from
                FROM `tabSales Order`
                WHERE amended_from IN ({placeholders_l2})
            """, tuple(level2_so), as_dict=True)

            for row in l2_rows:
                parent_jn = so_name_to_job_no.get(row.amended_from)
                if parent_jn:
                    job_no_to_all_so[parent_jn].add(row.name)
                    so_name_to_job_no[row.name] = parent_jn

        # fallback: job_no with no amendments found
        for jn in job_nos:
            if not job_no_to_all_so[jn]:
                job_no_to_all_so[jn].add(jn)
                so_name_to_job_no[jn] = jn

    # ── All SO names to search POs ─────────────────────────────────────
    all_so_names = set(sales_orders)
    for so_set in job_no_to_all_so.values():
        all_so_names.update(so_set)
    all_so_names = list(all_so_names)

    # ── Fetch all non-cancelled POs per SO ────────────────────────────
    # so_to_pos: so_name → [list of non-cancelled PO names]
    so_to_pos = defaultdict(list)
    if all_so_names:
        placeholders_so = ", ".join(["%s"] * len(all_so_names))
        po_rows = frappe.db.sql(f"""
            SELECT DISTINCT
                poi.sales_order,
                po.name  AS purchase_order
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
    all_po_names = list(set(po for pos in so_to_pos.values() for po in pos))

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

    # ── Fetch PO item amounts ──────────────────────────────────────────
    # key: (so_name, po_name) → amount
    # so_name here is whatever the PO item has in sales_order field
    # (could be LCLIMP0482-1 not LCLIMP0482)
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

        # all SO names in amendment chain for this job_no
        all_so_for_job = job_no_to_all_so.get(job_no, {job_no} if job_no else set())

        # collect all non-cancelled POs across all SO names in chain
        # po_name → so_name that the PO item references
        po_list        = []
        po_to_so_name  = {}
        for so_name in all_so_for_job:
            for po_name in so_to_pos.get(so_name, []):
                if po_name not in po_list:
                    po_list.append(po_name)
                    po_to_so_name[po_name] = so_name

        # also check direct sales_order from SI item
        direct_so = inv.sales_order or ""
        if direct_so and direct_so not in all_so_for_job:
            for po_name in so_to_pos.get(direct_so, []):
                if po_name not in po_list:
                    po_list.append(po_name)
                    po_to_so_name[po_name] = direct_so

        if not po_list:
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
                # so_name = the exact SO name stored in PO item's sales_order field
                so_name = po_to_so_name.get(po_name, job_no)
                pi_name = po_to_pi.get(po_name, "")

                # buy: use exact so_name from PO item — this is the key fix
                # PO item stores LCLIMP0482-1 not LCLIMP0482
                buy = flt(po_buy_map.get((so_name, po_name), 0))

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