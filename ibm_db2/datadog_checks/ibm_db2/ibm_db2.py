# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import ibm_db

from datadog_checks.base import AgentCheck
from datadog_checks.base.utils.containers import hash_mutable
from .utils import scrub_connection_string


class IbmDb2Check(AgentCheck):
    def __init__(self, name, init_config, agentConfig, instances=None):
        super(IbmDb2Check, self).__init__(name, init_config, agentConfig, instances)
        self._config_cache = {}

    def check(self, instance):
        config = self.get_config(instance)
        if config is None:
            return

        conn = config['connection']
        tags = list(config['tags'])

        db_version = ibm_db.get_db_info(conn, ibm_db.SQL_DBMS_VER)
        tags.append('version:{}'.format(db_version))

        self.gauge('ibm_db2.version', 0, tags=tags)

    def get_config(self, instance):
        instance_id = hash_mutable(instance)
        config = self._config_cache.get(instance_id)

        if config is None:
            config = {
                'db': instance.get('db', ''),
                'db_username': instance.get('db_username', ''),
                'db_password': instance.get('db_password', ''),
                'remote_host': instance.get('remote_host', ''),
                'remote_port': instance.get('remote_port', 5000),
                'tags': instance.get('tags', []),
            }

            config['connection'] = self.get_connection(config)
            if not config['connection']:
                return

            self._config_cache[instance_id] = config

        return config

    def get_connection(self, config):
        target, username, password = self.get_connection_data(config)

        try:
            connection = ibm_db.connect(target, username, password)
        except Exception as e:
            if config['remote_host']:
                self.log.error('Unable to connect with `{}`: {}'.format(scrub_connection_string(target), e))
            else:
                self.log.error('Unable to connect to database `{}` as user `{}`: {}'.format(target, username, e))
        else:
            return connection

    @classmethod
    def get_connection_data(cls, config):
        if config['remote_host']:
            target = 'database={};hostname={};port={};protocol=tcpip;uid={};pwd={}'.format(
                config['db'], config['remote_host'], config['remote_port'], config['db_username'], config['db_password']
            )
            username = ''
            password = ''
        else:
            target = config['db']
            username = config['db_username']
            password = config['db_password']

        return target, username, password
