# from __future__ import unicode_literals

# import frappe
# from frappe import _


# def execute(filters=None):
#     filters = frappe._dict(filters or {})

#     validate_filters(filters)

#     columns = get_columns()
#     data = get_data(filters)

#     # Add our own total row
#     if data:
#         data.append(get_total_row(data))

#     return columns, data


# # ======================================================================
# # VALIDATION
# # ======================================================================

# def validate_filters(filters):

#     if not filters.get("from_date"):
#         frappe.throw(_("From Date is mandatory."))

#     if not filters.get("to_date"):
#         frappe.throw(_("To Date is mandatory."))

#     if filters.from_date > filters.to_date:
#         frappe.throw(
#             _("From Date cannot be greater than To Date.")
#         )


# # ======================================================================
# # COLUMNS
# # ======================================================================

# def get_columns():

#     return [
#         {
#             "fieldname": "date",
#             "label": _("Date"),
#             "fieldtype": "Date",
#             "width": 95
#         },
#         {
#             "fieldname": "particulars",
#             "label": _("Particulars"),
#             "fieldtype": "Link",
#             "options": "Supplier",
#             "width": 220
#         },
#         {
#             "fieldname": "voucher_type",
#             "label": _("Voucher Type"),
#             "fieldtype": "Data",
#             "width": 140
#         },
#         {
#             "fieldname": "voucher_no",
#             "label": _("Voucher No."),
#             "fieldtype": "Link",
#             "options": "Purchase Invoice",
#             "width": 180
#         },
#         {
#             "fieldname": "voucher_ref_no",
#             "label": _("Voucher Ref. No."),
#             "fieldtype": "Data",
#             "width": 170
#         },
#         {
#             "fieldname": "gross_total",
#             "label": _("Gross Total"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "purchase_18",
#             "label": _("Purchase 18%"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "input_cgst_9",
#             "label": _("INPUT CGST 9%"),
#             "fieldtype": "Currency",
#             "width": 125
#         },
#         {
#             "fieldname": "input_sgst_9",
#             "label": _("INPUT SGST 9%"),
#             "fieldtype": "Currency",
#             "width": 125
#         },
#         {
#             "fieldname": "tds_2",
#             "label": _("94 C Tds Payable 2%"),
#             "fieldtype": "Currency",
#             "width": 145
#         },
#         {
#             "fieldname": "purchase_non_taxable",
#             "label": _("Purchase Non Taxable"),
#             "fieldtype": "Currency",
#             "width": 150
#         },
#         {
#             "fieldname": "input_igst_18",
#             "label": _("INPUT IGST 18%"),
#             "fieldtype": "Currency",
#             "width": 125
#         },
#         {
#             "fieldname": "round_off",
#             "label": _("Round Off"),
#             "fieldtype": "Currency",
#             "width": 100
#         },
#         {
#             "fieldname": "purchase_5",
#             "label": _("Purchase 5%"),
#             "fieldtype": "Currency",
#             "width": 120
#         },
#         {
#             "fieldname": "input_cgst_2_5",
#             "label": _("INPUT CGST 2.5%"),
#             "fieldtype": "Currency",
#             "width": 135
#         },
#         {
#             "fieldname": "input_sgst_2_5",
#             "label": _("Input Sgst 2.5%"),
#             "fieldtype": "Currency",
#             "width": 135
#         },
#         {
#             "fieldname": "tds_1",
#             "label": _("94 C Tds Payable 1%"),
#             "fieldtype": "Currency",
#             "width": 145
#         },
#         {
#             "fieldname": "interest_on_tds",
#             "label": _("Interest on TDS"),
#             "fieldtype": "Currency",
#             "width": 125
#         }
#     ]


# # ======================================================================
# # GET PURCHASE INVOICES
# # ======================================================================

# def get_data(filters):

#     conditions = [
#         "pi.docstatus = 1",
#         "pi.posting_date BETWEEN %(from_date)s AND %(to_date)s"
#     ]

#     values = {
#         "from_date": filters.from_date,
#         "to_date": filters.to_date
#     }

#     if filters.get("supplier"):
#         conditions.append(
#             "pi.supplier = %(supplier)s"
#         )

#         values["supplier"] = filters.supplier

#     where_clause = " AND ".join(conditions)

#     invoices = frappe.db.sql(
#         """
#         SELECT
#             pi.name,
#             pi.posting_date,
#             pi.supplier,
#             pi.bill_no,
#             pi.net_total,
#             pi.grand_total,
#             pi.rounding_adjustment

#         FROM `tabPurchase Invoice` pi

#         WHERE {where_clause}

#         ORDER BY
#             pi.posting_date ASC,
#             pi.name ASC
#         """.format(
#             where_clause=where_clause
#         ),
#         values,
#         as_dict=True
#     )

#     if not invoices:
#         return []

#     invoice_names = [
#         invoice.name
#         for invoice in invoices
#     ]

#     # --------------------------------------------------------------
#     # Get actual Purchase Taxes and Charges fields
#     # from your ERPNext v15 database.
#     # --------------------------------------------------------------

#     taxes = frappe.db.sql(
#         """
#         SELECT
#             parent,
#             name,
#             idx,
#             category,
#             add_deduct_tax,
#             charge_type,
#             row_id,
#             account_head,
#             description,
#             is_tax_withholding_account,
#             rate,
#             gst_tax_type,
#             tax_amount,
#             tax_amount_after_discount_amount,
#             total,
#             base_tax_amount,
#             base_total,
#             base_tax_amount_after_discount_amount,
#             item_wise_tax_detail

