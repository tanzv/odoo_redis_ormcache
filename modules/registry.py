# -*- coding: utf-8 -*-
from odoo.tools import (assertion_report, config, existing_tables,
                        lazy_classproperty, lazy_property, table_exists,
                        topological_sort, OrderedSet)
import logging
import odoo
from ..tools.RedisLRU import RedisLRU
import redis
from odoo.modules.registry import Registry
from odoo import tools

_logger = logging.getLogger(__name__)
config = tools.config.options


@lazy_property
def cache(self):
    r = redis.Redis(
        host=config.get('redis_host', 'localhost'), port=config.get('redis_port', 6379),
        decode_responses=True,
        password=config.get('redis_password', None),
        db=config.get('redis_db_index', 1),
    )
    # r = redis.StrictRedis.from_url(odoo.tools.config['ormcache_redis_url'])
    return RedisLRU(r, self.db_name, odoo.tools.config.get('ormcache_redis_expire'))


if config.get('redis_orm_cache'):
    Registry.cache = cache
