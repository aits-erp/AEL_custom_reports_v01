from __future__ import unicode_literals

import frappe
from frappe import _


def execute(filters=None):
    filters = frappe._dict(filters or {})

    validate_filters(filters)

    columns = get_columns()
    data = get_data(filters)

    # Add our own total row
    if data:
        data.append(get_total_row(data))

    return columns, data


# ======================================================================
# VALIDATION
# ======================================================================

def validate_filters(filters):

    if not filters.get("from_date"):
        frappe.throw(_("From Date is mandatory."))

    if not filters.get("to_date"):
        frappe.throw(_("To Date is mandatory."))

    if filters.from_date > filters.to_date:
        frappe.throw(
            _("From Date cannot be greater than To Date.")
        )


# ======================================================================
# COLUMNS
# ======================================================================

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
            "width": 140
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


# ======================================================================
# GET PURCHASE INVOICES
# ======================================================================

def get_data(filters):

    conditions = [
        "pi.docstatus = 1",
        "pi.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    ]

    values = {
        "from_date": filters.from_date,
        "to_date": filters.to_date
    }

    if filters.get("supplier"):
        conditions.append(
            "pi.supplier = %(supplier)s"
        )

        values["supplier"] = filters.supplier

    where_clause = " AND ".join(conditions)

    invoices = frappe.db.sql(
        """
        SELECT
            pi.name,
            pi.posting_date,
            pi.supplier,
            pi.bill_no,
            pi.net_total,
            pi.grand_total,
            pi.rounding_adjustment

        FROM `tabPurchase Invoice` pi

        WHERE {where_clause}

        ORDER BY
            pi.posting_date ASC,
            pi.name ASC
        """.format(
            where_clause=where_clause
        ),
        values,
        as_dict=True
    )

    if not invoices:
        return []

    invoice_names = [
        invoice.name
        for invoice in invoices
    ]

    # --------------------------------------------------------------
    # Get actual Purchase Taxes and Charges fields
    # from your ERPNext v15 database.
    # --------------------------------------------------------------

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
            "parents": invoice_names
        },
        as_dict=True
    )

    taxes_by_invoice = {}

    for tax in taxes:
        taxes_by_invoice.setdefault(
            tax.parent,
            []
        ).append(tax)

    data = []

    for invoice in invoices:

        invoice_taxes = taxes_by_invoice.get(
            invoice.name,
            []
        )

        row = calculate_invoice(
            invoice,
            invoice_taxes
        )

        data.append(row)

    return data


# ======================================================================
# CALCULATE ONE INVOICE
# ======================================================================

def calculate_invoice(invoice, taxes):

    input_cgst_9 = 0
    input_sgst_9 = 0
    input_igst_18 = 0

    input_cgst_2_5 = 0
    input_sgst_2_5 = 0

    tds_2 = 0
    tds_1 = 0
    interest_on_tds = 0

    # --------------------------------------------------------------
    # Taxable purchase bases
    # --------------------------------------------------------------

    purchase_base_18 = 0
    purchase_base_5 = 0

    # All GST taxable bases.
    # This is used to calculate non-taxable purchase.
    gst_bases = {}

    # --------------------------------------------------------------
    # Round Off comes directly from Purchase Invoice
    # --------------------------------------------------------------

    round_off = flt(
        invoice.rounding_adjustment
    )

    # --------------------------------------------------------------
    # Process every Purchase Taxes and Charges row
    # --------------------------------------------------------------

    for tax in taxes:

        rate = flt(tax.rate)

        tax_amount = get_tax_amount(tax)

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
        # INTEREST ON TDS
        # ==========================================================

        if (
            "interest" in account_text
            and "tds" in account_text
        ):
            interest_on_tds += tax_amount
            continue

        # ==========================================================
        # TDS
        #
        # Use ERPNext's actual:
        # is_tax_withholding_account
        #
        # No supplier/account name hardcoding.
        # ==========================================================

        if (
            cint(tax.is_tax_withholding_account)
            or "tds" in account_text
            or "withholding" in account_text
        ):

            if nearly_equal(rate, 2):
                tds_2 += tax_amount

            elif nearly_equal(rate, 1):
                tds_1 += tax_amount

            continue

        # ==========================================================
        # CGST 9%
        # ==========================================================

        if (
            "cgst" in account_text
            and nearly_equal(rate, 9)
        ):

            input_cgst_9 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            purchase_base_18 += taxable_base

            add_gst_base(
                gst_bases,
                "CGST",
                rate,
                taxable_base
            )

            continue

        # ==========================================================
        # SGST 9%
        # ==========================================================

        if (
            "sgst" in account_text
            and nearly_equal(rate, 9)
        ):

            input_sgst_9 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            add_gst_base(
                gst_bases,
                "SGST",
                rate,
                taxable_base
            )

            continue

        # ==========================================================
        # IGST 18%
        # ==========================================================

        if (
            "igst" in account_text
            and nearly_equal(rate, 18)
        ):

            input_igst_18 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            purchase_base_18 += taxable_base

            add_gst_base(
                gst_bases,
                "IGST",
                rate,
                taxable_base
            )

            continue

        # ==========================================================
        # CGST 2.5%
        # ==========================================================

        if (
            "cgst" in account_text
            and nearly_equal(rate, 2.5)
        ):

            input_cgst_2_5 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            purchase_base_5 += taxable_base

            add_gst_base(
                gst_bases,
                "CGST",
                rate,
                taxable_base
            )

            continue

        # ==========================================================
        # SGST 2.5%
        # ==========================================================

        if (
            "sgst" in account_text
            and nearly_equal(rate, 2.5)
        ):

            input_sgst_2_5 += tax_amount

            taxable_base = get_taxable_base(
                tax,
                tax_amount,
                rate
            )

            add_gst_base(
                gst_bases,
                "SGST",
                rate,
                taxable_base
            )

            continue

    # ==============================================================
    # PURCHASE 18%
    # ==============================================================

    purchase_18 = purchase_base_18

    # ==============================================================
    # PURCHASE 5%
    # ==============================================================

    purchase_5 = purchase_base_5

    # ==============================================================
    # ALL GST TAXABLE BASE
    #
    # CGST + SGST are not double counted.
    #
    # Example:
    #
    # CGST 9% = base 6000
    # SGST 9% = base 6000
    #
    # GST taxable base = 6000, NOT 12000.
    # ==============================================================

    gst_taxable_total = get_unique_gst_base_total(
        gst_bases
    )

    # ==============================================================
    # NON TAXABLE PURCHASE
    #
    # Net Total minus all GST taxable amounts.
    #
    # This prevents other GST rates from being incorrectly
    # treated as non-taxable.
    # ==============================================================

    net_total = flt(
        invoice.net_total
    )

    purchase_non_taxable = max(
        net_total - gst_taxable_total,
        0
    )

    # ==============================================================
    # FINAL ROW
    # ==============================================================

    return {
        "date": invoice.posting_date,

        "particulars": invoice.supplier,

        "voucher_type": "Purchase Invoice",

        "voucher_no": invoice.name,

        "voucher_ref_no": invoice.bill_no or "",

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
            round_off
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

        "interest_on_tds": flt(
            interest_on_tds
        )
    }


