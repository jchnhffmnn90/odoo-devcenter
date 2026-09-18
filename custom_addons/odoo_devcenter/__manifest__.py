{
    "name": "Odoo DevCenter Dashboard",
    "version": "1.0",
    "summary": "Live System & Odoo Monitoring Dashboard",
    "description": """
        Provides a real-time dashboard for monitoring Odoo CPU, RAM,
        Disk I/O, Connections, and general system health directly within the Odoo backend.
    """,
    "category": "Tools",
    "author": "jchnhffmnn90",
    "depends": ["base", "web"],
    "data": [
        "views/dashboard_action.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "odoo_devcenter/static/src/components/dashboard/**/*.js",
            "odoo_devcenter/static/src/components/dashboard/**/*.xml",
            "odoo_devcenter/static/src/components/dashboard/**/*.css",
        ],
    },
    "installable": True,
    "application": True,
}