#         FROM `tabPurchase Taxes and Charges`

#         WHERE parent IN %(parents)s

#         ORDER BY
#             parent,
#             idx
#         """,
#         {
#             "parents": invoice_names
#         },
#         as_dict=True
#     )

#     taxes_by_invoice = {}

#     for tax in taxes:
#         taxes_by_invoice.setdefault(
#             tax.parent,
#             []
#         ).append(tax)

#     data = []

#     for invoice in invoices:

#         invoice_taxes = taxes_by_invoice.get(
#             invoice.name,
#             []
#         )

#         row = calculate_invoice(
#             invoice,
#             invoice_taxes
#         )

#         data.append(row)

#     return data


# # ======================================================================
# # CALCULATE ONE INVOICE
# # ======================================================================

# def calculate_invoice(invoice, taxes):

#     input_cgst_9 = 0
#     input_sgst_9 = 0
#     input_igst_18 = 0

#     input_cgst_2_5 = 0
#     input_sgst_2_5 = 0

#     tds_2 = 0
#     tds_1 = 0
#     interest_on_tds = 0

#     # --------------------------------------------------------------
#     # Taxable purchase bases
#     # --------------------------------------------------------------

#     purchase_base_18 = 0
#     purchase_base_5 = 0

#     # All GST taxable bases.
#     # This is used to calculate non-taxable purchase.
#     gst_bases = {}

#     # --------------------------------------------------------------
#     # Round Off comes directly from Purchase Invoice
#     # --------------------------------------------------------------

#     round_off = flt(
#         invoice.rounding_adjustment
#     )

#     # --------------------------------------------------------------
#     # Process every Purchase Taxes and Charges row
#     # --------------------------------------------------------------

#     for tax in taxes:

#         rate = flt(tax.rate)

#         tax_amount = get_tax_amount(tax)

#         account_head = (
#             tax.account_head or ""
#         ).strip()

#         description = (
#             tax.description or ""
#         ).strip()

#         gst_tax_type = (
#             tax.gst_tax_type or ""
#         ).strip()

#         account_text = (
#             account_head
#             + " "
#             + description
#             + " "
#             + gst_tax_type
#         ).lower()

#         # ==========================================================
#         # INTEREST ON TDS
#         # ==========================================================

#         if (
#             "interest" in account_text
#             and "tds" in account_text
#         ):
#             interest_on_tds += tax_amount
#             continue

#         # ==========================================================
#         # TDS
#         #
#         # Use ERPNext's actual:
#         # is_tax_withholding_account
#         #
#         # No supplier/account name hardcoding.
#         # ==========================================================

#         if (
#             cint(tax.is_tax_withholding_account)
#             or "tds" in account_text
#             or "withholding" in account_text
#         ):

#             if nearly_equal(rate, 2):
#                 tds_2 += tax_amount

#             elif nearly_equal(rate, 1):
#                 tds_1 += tax_amount

#             continue

#         # ==========================================================
#         # CGST 9%
#         # ==========================================================

#         if (
#             "cgst" in account_text
#             and nearly_equal(rate, 9)
#         ):

#             input_cgst_9 += tax_amount

#             taxable_base = get_taxable_base(
#                 tax,
#                 tax_amount,
#                 rate
#             )

#             purchase_base_18 += taxable_base

#             add_gst_base(
#                 gst_bases,
#                 "CGST",
#                 rate,
#                 taxable_base
#             )

#             continue

#         # ==========================================================
#         # SGST 9%
#         # ==========================================================

#         if (
#             "sgst" in account_text
#             and nearly_equal(rate, 9)
#         ):

#             input_sgst_9 += tax_amount

#             taxable_base = get_taxable_base(
#                 tax,
#                 tax_amount,
#                 rate
#             )

#             add_gst_base(
#                 gst_bases,
#                 "SGST",
#                 rate,
#                 taxable_base
#             )

#             continue

#         # ==========================================================
#         # IGST 18%
#         # ==========================================================

#         if (
#             "igst" in account_text
#             and nearly_equal(rate, 18)
#         ):

#             input_igst_18 += tax_amount

#             taxable_base = get_taxable_base(
#                 tax,
#                 tax_amount,
#                 rate
#             )

#             purchase_base_18 += taxable_base

#             add_gst_base(
#                 gst_bases,
#                 "IGST",
#                 rate,
#                 taxable_base
#             )

#             continue

#         # ==========================================================
#         # CGST 2.5%
#         # ==========================================================

#         if (
#             "cgst" in account_text
#             and nearly_equal(rate, 2.5)
#         ):

#             input_cgst_2_5 += tax_amount

#             taxable_base = get_taxable_base(
#                 tax,
#                 tax_amount,
#                 rate
#             )

#             purchase_base_5 += taxable_base

#             add_gst_base(
#                 gst_bases,
#                 "CGST",
#                 rate,
#                 taxable_base
#             )

#             continue

#         # ==========================================================
#         # SGST 2.5%
#         # ==========================================================

#         if (
#             "sgst" in account_text
#             and nearly_equal(rate, 2.5)
#         ):

#             input_sgst_2_5 += tax_amount

#             taxable_base = get_taxable_base(
#                 tax,
#                 tax_amount,
#                 rate
#             )

#             add_gst_base(
#                 gst_bases,
#                 "SGST",
#                 rate,
#                 taxable_base
#             )

