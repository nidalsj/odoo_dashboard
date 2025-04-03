{
    'name': 'ODOO Dashboard',
    'version': '18.0.1.0.0',
    'author': 'Nidal SJ',
    'website': "https://github.com/nidalsj",
    'license': 'AGPL-3',
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
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