{
    'name': 'ODOO Dashboard',
    'version': '18.0.1.0.0',
    'author': 'Nidal SJ',
    'website': "https://github.com/nidalsj",
    'license': 'AGPL-3',
    'depends': ['base', 'sale', 'hr', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config.xml',
        'views/date_filter.xml',
        'views/dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_dashboard/static/src/components/**/*.js',
            'odoo_dashboard/static/src/components/**/*.xml',
            'odoo_dashboard/static/src/components/**/*.scss'
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}