// frappe.query_reports["Freight Margin Report"] = {

//     filters: [

//         {
//             fieldname: "company",
//             label: "Company",
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_default("company"),
//             reqd: 1
//         },

//         {
//             fieldname: "from_date",
//             label: "From Date",
//             fieldtype: "Date",
//             default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
//             reqd: 1
//         },

//         {
//             fieldname: "to_date",
//             label: "To Date",
//             fieldtype: "Date",
//             default: frappe.datetime.get_today(),
//             reqd: 1
//         },

//         {
//             fieldname: "invoice_type",
//             label: "Invoice Type",
//             fieldtype: "Select",
//             options: ["Invoice", "Credit Note"],
//             default: "Invoice"
//         },

//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         },

//         {
//             fieldname: "sales_invoice",
//             label: "Sales Invoice",
//             fieldtype: "Link",
//             options: "Sales Invoice"
//         },

//         {
//             fieldname: "item_group",
//             label: "Item Group",
//             fieldtype: "Link",
//             options: "Item Group"
//         },

//         {
//             fieldname: "warehouse",
//             label: "Warehouse",
//             fieldtype: "Link",
//             options: "Warehouse"
//         },

//         {
//             fieldname: "project",
//             label: "Project",
//             fieldtype: "Link",
//             options: "Project"
//         },

//         {
//             fieldname: "include_returned",
//             label: "Include Returned Invoices",
//             fieldtype: "Check",
//             default: 0
//         }

//     ]
// };


// frappe.query_reports["Freight Margin Report"] = {

//     filters: [
//         {
//             fieldname: "company",
//             label: "Company",
//             fieldtype: "Link",
//             options: "Company",
//             default: frappe.defaults.get_default("company"),
//             reqd: 1
//         },
//         {
//             fieldname: "from_date",
//             label: "From Date",
//             fieldtype: "Date",
//             default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
//             reqd: 1
//         },
//         {
//             fieldname: "to_date",
//             label: "To Date",
//             fieldtype: "Date",
//             default: frappe.datetime.get_today(),
//             reqd: 1
//         },
//         {
//             fieldname: "invoice_type",
//             label: "Invoice Type",
//             fieldtype: "Select",
//             options: ["Invoice", "Credit Note"],
//             default: "Invoice"
//         },
//         {
//             fieldname: "customer",
//             label: "Customer",
//             fieldtype: "Link",
//             options: "Customer"
//         },
//         {
//             fieldname: "sales_invoice",
//             label: "Sales Invoice",
//             fieldtype: "Link",
//             options: "Sales Invoice"
//         },
//         {
//             fieldname: "item_group",
//             label: "Item Group",
//             fieldtype: "Link",
//             options: "Item Group"
//         },
//         {
//             fieldname: "warehouse",
//             label: "Warehouse",
//             fieldtype: "Link",
//             options: "Warehouse"
//         },
//         {
//             fieldname: "project",
//             label: "Project",
//             fieldtype: "Link",
//             options: "Project"
//         },
//         {
//             fieldname: "include_returned",
//             label: "Include Returned Invoices",
//             fieldtype: "Check",
//             default: 0
//         }
//     ],

//     // ── Expand / collapse child rows on invoice click ─────────────────
//     onload: function (report) {
//         // Store collapsed state per invoice
//         report._collapsed = {};
//     },

//     formatter: function (value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);

//         // Highlight child rows with a subtle background
//         if (data && data.indent === 1) {
//             value = `<span style="color: var(--text-muted); font-size: 0.92em;">${value || ""}</span>`;
//         }

//         // Make the invoice link open the Sales Invoice form
//         if (column.fieldname === "invoice" && data && data.indent === 0 && data.invoice) {
//             value = `<a href="/app/sales-invoice/${encodeURIComponent(data.invoice)}"
//                         style="color: var(--text-on-blue); font-weight: 500;"
//                         onclick="event.stopPropagation()">
//                         ${data.invoice}
//                      </a>`;
//         }

//         // Clickable SO link
//         if (column.fieldname === "sales_order" && data && data.sales_order) {
//             value = `<a href="/app/sales-order/${encodeURIComponent(data.sales_order)}"
//                         onclick="event.stopPropagation()">
//                         ${data.sales_order}
//                      </a>`;
//         }

//         // Clickable PO link
//         if (column.fieldname === "purchase_order" && data && data.purchase_order) {
//             value = `<a href="/app/purchase-order/${encodeURIComponent(data.purchase_order)}"
//                         onclick="event.stopPropagation()">
//                         ${data.purchase_order}
//                      </a>`;
//         }

//         // Clickable PI link
//         if (column.fieldname === "purchase_invoice" && data && data.purchase_invoice) {
//             value = `<a href="/app/purchase-invoice/${encodeURIComponent(data.purchase_invoice)}"
//                         onclick="event.stopPropagation()">
//                         ${data.purchase_invoice}
//                      </a>`;
//         }

//         return value;
//     },

//     // Row-level CSS classes for visual distinction
//     get_datatable_options: function (options) {
//         options.treeView = true;  // enables Frappe's built-in indent/expand behaviour
//         return options;
//     }
// };



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
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // ── child rows (item lines) ───────────────────────────────────
        if (data && data.indent === 1) {
            // invoice column on child row holds item name as plain text
            // — do NOT render as a link
            if (column.fieldname === "invoice") {
                return `<span style="color:var(--text-muted);font-size:0.92em;padding-left:4px;">
                            ${data.invoice || ""}
                        </span>`;
            }
            // all other child cells — muted styling
            return `<span style="color:var(--text-muted);font-size:0.92em;">
                        ${value || ""}
                    </span>`;
        }

        // ── parent rows (invoice summary) ─────────────────────────────
        if (column.fieldname === "invoice" && data && data.invoice) {
            return `<a href="/app/sales-invoice/${encodeURIComponent(data.invoice)}"
                       style="font-weight:500;"
                       onclick="event.stopPropagation()">
                       ${data.invoice}
                   </a>`;
        }

        if (column.fieldname === "sales_order" && data && data.sales_order) {
            return `<a href="/app/sales-order/${encodeURIComponent(data.sales_order)}"
                       onclick="event.stopPropagation()">
                       ${data.sales_order}
                   </a>`;
        }

        if (column.fieldname === "purchase_order" && data && data.purchase_order) {
            return `<a href="/app/purchase-order/${encodeURIComponent(data.purchase_order)}"
                       onclick="event.stopPropagation()">
                       ${data.purchase_order}
                   </a>`;
        }

        if (column.fieldname === "purchase_invoice" && data && data.purchase_invoice) {
            return `<a href="/app/purchase-invoice/${encodeURIComponent(data.purchase_invoice)}"
                       onclick="event.stopPropagation()">
                       ${data.purchase_invoice}
                   </a>`;
        }

        return value;
    },

    get_datatable_options: function (options) {
        options.treeView = true;
        return options;
    }
};