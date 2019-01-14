# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from copy import deepcopy

import ibm_db
import pytest

from datadog_checks.dev import WaitFor, docker_run, run_command
from datadog_checks.ibm_db2 import IbmDb2Check
from .common import COMPOSE_FILE, CONFIG


class DbManager(object):
    def __init__(self, config):
        self.target, self.username, self.password = IbmDb2Check.get_connection_data(config)
        self.db_name = config['db']
        self.conn = None

    def initialize(self):
        run_command(
            'docker exec ibm_db2 su - db2inst1 -c "db2 -c create db datadog using codeset utf-8 territory us"',
            check=True,
        )

    def connect(self):
        ibm_db.close(ibm_db.connect(self.target, self.username, self.password))


@pytest.fixture(scope='session')
def dd_environment():
    db = DbManager(CONFIG)

    with docker_run(COMPOSE_FILE, conditions=[db.initialize, WaitFor(db.connect)]):
        yield CONFIG


@pytest.fixture
def instance():
    return deepcopy(CONFIG)