#             continue

#     # ==============================================================
#     # PURCHASE 18%
#     # ==============================================================

#     purchase_18 = purchase_base_18

#     # ==============================================================
#     # PURCHASE 5%
#     # ==============================================================

#     purchase_5 = purchase_base_5

#     # ==============================================================
#     # ALL GST TAXABLE BASE
#     #
#     # CGST + SGST are not double counted.
#     #
#     # Example:
#     #
#     # CGST 9% = base 6000
#     # SGST 9% = base 6000
#     #
#     # GST taxable base = 6000, NOT 12000.
#     # ==============================================================

#     gst_taxable_total = get_unique_gst_base_total(
#         gst_bases
#     )

#     # ==============================================================
#     # NON TAXABLE PURCHASE
#     #
#     # Net Total minus all GST taxable amounts.
#     #
#     # This prevents other GST rates from being incorrectly
#     # treated as non-taxable.
#     # ==============================================================

#     net_total = flt(
#         invoice.net_total
#     )

#     purchase_non_taxable = max(
#         net_total - gst_taxable_total,
#         0
#     )

#     # ==============================================================
#     # FINAL ROW
#     # ==============================================================

#     return {
#         "date": invoice.posting_date,

#         "particulars": invoice.supplier,

#         "voucher_type": "Purchase Invoice",

#         "voucher_no": invoice.name,

#         "voucher_ref_no": invoice.bill_no or "",

#         "gross_total": flt(
#             invoice.grand_total
#         ),

#         "purchase_18": flt(
#             purchase_18
#         ),

#         "input_cgst_9": flt(
#             input_cgst_9
#         ),

#         "input_sgst_9": flt(
#             input_sgst_9
#         ),

#         "tds_2": flt(
#             tds_2
#         ),

#         "purchase_non_taxable": flt(
#             purchase_non_taxable
#         ),

#         "input_igst_18": flt(
#             input_igst_18
#         ),

#         "round_off": flt(
#             round_off
#         ),

#         "purchase_5": flt(
#             purchase_5
#         ),

#         "input_cgst_2_5": flt(
#             input_cgst_2_5
#         ),

#         "input_sgst_2_5": flt(
#             input_sgst_2_5
#         ),

#         "tds_1": flt(
#             tds_1
#         ),

#         "interest_on_tds": flt(
#             interest_on_tds
#         )
#     }


# # ======================================================================
# # TAX AMOUNT
# # ======================================================================

# def get_tax_amount(tax):

#     value = tax.get(
#         "tax_amount_after_discount_amount"
#     )

#     if value is not None:
#         return flt(value)

#     value = tax.get("tax_amount")

#     if value is not None:
#         return flt(value)

#     return 0


# # ======================================================================
# # TAXABLE BASE
# # ======================================================================

# def get_taxable_base(tax, tax_amount, rate):

#     if not rate:
#         return 0

#     # --------------------------------------------------------------
#     # ERPNext stores company-currency tax amount here.
#     # base_total is cumulative total, so it must NOT be used as
#     # taxable base.
#     # --------------------------------------------------------------

#     base_tax_amount = flt(
#         tax.get("base_tax_amount")
#     )

#     base_tax_after_discount = flt(
#         tax.get(
#             "base_tax_amount_after_discount_amount"
#         )
#     )

#     if base_tax_after_discount:
#         return abs(base_tax_after_discount) * 100 / abs(rate)

#     if base_tax_amount:
#         return abs(base_tax_amount) * 100 / abs(rate)

#     return abs(tax_amount) * 100 / abs(rate)


# # ======================================================================
# # STORE GST BASE
# # ======================================================================

# def add_gst_base(
#     gst_bases,
#     tax_type,
#     rate,
#     taxable_base
# ):

#     key = round(rate, 4)

#     if key not in gst_bases:
#         gst_bases[key] = {}

#     current = gst_bases[key].get(
#         tax_type,
#         0
#     )

#     gst_bases[key][tax_type] = max(
#         current,
#         abs(taxable_base)
#     )


# # ======================================================================
# # UNIQUE GST BASE
# # ======================================================================

# def get_unique_gst_base_total(gst_bases):

#     total = 0

#     for rate, components in gst_bases.items():

#         igst = flt(
#             components.get("IGST", 0)
#         )

#         cgst = flt(
#             components.get("CGST", 0)
#         )

#         sgst = flt(
#             components.get("SGST", 0)
#         )

#         # ----------------------------------------------------------
#         # IGST is already the complete taxable base.
#         # ----------------------------------------------------------

#         if igst:
#             total += igst

#         # ----------------------------------------------------------
#         # For CGST + SGST, they represent the SAME taxable base.
#         # Do not add both.
#         # ----------------------------------------------------------

#         else:
#             total += max(
#                 cgst,
#                 sgst
#             )

#     return total


# # ======================================================================
# # TOTAL ROW
# # ======================================================================

# def get_total_row(data):

#     numeric_fields = [
#         "gross_total",
#         "purchase_18",
#         "input_cgst_9",
#         "input_sgst_9",
#         "tds_2",
#         "purchase_non_taxable",
#         "input_igst_18",
#         "round_off",
#         "purchase_5",
#         "input_cgst_2_5",
#         "input_sgst_2_5",
#         "tds_1",
#         "interest_on_tds"
#     ]

