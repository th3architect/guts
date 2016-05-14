# Copyright (c) 2015 Aptira Pty Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""The source instances."""

import six
import webob

from oslo_config import cfg
from oslo_log import log as logging
from oslo_utils import timeutils

from guts.api import extensions
from guts.api.openstack import wsgi
from guts import exception
from guts import objects
from guts import rpc
from guts import utils

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

authorize = extensions.extension_authorizer('migration', 'instances')


class InstancesController(wsgi.Controller):
    """The instance API controller for the OpenStack API."""

    def __init__(self, ext_mgr):
        self.ext_mgr = ext_mgr
        super(InstancesController, self).__init__()

    def _notify_source_error(self, ctxt, method, err,
                             source=None, id=None, name=None):
        payload = dict(sources=source, name=name, id=id, error_message=err)
        rpc.get_notifier('source').error(ctxt, method, payload)

    def _notify_source_info(self, ctxt, method, source):
        payload = dict(sources=source)
        rpc.get_notifier('source').info(ctxt, method, payload)

    def index(self, req):
        """Returns the list of Instances."""
        context = req.environ['guts.context']
        instances = objects.ResourceList.get_all_by_type(context, 'instance')

        instances = []
        for i in instances:
            instance = {}
            instance['id'] = i.id
            instance['migrated'] = i.migrated
            instance['source'] = i.source

            instances.append(instance)
        return dict(instances=instances)

    def show(self, req, instance_id):
        """Returns data about given instance."""
        context = req.environ['guts.context']
        try:
            inst = objects.Resource.get(context, instance_id)
        except exception.NotFound:
            raise webob.exc.HTTPNotFound()

        instance = {}
        instance['id'] = inst.id
        instance['migrated'] = inst.migrated
        instance['source'] = inst.source
        instance['properties'] = inst.properties

        return {'instance': instance}

def create_resource(ext_mgr):
    return wsgi.Resource(InstancesController(ext_mgr))
