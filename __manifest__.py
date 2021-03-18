# -*- coding: utf-8 -*-
{
    'name': "Odoo redis orm cache",

    'summary': """
        ormcache in redis""",
    'description': """
        redis_host=127.0.0.1
        redis_port=6379
        redis_password=xxx or null
        redis_redis_db_index = 1
        max_cron_threads = x     
    """,
    'author': "tanzv",
    'category': 'Technical Settings',
    'version': '0.1',

    'depends': ['base'],
    "external_dependencies": {
        'python': ['redis'],
    },

}