#     total_row = {
#         "date": None,
#         "particulars": "Total",
#         "voucher_type": "",
#         "voucher_no": "",
#         "voucher_ref_no": ""
#     }

#     for fieldname in numeric_fields:

#         total_row[fieldname] = sum(
#             flt(row.get(fieldname))
#             for row in data
#         )

#     return total_row


# # ======================================================================
# # HELPERS
# # ======================================================================

# def nearly_equal(
#     value1,
#     value2,
#     tolerance=0.0001
# ):

#     return abs(
#         flt(value1) - flt(value2)
#     ) <= tolerance


# def flt(value):

#     return frappe.utils.flt(
#         value
#     )


# def cint(value):

#     return frappe.utils.cint(
#         value
#     )

from __future__ import unicode_literals

import json
import hashlib

import frappe
from frappe import _


# ======================================================================
# EXECUTE
# ======================================================================

def execute(filters=None):
    filters = frappe._dict(filters or {})

    validate_filters(filters)

    # --------------------------------------------------------------
    # Get ALL Tax Withholding Categories from the system.
    # --------------------------------------------------------------
    tds_categories = get_tds_categories()

    columns = get_columns(tds_categories)

    data = get_data(
        filters,
        tds_categories
    )

    if data:
        data.append(
            get_total_row(
                data,
                tds_categories
            )
        )

    return columns, data


# ======================================================================
# VALIDATION
# ======================================================================

def validate_filters(filters):

    if not filters.get("from_date"):
        frappe.throw(
            _("From Date is mandatory.")
        )

    if not filters.get("to_date"):
        frappe.throw(
            _("To Date is mandatory.")
        )

    if filters.from_date > filters.to_date:
        frappe.throw(
            _("From Date cannot be greater than To Date.")
        )


# ======================================================================
# GET ALL TAX WITHHOLDING CATEGORIES
# ======================================================================

def get_tds_categories():

    categories = frappe.get_all(
        "Tax Withholding Category",
        fields=["name"],
        order_by="name asc"
    )

    result = []

    for category in categories:

        category_name = category.name

        result.append({
            "name": category_name,
            "fieldname": get_category_fieldname(
                category_name
            )
        })

    return result


# ======================================================================
# DYNAMIC FIELDNAME FOR TDS CATEGORY
# ======================================================================

def get_category_fieldname(category_name):

    # --------------------------------------------------------------
    # Use hash to guarantee a unique fieldname even when category
    # names contain spaces, hyphens, %, brackets, etc.
    # --------------------------------------------------------------

    category_hash = hashlib.md5(
        category_name.encode("utf-8")
    ).hexdigest()[:10]

    return "tds_category_" + category_hash


# ======================================================================
# COLUMNS
# ======================================================================

def get_columns(tds_categories):

    columns = [

        # ----------------------------------------------------------
        # DATE
        # ----------------------------------------------------------

        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 95,
        },

        # ----------------------------------------------------------
        # PARTICULARS
        # ----------------------------------------------------------

        {
            "fieldname": "particulars",
            "label": _("Particulars"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 220,
        },

        # ----------------------------------------------------------
        # SUPPLIER PAN
        # ----------------------------------------------------------

        {
            "fieldname": "supplier_pan",
            "label": _("Supplier PAN"),
            "fieldtype": "Data",
            "width": 130,
        },

        # ----------------------------------------------------------
        # VOUCHER TYPE
        # ----------------------------------------------------------

        {
            "fieldname": "voucher_type",
            "label": _("Voucher type"),
            "fieldtype": "Data",
            "width": 140,
        },

        # ----------------------------------------------------------
        # VOUCHER NO.
        # ----------------------------------------------------------

        {
            "fieldname": "voucher_no",
            "label": _("Voucher no."),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180,
        },

        # ----------------------------------------------------------
        # VOUCHER REF. NO.
        # ----------------------------------------------------------

        {
            "fieldname": "voucher_ref_no",
            "label": _("Voucher ref. no."),
            "fieldtype": "Data",
            "width": 170,
        },

        # ----------------------------------------------------------
        # GROSS TOTAL
        # ----------------------------------------------------------

        {
            "fieldname": "gross_total",
            "label": _("Gross total"),
            "fieldtype": "Currency",
            "width": 120,
        },

        # ----------------------------------------------------------
        # PURCHASE 18%
        # ----------------------------------------------------------

        {
            "fieldname": "purchase_18",
            "label": _("Purchase 18%"),
            "fieldtype": "Currency",
            "width": 120,
        },

        # ----------------------------------------------------------
        # INPUT CGST 9%
        # ----------------------------------------------------------

        {
            "fieldname": "input_cgst_9",
            "label": _("Input cgst 9%"),
            "fieldtype": "Currency",
            "width": 125,
        },

        # ----------------------------------------------------------
        # INPUT SGST 9%
        # ----------------------------------------------------------

        {
            "fieldname": "input_sgst_9",
            "label": _("Input sgst 9%"),
            "fieldtype": "Currency",
            "width": 125,
        },

        # ----------------------------------------------------------
        # 94 C TDS 2%
        # ----------------------------------------------------------

        {
            "fieldname": "tds_2",
            "label": _("94 C tds payable 2%"),
            "fieldtype": "Currency",
            "width": 145,
        },

        # ----------------------------------------------------------
        # PURCHASE NON TAXABLE
        # ----------------------------------------------------------

        {
            "fieldname": "purchase_non_taxable",
            "label": _("Purchase non taxable"),
            "fieldtype": "Currency",
            "width": 150,
        },

        # ----------------------------------------------------------
        # INPUT IGST 18%
        # ----------------------------------------------------------

        {
            "fieldname": "input_igst_18",
            "label": _("Input igst 18%"),
            "fieldtype": "Currency",
            "width": 125,
        },

        # ----------------------------------------------------------
        # ROUND OFF
        # ----------------------------------------------------------

        {
            "fieldname": "round_off",
            "label": _("Round off"),
            "fieldtype": "Currency",
            "width": 100,
        },

        # ----------------------------------------------------------
        # PURCHASE 5%
        # ----------------------------------------------------------

        {
            "fieldname": "purchase_5",
            "label": _("Purchase 5%"),
            "fieldtype": "Currency",
            "width": 120,
        },

        # ----------------------------------------------------------
        # INPUT CGST 2.5%
        # ----------------------------------------------------------

        {
            "fieldname": "input_cgst_2_5",
            "label": _("Input cgst 2.5%"),
            "fieldtype": "Currency",
            "width": 135,
        },

        # ----------------------------------------------------------
        # INPUT SGST 2.5%
        # ----------------------------------------------------------

        {
            "fieldname": "input_sgst_2_5",
            "label": _("Input sgst 2.5%"),
            "fieldtype": "Currency",
            "width": 135,
        },

        # ----------------------------------------------------------
        # 94 C TDS 1%
        # ----------------------------------------------------------

        {
            "fieldname": "tds_1",
            "label": _("94 C tds payable 1%"),
            "fieldtype": "Currency",
            "width": 145,
        },
    ]

    # ==============================================================
    # DYNAMIC TAX WITHHOLDING CATEGORY COLUMNS
    # ==============================================================

    for category in tds_categories:

        columns.append({
            "fieldname": category["fieldname"],
            "label": _(category["name"]),
            "fieldtype": "Currency",
            "width": 180,
        })

    return columns


