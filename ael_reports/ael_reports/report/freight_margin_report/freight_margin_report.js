frappe.query_reports["Freight Margin Report"] = {

    filters: [

        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_default("company"),
            reqd: 1
        },

        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },

        {
            fieldname: "invoice_type",
            label: "Invoice Type",
            fieldtype: "Select",
            options: ["Invoice", "Credit Note"],
            default: "Invoice"
        },

        {
            fieldname: "customer",
            label: "Customer",
            fieldtype: "Link",
            options: "Customer"
        },

        {
            fieldname: "sales_invoice",
            label: "Sales Invoice",
            fieldtype: "Link",
            options: "Sales Invoice"
        },

        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group"
        },

        {
            fieldname: "warehouse",
            label: "Warehouse",
            fieldtype: "Link",
            options: "Warehouse"
        },

        {
            fieldname: "project",
            label: "Project",
            fieldtype: "Link",
            options: "Project"
        },

        {
            fieldname: "include_returned",
            label: "Include Returned Invoices",
            fieldtype: "Check",
            default: 0
        }

    ]
};