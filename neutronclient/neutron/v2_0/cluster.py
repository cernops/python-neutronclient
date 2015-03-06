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
from neutronclient.openstack.common.gettextutils import _
from neutronclient.neutron import v2_0 as neutronV20


def add_updatable_arguments(parser):
    parser.add_argument(
        'name', metavar='NAME',
        help=_('Name of this cluster.'))


def updatable_args2body(parsed_args, body, for_create=True):
    if parsed_args.name:
        body['cluster'].update({'name': parsed_args.name})

def _format_subnets(network):
    try:
        return '\n'.join([' '.join([s['id'], s.get('cidr', '')])
                          for s in network['subnets']])
    except Exception:
        return ''

class ListCluster(neutronV20.ListCommand):
    """List clusters."""

    resource = 'cluster'
    _formatters = {'subnets': _format_subnets, }
    list_columns = ['id', 'name', 'subnets']
    pagination_support = True
    sorting_support = True

    def extend_list(self, data, parsed_args):
        """Add subnet information to a network list."""
        neutron_client = self.get_client()
        search_opts = {'fields': ['id', 'cidr']}
        if self.pagination_support:
            page_size = parsed_args.page_size
            if page_size:
                search_opts.update({'limit': page_size})
        subnet_ids = []
        for n in data:
            if 'subnets' in n:
                subnet_ids.extend(n['subnets'])

        def _get_subnet_list(sub_ids):
            search_opts['id'] = sub_ids
            return neutron_client.list_subnets(
                **search_opts).get('subnets', [])

        try:
            subnets = _get_subnet_list(subnet_ids)
        except exceptions.RequestURITooLong as uri_len_exc:
            # The URI is too long because of too many subnet_id filters
            # Use the excess attribute of the exception to know how many
            # subnet_id filters can be inserted into a single request
            subnet_count = len(subnet_ids)
            max_size = ((self.subnet_id_filter_len * subnet_count) -
                        uri_len_exc.excess)
            chunk_size = max_size / self.subnet_id_filter_len
            subnets = []
            for i in range(0, subnet_count, chunk_size):
                subnets.extend(
                    _get_subnet_list(subnet_ids[i: i + chunk_size]))

        subnet_dict = dict([(s['id'], s) for s in subnets])
        for n in data:
            if 'subnets' in n:
                n['subnets'] = [(subnet_dict.get(s) or {"id": s})
                                for s in n['subnets']]


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