# ======================================================================
# GET PURCHASE INVOICES
# ======================================================================

def get_data(
    filters,
    tds_categories
):

    conditions = [
        "pi.docstatus = 1",
        "pi.posting_date BETWEEN %(from_date)s AND %(to_date)s",
    ]

    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date,
    }

    # --------------------------------------------------------------
    # SUPPLIER FILTER
    # --------------------------------------------------------------

    if filters.get("supplier"):

        conditions.append(
            "pi.supplier = %(supplier)s"
        )

        values["supplier"] = filters.supplier

    where_clause = " AND ".join(
        conditions
    )

    # ==============================================================
    # PURCHASE INVOICES
    # ==============================================================

    invoices = frappe.db.sql(
        """
        SELECT
            pi.name,
            pi.posting_date,
            pi.supplier,
            pi.bill_no,
            pi.net_total,
            pi.grand_total,
            pi.rounding_adjustment,
            pi.tax_withholding_category,

            s.pan AS supplier_pan,
            s.tax_withholding_group AS supplier_tax_withholding_group

        FROM `tabPurchase Invoice` pi

        LEFT JOIN `tabSupplier` s
            ON s.name = pi.supplier

        WHERE {where_clause}

        ORDER BY
            pi.posting_date ASC,
            pi.name ASC
        """.format(
            where_clause=where_clause
        ),
        values,
        as_dict=True,
    )

    if not invoices:
        return []

    invoice_names = [
        invoice.name
        for invoice in invoices
    ]

    # ==============================================================
    # PURCHASE TAXES AND CHARGES
    # ==============================================================

    taxes = frappe.db.sql(
        """
        SELECT
            parent,
            name,
            idx,
            category,
            add_deduct_tax,
            charge_type,
            row_id,
            account_head,
            description,
            is_tax_withholding_account,
            rate,
            gst_tax_type,
            tax_amount,
            tax_amount_after_discount_amount,
            total,
            base_tax_amount,
            base_total,
            base_tax_amount_after_discount_amount,
            item_wise_tax_detail

        FROM `tabPurchase Taxes and Charges`

        WHERE parent IN %(parents)s

        ORDER BY
            parent,
            idx
        """,
        {
            "parents": invoice_names,
        },
        as_dict=True,
    )

    taxes_by_invoice = {}

    for tax in taxes:

        taxes_by_invoice.setdefault(
            tax.parent,
            []
        ).append(tax)

    # ==============================================================
    # PURCHASE INVOICE ITEMS
    # ==============================================================

    items = frappe.db.sql(
        """
        SELECT
            parent,
            name,
            idx,
            item_code,
            item_name,
            amount,
            base_amount,
            item_tax_template

        FROM `tabPurchase Invoice Item`

        WHERE parent IN %(parents)s

        ORDER BY
            parent,
            idx
        """,
        {
            "parents": invoice_names,
        },
        as_dict=True,
    )

    items_by_invoice = {}

    for item in items:

        items_by_invoice.setdefault(
            item.parent,
            []
        ).append(item)

    # ==============================================================
    # CALCULATE DATA
    # ==============================================================

    data = []

    for invoice in invoices:

        invoice_taxes = taxes_by_invoice.get(
            invoice.name,
            []
        )

        invoice_items = items_by_invoice.get(
            invoice.name,
            []
        )

        row = calculate_invoice(
            invoice,
            invoice_taxes,
            invoice_items,
            tds_categories
        )

        data.append(row)

    return data


# ======================================================================
# CALCULATE ONE INVOICE
# ======================================================================

