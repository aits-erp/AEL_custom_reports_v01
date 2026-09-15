# Copyright (c) 2026, sai and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    return columns, data


# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------

def validate_filters(filters):
    if not filters.get("from_date"):
        frappe.throw(_("From Date is mandatory."))

    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory."))

    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be greater than To Date."))


# ----------------------------------------------------------------------
# COLUMNS
# ----------------------------------------------------------------------

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": _("Date"),
            "fieldtype": "Date",
            "width": 95
        },
        {
            "fieldname": "particulars",
            "label": _("Particulars"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 220
        },
        {
            "fieldname": "voucher_type",
            "label": _("Voucher Type"),
            "fieldtype": "Data",
            "width": 130
        },
        {
            "fieldname": "voucher_no",
            "label": _("Voucher No."),
            "fieldtype": "Link",
            "options": "Purchase Invoice",
            "width": 180
        },
        {
            "fieldname": "voucher_ref_no",
            "label": _("Voucher Ref. No."),
            "fieldtype": "Data",
            "width": 170
        },
        {
            "fieldname": "gross_total",
            "label": _("Gross Total"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "purchase_18",
            "label": _("Purchase 18%"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "input_cgst_9",
            "label": _("INPUT CGST 9%"),
            "fieldtype": "Currency",
            "width": 125
        },
        {
            "fieldname": "input_sgst_9",
            "label": _("INPUT SGST 9%"),
            "fieldtype": "Currency",
            "width": 125
        },
        {
            "fieldname": "tds_2",
            "label": _("94 C Tds Payable 2%"),
            "fieldtype": "Currency",
            "width": 145
        },
        {
            "fieldname": "purchase_non_taxable",
            "label": _("Purchase Non Taxable"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "input_igst_18",
            "label": _("INPUT IGST 18%"),
            "fieldtype": "Currency",
            "width": 125
        },
        {
            "fieldname": "round_off",
            "label": _("Round Off"),
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "fieldname": "purchase_5",
            "label": _("Purchase 5%"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "input_cgst_2_5",
            "label": _("INPUT CGST 2.5%"),
            "fieldtype": "Currency",
            "width": 135
        },
        {
            "fieldname": "input_sgst_2_5",
            "label": _("Input Sgst 2.5%"),
            "fieldtype": "Currency",
            "width": 135
        },
        {
            "fieldname": "tds_1",
            "label": _("94 C Tds Payable 1%"),
            "fieldtype": "Currency",
            "width": 145
        },
        {
            "fieldname": "interest_on_tds",
            "label": _("Interest on TDS"),
            "fieldtype": "Currency",
            "width": 125
        }
    ]


# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------

def get_data(filters):
    conditions = """
        pi.docstatus = 1
        AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
    """

    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.get("supplier"):
        conditions += """
            AND pi.supplier = %(supplier)s
        """
        values["supplier"] = filters.supplier

    # --------------------------------------------------------------
    # Get submitted Purchase Invoices
    # --------------------------------------------------------------

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
            pi.currency

        FROM `tabPurchase Invoice` pi

        WHERE {conditions}

        ORDER BY
            pi.posting_date ASC,
            pi.name ASC
        """.format(conditions=conditions),
        values,
        as_dict=True
    )

    if not invoices:
        return []

    invoice_names = [invoice.name for invoice in invoices]

    # --------------------------------------------------------------
    # Get ALL Purchase Taxes and Charges rows dynamically
    # --------------------------------------------------------------

    taxes = frappe.db.sql(
        """
        SELECT
            parent,
            name,
            idx,
            charge_type,
            account_head,
            description,
            rate,
            tax_amount,
            amount,
            total,
            base_tax_amount,
            base_amount,
            base_total

        FROM `tabPurchase Taxes and Charges`

        WHERE
            parent IN %(parents)s

        ORDER BY
            parent,
            idx
        """,
        {
            "parents": invoice_names
        },
        as_dict=True
    )

    # --------------------------------------------------------------
    # Group taxes by Purchase Invoice
    # --------------------------------------------------------------

    taxes_by_invoice = {}

    for tax in taxes:
        taxes_by_invoice.setdefault(tax.parent, []).append(tax)

    data = []

    for invoice in invoices:

        invoice_taxes = taxes_by_invoice.get(invoice.name, [])

        values = calculate_invoice_values(
            invoice,
            invoice_taxes
        )

        data.append(values)

    return data


# ----------------------------------------------------------------------
# DYNAMIC TAX CALCULATION
# ----------------------------------------------------------------------

def calculate_invoice_values(invoice, taxes):
    """
    Build one report row for one Purchase Invoice.

    No supplier names or account names are hardcoded.

    The classification is based on:
        - Account Head
        - Description
        - Tax Rate
        - Actual tax amount
    """

    # --------------------------------------------------------------
    # Initialize
    # --------------------------------------------------------------

    purchase_18 = 0
    input_cgst_9 = 0
    input_sgst_9 = 0

    tds_2 = 0

    purchase_non_taxable = 0

    input_igst_18 = 0

    round_off = flt(invoice.rounding_adjustment)

    purchase_5 = 0
    input_cgst_2_5 = 0
    input_sgst_2_5 = 0

    tds_1 = 0
    interest_on_tds = 0

    # --------------------------------------------------------------
    # Track taxable bases
    # --------------------------------------------------------------

    taxable_base_18 = 0
    taxable_base_5 = 0

    # --------------------------------------------------------------
    # Track whether GST exists
    # --------------------------------------------------------------

    taxable_base_total = 0

    for tax in taxes:

        rate = flt(tax.rate)
        tax_amount = get_tax_amount(tax)

        account_head = (tax.account_head or "").strip()
        description = (tax.description or "").strip()

        account_text = (
            account_head + " " + description
        ).lower()

        # ----------------------------------------------------------
        # Ignore empty tax rows
        # ----------------------------------------------------------

        if not account_head and not description and not rate and not tax_amount:
            continue

        # ----------------------------------------------------------
        # ROUND OFF
        #
        # If ERPNext has a tax/charge row specifically representing
        # round off, capture it as well.
        # Parent rounding_adjustment remains the primary source.
        # ----------------------------------------------------------

        if "round off" in account_text or "rounding" in account_text:
            round_off += tax_amount
            continue

        # ----------------------------------------------------------
        # TDS / INTEREST
        #
        # TDS is detected dynamically from account/description.
        # No exact account name is hardcoded.
        # ----------------------------------------------------------

        if "tds" in account_text or "withholding" in account_text:

            if (
                "interest" in account_text
                or "late fee" in account_text
                or "interest on" in account_text
            ):
                interest_on_tds += tax_amount

            elif nearly_equal(rate, 2):
                tds_2 += tax_amount

            elif nearly_equal(rate, 1):
                tds_1 += tax_amount

            continue

        # ----------------------------------------------------------
        # INTEREST ON TDS
        # ----------------------------------------------------------

        if (
            "interest" in account_text
            and "tds" in account_text
        ):
            interest_on_tds += tax_amount
            continue

        # ----------------------------------------------------------
        # CGST 9%
        # ----------------------------------------------------------

        if "cgst" in account_text and nearly_equal(rate, 9):

            input_cgst_9 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            taxable_base_18 += taxable_base
            taxable_base_total += taxable_base

            continue

        # ----------------------------------------------------------
        # SGST 9%
        # ----------------------------------------------------------

        if "sgst" in account_text and nearly_equal(rate, 9):

            input_sgst_9 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            taxable_base_total += taxable_base

            continue

        # ----------------------------------------------------------
        # IGST 18%
        # ----------------------------------------------------------

        if "igst" in account_text and nearly_equal(rate, 18):

            input_igst_18 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            taxable_base_18 += taxable_base
            taxable_base_total += taxable_base

            continue

        # ----------------------------------------------------------
        # CGST 2.5%
        # ----------------------------------------------------------

        if "cgst" in account_text and nearly_equal(rate, 2.5):

            input_cgst_2_5 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            taxable_base_5 += taxable_base
            taxable_base_total += taxable_base

            continue

        # ----------------------------------------------------------
        # SGST 2.5%
        # ----------------------------------------------------------

        if "sgst" in account_text and nearly_equal(rate, 2.5):

            input_sgst_2_5 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            taxable_base_total += taxable_base

            continue

    # --------------------------------------------------------------
    # Purchase 18%
    #
    # 9% CGST + 9% SGST = 18% GST
    #
    # IGST 18% is also 18% GST.
    # --------------------------------------------------------------

    purchase_18 = taxable_base_18

    # --------------------------------------------------------------
    # Purchase 5%
    #
    # 2.5% CGST + 2.5% SGST = 5%
    # --------------------------------------------------------------

    purchase_5 = taxable_base_5

    # --------------------------------------------------------------
    # NON TAXABLE PURCHASE
    #
    # net_total minus GST-taxable purchase bases.
    #
    # This remains dynamic and does not depend on supplier/account
    # names.
    # --------------------------------------------------------------

    net_total = flt(invoice.net_total)

    taxable_total = (
        taxable_base_18
        + taxable_base_5
    )

    purchase_non_taxable = max(
        net_total - taxable_total,
        0
    )

    # --------------------------------------------------------------
    # Return report row
    # --------------------------------------------------------------

    return {
        "date": invoice.posting_date,

        "particulars": invoice.supplier,

        "voucher_type": "Purchase Invoice",

        "voucher_no": invoice.name,

        "voucher_ref_no": invoice.bill_no or "",

        "gross_total": flt(invoice.grand_total),

        "purchase_18": flt(purchase_18),

        "input_cgst_9": flt(input_cgst_9),

        "input_sgst_9": flt(input_sgst_9),

        "tds_2": flt(tds_2),

        "purchase_non_taxable": flt(
            purchase_non_taxable
        ),

        "input_igst_18": flt(input_igst_18),

        "round_off": flt(round_off),

        "purchase_5": flt(purchase_5),

        "input_cgst_2_5": flt(input_cgst_2_5),

        "input_sgst_2_5": flt(input_sgst_2_5),

        "tds_1": flt(tds_1),

        "interest_on_tds": flt(interest_on_tds)
    }


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------

def get_tax_amount(tax):
    """
    Get the actual tax amount from the Purchase Taxes and Charges row.

    Purchase Taxes and Charges normally stores the calculated tax
    amount in tax_amount.
    """

    if tax.get("tax_amount") is not None:
        return flt(tax.tax_amount)

    if tax.get("amount") is not None:
        return flt(tax.amount)

    return 0


def get_taxable_base(tax, tax_amount, rate):
    """
    Calculate taxable base dynamically.

    Example:

        CGST = 540
        Rate = 9%

        Taxable Base = 540 / 9 * 100
                     = 6000
    """

    if not rate:
        return 0

    # Prefer ERPNext's stored base amount where available.
    if tax.get("base_tax_amount") and tax.get("base_amount"):
        base_tax_amount = flt(tax.base_tax_amount)
        base_amount = flt(tax.base_amount)

        if base_tax_amount:
            return abs(base_amount) * (
                abs(tax_amount) / abs(base_tax_amount)
            )

    return abs(tax_amount) * 100 / abs(rate)


def nearly_equal(value1, value2, tolerance=0.0001):
    return abs(flt(value1) - flt(value2)) <= tolerance


def flt(value):
    try:
        return frappe.utils.flt(value)
    except Exception:
        return float(value or 0)
