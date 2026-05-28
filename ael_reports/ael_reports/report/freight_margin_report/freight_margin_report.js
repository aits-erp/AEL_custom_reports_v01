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

//     formatter: function (value, row, column, data, default_formatter) {
//         value = default_formatter(value, row, column, data);

//         const BLANK_ON_CHILD = new Set([
//             "customer",
//             "sales_order",
//             "purchase_order",
//             "purchase_invoice",
//             "origin_country",
//             "destination_country",
//             "mode",
//             "cbm",
//             "weight",
//             "job_no"
//         ]);

//         if (data && data.indent === 1) {

//             if (column.fieldname === "invoice") {
//                 return `<span style="color:var(--text-muted);font-size:0.92em;padding-left:4px;">
//                             ${data.invoice || ""}
//                         </span>`;
//             }

//             if (BLANK_ON_CHILD.has(column.fieldname)) {
//                 return "";
//             }

//             return `<span style="color:var(--text-muted);font-size:0.92em;">
//                         ${value || ""}
//                     </span>`;
//         }

//         if (column.fieldname === "invoice" && data && data.invoice) {
//             return `<a href="/app/sales-invoice/${encodeURIComponent(data.invoice)}"
//                        style="font-weight:500;"
//                        onclick="event.stopPropagation()">
//                        ${data.invoice}
//                    </a>`;
//         }

//         if (column.fieldname === "sales_order" && data && data.sales_order) {
//             return `<a href="/app/sales-order/${encodeURIComponent(data.sales_order)}"
//                        onclick="event.stopPropagation()">
//                        ${data.sales_order}
//                    </a>`;
//         }

//         if (column.fieldname === "purchase_order" && data && data.purchase_order) {
//             return `<a href="/app/purchase-order/${encodeURIComponent(data.purchase_order)}"
//                        onclick="event.stopPropagation()">
//                        ${data.purchase_order}
//                    </a>`;
//         }

//         if (column.fieldname === "purchase_invoice" && data && data.purchase_invoice) {
//             return `<a href="/app/purchase-invoice/${encodeURIComponent(data.purchase_invoice)}"
//                        onclick="event.stopPropagation()">
//                        ${data.purchase_invoice}
//                    </a>`;
//         }

//         return value;
//     },

//          get_datatable_options: function (options) {
//             options.treeView = true;
//             options.initialDepth = 0;
//             return options;
//         }
//     };




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
            fieldname: "total_amount_view",
            label: "Total Amount",
            fieldtype: "Select",
            options: ["Invoice Based", "Total Based"],
            default: "Total Based"
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

        const BLANK_ON_CHILD = new Set([
            "customer",
            "sales_order",
            "purchase_order",
            "purchase_invoice",
            "origin_country",
            "destination_country",
            "mode",
            "cbm",
            "weight",
            "job_no"
        ]);

        if (data && data.indent === 1) {

            if (column.fieldname === "invoice") {
                return `<span style="color:var(--text-muted);font-size:0.92em;padding-left:4px;">
                            ${data.invoice || ""}
                        </span>`;
            }

            if (BLANK_ON_CHILD.has(column.fieldname)) {
                return "";
            }

            return `<span style="color:var(--text-muted);font-size:0.92em;">
                        ${value || ""}
                    </span>`;
        }

        if (column.fieldname === "invoice" && data && data.invoice) {
            return `<a href="/app/sales-invoice/${encodeURIComponent(data.invoice)}"
                       style="font-weight:500;"
                       onclick="event.stopPropagation()">
                       ${data.invoice}
                   </a>`;
        }9898

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
        options.initialDepth = 0;
        return options;
    }
};