def calculate_invoice(
    invoice,
    taxes,
    items,
    tds_categories
):

    input_cgst_9 = 0
    input_sgst_9 = 0
    input_igst_18 = 0

    input_cgst_2_5 = 0
    input_sgst_2_5 = 0

    tds_2 = 0
    tds_1 = 0

    # --------------------------------------------------------------
    # Dynamic TDS category values
    # --------------------------------------------------------------

    tds_by_category = {}

    for category in tds_categories:

        tds_by_category[
            category["name"]
        ] = 0

    # ==============================================================
    # PROCESS TAX ROWS
    # ==============================================================

    for tax in taxes:

        rate = flt(
            tax.rate
        )

        tax_amount = get_tax_amount(
            tax
        )

        account_head = (
            tax.account_head or ""
        ).strip()

        description = (
            tax.description or ""
        ).strip()

        gst_tax_type = (
            tax.gst_tax_type or ""
        ).strip()

        account_text = (
            account_head
            + " "
            + description
            + " "
            + gst_tax_type
        ).lower()

        # ==========================================================
        # TDS / TAX WITHHOLDING
        # ==========================================================

        if (
            invoice.tax_withholding_category
            and is_tds_row(tax)
        ):

            tds_category = (
                invoice.tax_withholding_category
            )

            # ------------------------------------------------------
            # PUT ACTUAL TDS AMOUNT INTO THE EXACT CATEGORY COLUMN
            # ------------------------------------------------------

            if tds_category in tds_by_category:

                tds_by_category[
                    tds_category
                ] += tax_amount

            # ------------------------------------------------------
            # 94C FIXED COLUMNS
            #
            # IMPORTANT:
            # Classification is based on PURCHASE INVOICE
            # Tax Withholding Category name.
            #
            # Example:
            # TDS - 194LBB - Company
            #
            # will NOT be treated as 194C even if its account
            # happens to contain "194C".
            # ------------------------------------------------------

            if is_194c_category(
                tds_category
            ):

                tds_rate = get_tds_category_rate(
                    tds_category,
                    invoice.posting_date,
                    invoice.supplier_tax_withholding_group
                )

                # --------------------------------------------------
                # If category configuration does not return a rate,
                # fall back to tax row rate.
                # --------------------------------------------------

                if not tds_rate:
                    tds_rate = abs(
                        rate
                    )

                if nearly_equal(
                    tds_rate,
                    2
                ):

                    tds_2 += tax_amount

                elif nearly_equal(
                    tds_rate,
                    1
                ):

                    tds_1 += tax_amount

            continue

        # ==========================================================
        # CGST 9%
        # ==========================================================

        if (
            "cgst" in account_text
            and nearly_equal(
                rate,
                9
            )
        ):

            input_cgst_9 += tax_amount

            continue

        # ==========================================================
        # SGST 9%
        # ==========================================================

        if (
            "sgst" in account_text
            and nearly_equal(
                rate,
                9
            )
        ):

            input_sgst_9 += tax_amount

            continue

        # ==========================================================
        # IGST 18%
        # ==========================================================

        if (
            "igst" in account_text
            and nearly_equal(
                rate,
                18
            )
        ):

            input_igst_18 += tax_amount

            continue

        # ==========================================================
        # CGST 2.5%
        # ==========================================================

        if (
            "cgst" in account_text
            and nearly_equal(
                rate,
                2.5
            )
        ):

            input_cgst_2_5 += tax_amount

            continue

        # ==========================================================
        # SGST 2.5%
        # ==========================================================

        if (
            "sgst" in account_text
            and nearly_equal(
                rate,
                2.5
            )
        ):

            input_sgst_2_5 += tax_amount

            continue

    # ==============================================================
    # PURCHASE 18%
    #
    # CGST 9% + SGST 9%
    # ==============================================================

    purchase_18 = (
        input_cgst_9
        + input_sgst_9
    )

    # ==============================================================
    # PURCHASE 5%
    #
    # CGST 2.5% + SGST 2.5%
    # ==============================================================

    purchase_5 = (
        input_cgst_2_5
        + input_sgst_2_5
    )

    # ==============================================================
    # PURCHASE NON TAXABLE
    # ==============================================================

    purchase_non_taxable = (
        get_purchase_non_taxable(
            items,
            taxes
        )
    )

    # ==============================================================
    # FINAL ROW
    # ==============================================================

    row = {

        "date": invoice.posting_date,

        "particulars": invoice.supplier,

        "supplier_pan": invoice.supplier_pan or "",

        "voucher_type": "Purchase Invoice",

        "voucher_no": invoice.name,

        "voucher_ref_no": (
            invoice.bill_no or ""
        ),

        "gross_total": flt(
            invoice.grand_total
        ),

        "purchase_18": flt(
            purchase_18
        ),

        "input_cgst_9": flt(
            input_cgst_9
        ),

        "input_sgst_9": flt(
            input_sgst_9
        ),

        "tds_2": flt(
            tds_2
        ),

        "purchase_non_taxable": flt(
            purchase_non_taxable
        ),

        "input_igst_18": flt(
            input_igst_18
        ),

        "round_off": flt(
            invoice.rounding_adjustment
        ),

        "purchase_5": flt(
            purchase_5
        ),

        "input_cgst_2_5": flt(
            input_cgst_2_5
        ),

        "input_sgst_2_5": flt(
            input_sgst_2_5
        ),

        "tds_1": flt(
            tds_1
        ),
    }

    # ==============================================================
    # ADD ALL DYNAMIC TDS CATEGORY VALUES
    # ==============================================================

    for category in tds_categories:

        category_name = category["name"]

        fieldname = category["fieldname"]

        row[fieldname] = flt(
            tds_by_category.get(
                category_name,
                0
            )
        )

    return row


