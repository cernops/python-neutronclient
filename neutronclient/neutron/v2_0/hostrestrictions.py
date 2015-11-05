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

class ShowHost(neutronV20.ShowCommand):
    """Show restrictions about a given host."""

    resource = 'host'
    allow_names = False
