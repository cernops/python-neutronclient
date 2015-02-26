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
#

import argparse

from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.i18n import _
from neutronclient.neutron import v2_0 as neutronV20


def add_updatable_arguments(parser):
    parser.add_argument(
        'name', metavar='NAME',
        help=_('Name of this cluster.'))


def updatable_args2body(parsed_args, body, for_create=True):
    if parsed_args.name:
        body['cluster'].update({'name': parsed_args.name})


class ListCluster(neutronV20.ListCommand):
    """List clusters."""

    resource = 'cluster'
    _formatters = { }
    list_columns = ['id', 'name']
    pagination_support = True
    sorting_support = True


class ShowCluster(neutronV20.ShowCommand):
    """Show information of a given cluster."""

    resource = 'cluster'


class CreateCluster(neutronV20.CreateCommand):
    """Create a cluster with a given name."""

    resource = 'cluster'

    def add_known_arguments(self, parser):
        add_updatable_arguments(parser)

    def args2body(self, parsed_args):
        body = {'cluster': {'name': parsed_args.name } }
        updatable_args2body(parsed_args, body)
        if parsed_args.tenant_id:
            body['cluster'].update({'tenant_id': parsed_args.tenant_id})
        return body


class DeleteCluster(neutronV20.DeleteCommand):
    """Delete a given cluster."""

    resource = 'cluster'


class UpdateCluster(neutronV20.UpdateCommand):
    """Update cluster's information."""

    resource = 'cluster'

    def add_known_arguments(self, parser):
        add_updatable_arguments(parser)

    def args2body(self, parsed_args):
        body = {'cluster': {}}
        updatable_args2body(parsed_args, body, for_create=False)
        return body


class AddSubnet(neutronV20.CreateCommand):
    """Add a subnet to a cluster"""

    resource = 'cluster'

    def call_api(self, neutron_client, cluster_id, body):
        return neutron_client.cluster_insert_subnet(cluster_id, body)

    def args2body(self, parsed_args):
        _subnet = ''
        if parsed_args.subnet_id:
            _subnet = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'subnet',
                parsed_args.subnet_id)
        body = {'cluster': {'subnet_id': _subnet}}
        neutronV20.update_dict(parsed_args, body, [])

        if parsed_args.tenant_id:
            body['cluster'].update({'tenant_id': parsed_args.tenant_id})

        return body


    def get_parser(self, prog_name):
        parser = super(AddSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=_('ID or name of %s to update.') % self.resource)
        parser.add_argument(
            'subnet_id', metavar='SUBNET',
            help=_('Subnet to add to the cluster'))
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        self.call_api(neutron_client, _id, body)

class RemoveSubnet(neutronV20.CreateCommand):
    """Removes a subnet from a cluster"""

    resource = 'cluster'

    def call_api(self, neutron_client, cluster_id, body):
        return neutron_client.cluster_remove_subnet(cluster_id, body)

    def args2body(self, parsed_args):
        _subnet = ''
        if parsed_args.subnet_id:
            _subnet = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'subnet',
                parsed_args.subnet_id)
        body = {'cluster': {'subnet_id': _subnet}}
        neutronV20.update_dict(parsed_args, body, [])

        if parsed_args.tenant_id:
            body['cluster'].update({'tenant_id': parsed_args.tenant_id})

        return body


    def get_parser(self, prog_name):
        parser = super(RemoveSubnet, self).get_parser(prog_name)
        parser.add_argument(
            'id', metavar=self.resource.upper(),
            help=_('ID or name of %s to update.') % self.resource)
        parser.add_argument(
            'subnet_id', metavar='SUBNET',
            help=_('Subnet to remove from the cluster'))
        self.add_known_arguments(parser)
        return parser

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        self.call_api(neutron_client, _id, body)