# ======================================================================
# CHECK WHETHER TAX ROW IS TDS
# ======================================================================

def is_tds_row(tax):

    account_head = (
        tax.account_head or ""
    ).lower()

    description = (
        tax.description or ""
    ).lower()

    # --------------------------------------------------------------
    # is_tax_withholding_account is the preferred indicator.
    # --------------------------------------------------------------

    if cint(
        tax.is_tax_withholding_account
    ):
        return True

    # --------------------------------------------------------------
    # Fallback for existing invoices where the flag may not be set.
    # --------------------------------------------------------------

    if "tds" in account_head:
        return True

    if "tds" in description:
        return True

    if "withholding" in account_head:
        return True

    if "withholding" in description:
        return True

    return False


# ======================================================================
# CHECK 194C CATEGORY
# ======================================================================

def is_194c_category(category_name):

    if not category_name:
        return False

    return "194c" in (
        category_name.lower()
    )


# ======================================================================
# GET TDS CATEGORY RATE
# ======================================================================

def get_tds_category_rate(
    category_name,
    posting_date,
    supplier_tax_withholding_group=None
):

    if not category_name:
        return 0

    try:

        category = frappe.get_doc(
            "Tax Withholding Category",
            category_name
        )

    except Exception:

        return 0

    rates = category.get(
        "rates"
    ) or []

    valid_rates = []

    # ==============================================================
    # FIRST FIND RATE ROWS VALID FOR POSTING DATE
    # ==============================================================

    for rate_row in rates:

        from_date = rate_row.get(
            "from_date"
        )

        to_date = rate_row.get(
            "to_date"
        )

        if (
            from_date
            and posting_date < from_date
        ):
            continue

        if (
            to_date
            and posting_date > to_date
        ):
            continue

        rate = flt(
            rate_row.get(
                "tax_withholding_rate"
            )
            or rate_row.get(
                "rate"
            )
        )

        if rate:

            valid_rates.append(
                rate_row
            )

    if not valid_rates:
        return 0

    # ==============================================================
    # 1. TRY SUPPLIER'S TAX WITHHOLDING GROUP
    # ==============================================================

    if supplier_tax_withholding_group:

        for rate_row in valid_rates:

            row_group = (
                rate_row.get(
                    "tax_withholding_group"
                )
                or ""
            ).strip()

            if (
                row_group
                and row_group
                == supplier_tax_withholding_group
            ):

                return flt(
                    rate_row.get(
                        "tax_withholding_rate"
                    )
                    or rate_row.get(
                        "rate"
                    )
                )

    # ==============================================================
    # 2. TRY BLANK / DEFAULT GROUP
    # ==============================================================

    for rate_row in valid_rates:

        row_group = (
            rate_row.get(
                "tax_withholding_group"
            )
            or ""
        ).strip()

        if not row_group:

            return flt(
                rate_row.get(
                    "tax_withholding_rate"
                )
                or rate_row.get(
                    "rate"
                )
            )

    # ==============================================================
    # 3. FALLBACK TO FIRST VALID RATE
    # ==============================================================

    first_row = valid_rates[0]

    return flt(
        first_row.get(
            "tax_withholding_rate"
        )
        or first_row.get(
            "rate"
        )
    )


# ======================================================================
# TAX AMOUNT
# ======================================================================

def get_tax_amount(tax):

    # --------------------------------------------------------------
    # Actual amount after discount is preferred.
    # --------------------------------------------------------------

    value = tax.get(
        "tax_amount_after_discount_amount"
    )

    if value is not None:

        return flt(
            value
        )

    # --------------------------------------------------------------
    # Fallback
    # --------------------------------------------------------------

    value = tax.get(
        "tax_amount"
    )

    if value is not None:

        return flt(
            value
        )

    return 0


# ======================================================================
# PURCHASE NON TAXABLE
# ======================================================================

