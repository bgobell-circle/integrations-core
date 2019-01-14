# (C) Datadog, Inc. 2019
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import re

CONN_STRING_PASSWORD = re.compile('(?:^|;)pwd=([^;]+)')


def scrub_connection_string(conn_str):
    return CONN_STRING_PASSWORD.sub(_scrub_password, conn_str)


def _scrub_password(match):
    password = match.group(1)
    return match.group(0).replace(password, '*' * len(password))
