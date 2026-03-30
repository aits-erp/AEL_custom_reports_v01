# Copyright (c) 2026, Sukku

import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():

    return [
        {"label": "Customer Name", "fieldname": "customer", "fieldtype": "Data", "width": 180},
        {"label": "Invoice Number", "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},

        {"label": "Origin Country", "fieldname": "origin_country", "fieldtype": "Data", "width": 140},
        {"label": "Destination Country", "fieldname": "destination_country", "fieldtype": "Data", "width": 160},
        {"label": "Mode", "fieldname": "mode", "fieldtype": "Data", "width": 100},

        {"label": "CBM", "fieldname": "cbm", "fieldtype": "Float", "width": 100},
        {"label": "Weight", "fieldname": "weight", "fieldtype": "Float", "width": 100},

        {"label": "Job No", "fieldname": "job_no", "fieldtype": "Data", "width": 140},

        {"label": "BUY", "fieldname": "buy", "fieldtype": "Currency", "width": 120},
        {"label": "SELL", "fieldname": "sell", "fieldtype": "Currency", "width": 120},

        {"label": "Gross Margin", "fieldname": "gross_margin", "fieldtype": "Currency", "width": 130},
        {"label": "Gross Percent", "fieldname": "gross_percentage", "fieldtype": "Percent", "width": 120},

        {"label": "Commission", "fieldname": "commission", "fieldtype": "Currency", "width": 120},
        {"label": "Net Margin", "fieldname": "net_margin", "fieldtype": "Currency", "width": 130},
    ]


def get_data(filters):

    conditions = []
    values = {}

    if filters.get("company"):
        conditions.append("si.company = %(company)s")
        values["company"] = filters.get("company")

    if filters.get("from_date"):
        conditions.append("si.posting_date >= %(from_date)s")
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions.append("si.posting_date <= %(to_date)s")
        values["to_date"] = filters.get("to_date")

    if filters.get("customer"):
        conditions.append("si.customer = %(customer)s")
        values["customer"] = filters.get("customer")

    if filters.get("sales_invoice"):
        conditions.append("si.name = %(sales_invoice)s")
        values["sales_invoice"] = filters.get("sales_invoice")

    if filters.get("item_group"):
        conditions.append("sii.item_group = %(item_group)s")
        values["item_group"] = filters.get("item_group")

    if filters.get("warehouse"):
        conditions.append("sii.warehouse = %(warehouse)s")
        values["warehouse"] = filters.get("warehouse")

    if filters.get("project"):
        conditions.append("sii.project = %(project)s")
        values["project"] = filters.get("project")

    # Invoice Type
    if filters.get("invoice_type") == "Credit Note":
        conditions.append("si.is_return = 1")
    else:
        conditions.append("IFNULL(si.is_return, 0) = 0")

    if not filters.get("include_returned"):
        conditions.append("IFNULL(si.is_return, 0) = 0")

    where_clause = ""
    if conditions:
        where_clause = " AND " + " AND ".join(conditions)

    query = """
        SELECT
            si.customer,
            si.name AS invoice,

            si.custom_country_of_origin AS origin_country,
            si.custom_country_of_destination AS destination_country,
            si.custom_mode AS mode,

            si.custom_total_cbm AS cbm,
            si.custom_total_weight AS weight,
            si.custom_job_no AS job_no,

            SUM(sii.base_net_amount) AS sell,

            SUM(
                sii.qty * IFNULL((
                    SELECT sle.valuation_rate
                    FROM `tabStock Ledger Entry` sle
                    WHERE sle.voucher_no = si.name
                    AND sle.item_code = sii.item_code
                    ORDER BY sle.posting_date DESC, sle.posting_time DESC
                    LIMIT 1
                ), 0)
            ) AS buy,

            (
                SUM(sii.base_net_amount) -
                SUM(
                    sii.qty * IFNULL((
                        SELECT sle.valuation_rate
                        FROM `tabStock Ledger Entry` sle
                        WHERE sle.voucher_no = si.name
                        AND sle.item_code = sii.item_code
                        ORDER BY sle.posting_date DESC, sle.posting_time DESC
                        LIMIT 1
                    ), 0)
                )
            ) AS gross_margin,

            CASE 
                WHEN SUM(sii.base_net_amount) > 0 THEN
                    (
                        (
                            SUM(sii.base_net_amount) -
                            SUM(
                                sii.qty * IFNULL((
                                    SELECT sle.valuation_rate
                                    FROM `tabStock Ledger Entry` sle
                                    WHERE sle.voucher_no = si.name
                                    AND sle.item_code = sii.item_code
                                    ORDER BY sle.posting_date DESC, sle.posting_time DESC
                                    LIMIT 1
                                ), 0)
                            )
                        ) / SUM(sii.base_net_amount)
                    ) * 100
                ELSE 0
            END AS gross_percentage,

            (SUM(sii.base_net_amount) * 0.02) AS commission,

            (
                (
                    SUM(sii.base_net_amount) -
                    SUM(
                        sii.qty * IFNULL((
                            SELECT sle.valuation_rate
                            FROM `tabStock Ledger Entry` sle
                            WHERE sle.voucher_no = si.name
                            AND sle.item_code = sii.item_code
                            ORDER BY sle.posting_date DESC, sle.posting_time DESC
                            LIMIT 1
                        ), 0)
                    )
                )
                - (SUM(sii.base_net_amount) * 0.02)
            ) AS net_margin

        FROM `tabSales Invoice` si

        LEFT JOIN `tabSales Invoice Item` sii 
            ON sii.parent = si.name

        WHERE si.docstatus = 1
    """ + where_clause + """
        GROUP BY si.name
        ORDER BY si.posting_date DESC
    """

    return frappe.db.sql(query, values, as_dict=True)