def get_purchase_non_taxable(
    items,
    taxes
):

    """
    Purchase Non Taxable is calculated from item-level GST
    information.

    It does NOT use:

        net_total - GST taxable total

    because that can incorrectly classify another GST rate
    as non-taxable.

    Items with:
        - 0% GST
        - exempt
        - nil rated
        - zero rated
        - non-taxable
        - no GST information when invoice has no GST rows

    are included.
    """

    if not items:
        return 0

    item_gst_rates = get_item_gst_rates(
        taxes
    )

    # ==============================================================
    # CHECK WHETHER INVOICE HAS GST ROWS
    # ==============================================================

    has_gst_rows = False

    for tax in taxes:

        account_head = (
            tax.account_head or ""
        ).lower()

        description = (
            tax.description or ""
        ).lower()

        gst_tax_type = (
            tax.gst_tax_type or ""
        ).lower()

        tax_text = (
            account_head
            + " "
            + description
            + " "
            + gst_tax_type
        )

        if (
            "cgst" in tax_text
            or "sgst" in tax_text
            or "igst" in tax_text
        ):

            if (
                flt(tax.rate) > 0
                or tax.get(
                    "item_wise_tax_detail"
                )
            ):

                has_gst_rows = True

                break

    total_non_taxable = 0

    # ==============================================================
    # PROCESS EACH ITEM
    # ==============================================================

    for item in items:

        item_code = (
            item.item_code or ""
        ).strip()

        # ----------------------------------------------------------
        # Item value
        # ----------------------------------------------------------

        item_value = item.get(
            "base_amount"
        )

        if item_value is None:

            item_value = item.get(
                "amount"
            )

        item_value = flt(
            item_value
        )

        if not item_value:
            continue

        # ==========================================================
        # ITEM-WISE GST INFORMATION
        # ==========================================================

        rates = item_gst_rates.get(
            item_code
        )

        if rates is not None:

            # ------------------------------------------------------
            # No rate or all rates are 0
            # ------------------------------------------------------

            if (
                not rates
                or all(
                    nearly_equal(
                        rate,
                        0
                    )
                    for rate in rates
                )
            ):

                total_non_taxable += (
                    item_value
                )

            continue

        # ==========================================================
        # ITEM TAX TEMPLATE
        # ==========================================================

        template = (
            item.item_tax_template or ""
        ).strip()

        if template:

            template_text = (
                template.lower()
            )

            if is_exempt_or_zero_tax_template(
                template_text
            ):

                total_non_taxable += (
                    item_value
                )

            continue

        # ==========================================================
        # NO GST INFORMATION
        # ==============================================================

        if not has_gst_rows:

            total_non_taxable += (
                item_value
            )

    return total_non_taxable


# ======================================================================
# ITEM-WISE GST RATES
# ======================================================================

def get_item_gst_rates(taxes):

    item_gst_rates = {}

    for tax in taxes:

        account_head = (
            tax.account_head or ""
        ).lower()

        description = (
            tax.description or ""
        ).lower()

        gst_tax_type = (
            tax.gst_tax_type or ""
        ).lower()

        tax_text = (
            account_head
            + " "
            + description
            + " "
            + gst_tax_type
        )

        # ----------------------------------------------------------
        # Only GST rows
        # ----------------------------------------------------------

        if not (
            "cgst" in tax_text
            or "sgst" in tax_text
            or "igst" in tax_text
        ):

            continue

        raw_detail = tax.get(
            "item_wise_tax_detail"
        )

        if not raw_detail:
            continue

        try:

            if isinstance(
                raw_detail,
                str
            ):

                details = json.loads(
                    raw_detail
                )

            else:

                details = raw_detail

        except Exception:

            continue

        if not isinstance(
            details,
            dict
        ):

            continue

        for item_code, detail in details.items():

            rate = 0

            # ------------------------------------------------------
            # Standard ERPNext format
            # ------------------------------------------------------

            if isinstance(
                detail,
                (list, tuple)
            ):

                if len(detail) > 0:

                    rate = flt(
                        detail[0]
                    )

            # ------------------------------------------------------
            # Dictionary format
            # ------------------------------------------------------

            elif isinstance(
                detail,
                dict
            ):

                rate = flt(
                    detail.get(
                        "rate"
                    )
                    or detail.get(
                        "tax_rate"
                    )
                )

            item_gst_rates.setdefault(
                item_code,
                []
            ).append(
                rate
            )

    return item_gst_rates


# ======================================================================
# EXEMPT / ZERO TAX TEMPLATE
# ======================================================================

def is_exempt_or_zero_tax_template(
    template_text
):

    keywords = [

        "exempt",
        "exempted",

        "nil rated",
        "nil-rated",

        "zero rated",
        "zero-rated",

        "non taxable",
        "non-taxable",

        "not taxable",

        "0%",
    ]

    return any(
        keyword in template_text
        for keyword in keywords
    )


# ======================================================================
# TOTAL ROW
# ======================================================================

def get_total_row(
    data,
    tds_categories
):

    # --------------------------------------------------------------
    # Fixed numeric columns
    # --------------------------------------------------------------

    numeric_fields = [

        "gross_total",

        "purchase_18",

        "input_cgst_9",

        "input_sgst_9",

        "tds_2",

        "purchase_non_taxable",

        "input_igst_18",

        "round_off",

        "purchase_5",

        "input_cgst_2_5",

        "input_sgst_2_5",

        "tds_1",
    ]

    total_row = {

        "date": None,

        "particulars": "Total",

        "supplier_pan": "",

        "voucher_type": "",

        "voucher_no": "",

        "voucher_ref_no": "",
    }

    # ==============================================================
    # FIXED TOTALS
    # ==============================================================

    for fieldname in numeric_fields:

        total_row[fieldname] = sum(
            flt(
                row.get(
                    fieldname
                )
            )
            for row in data
        )

    # ==============================================================
    # DYNAMIC TDS CATEGORY TOTALS
    # ==============================================================

    for category in tds_categories:

        fieldname = category[
            "fieldname"
        ]

        total_row[fieldname] = sum(
            flt(
                row.get(
                    fieldname
                )
            )
            for row in data
        )

    return total_row


# ======================================================================
# HELPER - NEARLY EQUAL
# ======================================================================

def nearly_equal(
    value1,
    value2,
    tolerance=0.0001
):

    return abs(
        flt(value1)
        - flt(value2)
    ) <= tolerance


# ======================================================================
# HELPER - FLT
# ======================================================================

def flt(value):

    return frappe.utils.flt(
        value
    )


# ======================================================================
# HELPER - CINT
# ======================================================================

def cint(value):

    return frappe.utils.cint(
        value
    )