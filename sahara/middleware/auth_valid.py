# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webob.exc as ex

from sahara.openstack.common import log as logging
import sahara.openstack.commons as commons


LOG = logging.getLogger(__name__)


class AuthValidator:
    """Handles token auth results and tenants."""

    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        """Ensures that tenants in url and token are equal.

        Handle incoming request by checking tenant info prom the headers and
        url ({tenant_id} url attribute).

        Pass request downstream on success.
        Reject request if tenant_id from headers not equals to tenant_id from
        url.
        """
        token_tenant = env['HTTP_X_TENANT_ID']
        if not token_tenant:
            LOG.warn("Can't get tenant_id from env")
            resp = ex.HTTPServiceUnavailable()
            return resp(env, start_response)

        path = env['PATH_INFO']
        if path != '/':
            version, url_tenant, rest = commons.split_path(path, 3, 3, True)
            if not version or not url_tenant or not rest:
                LOG.info("Incorrect path: %s", path)
                resp = ex.HTTPNotFound("Incorrect path")
                return resp(env, start_response)

            if token_tenant != url_tenant:
                LOG.debug("Unauthorized: token tenant != requested tenant")
                resp = ex.HTTPUnauthorized('Token tenant != requested tenant')
                return resp(env, start_response)

        return self.app(env, start_response)


def wrap(app):
    """Wrap wsgi application with auth validator check."""

    return AuthValidator(app)