# ======================================================================
# TAX AMOUNT
# ======================================================================

def get_tax_amount(tax):

    value = tax.get(
        "tax_amount_after_discount_amount"
    )

    if value is not None:
        return flt(value)

    value = tax.get("tax_amount")

    if value is not None:
        return flt(value)

    return 0


# ======================================================================
# TAXABLE BASE
# ======================================================================

def get_taxable_base(tax, tax_amount, rate):

    if not rate:
        return 0

    # --------------------------------------------------------------
    # ERPNext stores company-currency tax amount here.
    # base_total is cumulative total, so it must NOT be used as
    # taxable base.
    # --------------------------------------------------------------

    base_tax_amount = flt(
        tax.get("base_tax_amount")
    )

    base_tax_after_discount = flt(
        tax.get(
            "base_tax_amount_after_discount_amount"
        )
    )

    if base_tax_after_discount:
        return abs(base_tax_after_discount) * 100 / abs(rate)

    if base_tax_amount:
        return abs(base_tax_amount) * 100 / abs(rate)

    return abs(tax_amount) * 100 / abs(rate)


# ======================================================================
# STORE GST BASE
# ======================================================================

def add_gst_base(
    gst_bases,
    tax_type,
    rate,
    taxable_base
):

    key = round(rate, 4)

    if key not in gst_bases:
        gst_bases[key] = {}

    current = gst_bases[key].get(
        tax_type,
        0
    )

    gst_bases[key][tax_type] = max(
        current,
        abs(taxable_base)
    )


# ======================================================================
# UNIQUE GST BASE
# ======================================================================

def get_unique_gst_base_total(gst_bases):

    total = 0

    for rate, components in gst_bases.items():

        igst = flt(
            components.get("IGST", 0)
        )

        cgst = flt(
            components.get("CGST", 0)
        )

        sgst = flt(
            components.get("SGST", 0)
        )

        # ----------------------------------------------------------
        # IGST is already the complete taxable base.
        # ----------------------------------------------------------

        if igst:
            total += igst

        # ----------------------------------------------------------
        # For CGST + SGST, they represent the SAME taxable base.
        # Do not add both.
        # ----------------------------------------------------------

        else:
            total += max(
                cgst,
                sgst
            )

    return total


# ======================================================================
# TOTAL ROW
# ======================================================================

def get_total_row(data):

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
        "interest_on_tds"
    ]

    total_row = {
        "date": None,
        "particulars": "Total",
        "voucher_type": "",
        "voucher_no": "",
        "voucher_ref_no": ""
    }

    for fieldname in numeric_fields:

        total_row[fieldname] = sum(
            flt(row.get(fieldname))
            for row in data
        )

    return total_row


# ======================================================================
# HELPERS
# ======================================================================

def nearly_equal(
    value1,
    value2,
    tolerance=0.0001
):

    return abs(
        flt(value1) - flt(value2)
    ) <= tolerance


def flt(value):

    return frappe.utils.flt(
        value
    )


def cint(value):

    return frappe.utils.cint(
        value
    )