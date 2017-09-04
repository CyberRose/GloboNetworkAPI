# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json
from enum import Enum

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from django.core.exceptions import ObjectDoesNotExist

from networkapi.plugins import exceptions
from networkapi.plugins.SDN.base import BaseSdnPlugin
from networkapi.equipamento.models import EquipamentoAcesso
from networkapi.plugins.SDN.ODL.flows.acl import AclFlowBuilder

log = logging.getLogger(__name__)


class FlowTypes(Enum):
    """ Inner class that holds the Enumeration of flow types """
    ACL = 0


class ODLPlugin(BaseSdnPlugin):
    """
    Plugin base para interação com controlador ODL
    """

    versions = [ "BERYLLIUM", "BORON", "CARBON" ]

    def __init__(self, **kwargs):

        super(ODLPlugin, self).__init__(**kwargs)

        try:
            if not isinstance(self.equipment_access, EquipamentoAcesso):
                msg = 'equipment_access is not of EquipamentoAcesso type'
                log.info(msg)
                raise TypeError(msg)

        except (AttributeError, TypeError):
            # If AttributeError raised, equipment_access do not exists
            self.equipment_access = self._get_equipment_access()

        if self.version not in self.versions:
            log.error("Invalid version at ODL Controller initialization")
            raise exceptions.ValueInvalid(msg="Invalid version at ODL Controller initialization")

    def add_flow(self, data=None, flow_id=0, flow_type=FlowTypes.ACL):

        if flow_type == FlowTypes.ACL:
            builder = AclFlowBuilder(data)

            flows_set = builder.build()
        try:
            for flows in flows_set:
                for flow in flows['flow']:

                    self._flow(flow_id=flow['id'],
                               method='put',
                               data=json.dumps({'flow': [flow]}))
        except HTTPError as e:
            raise exceptions.CommandErrorException(
                                msg=self._parse_errors(e.response.json()))


    def del_flow(self, flow_id=0):
        return self._flow(flow_id=flow_id, method='delete')

    def flush_flows(self):
        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids) < 1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        for node_id in nodes_ids:
            try:
                path = "/restconf/config/opendaylight-inventory:nodes/node/" \
                       "%s/flow-node-inventory:table/0/" % node_id

                self._request(
                    method="delete", path=path, contentType='json'
                )
            except HTTPError as e:
                if e.response.status_code == 404:
                    pass
                else:
                    raise exceptions.CommandErrorException(
                        msg=self._parse_errors(e.response.json()))
            except Exception as e:
                raise e

    def _parse_errors(self, err_json):
        """ Generic message creator to format errors """

        sep = ""
        msg = ""
        for error in err_json["errors"]["error"]:
            msg = msg + sep + error["error-message"]
            sep = ". "
        return msg

    def get_flow(self, flow_id=0):
        """ HTTP GET method to request flows by id """

        return self._flow(flow_id=flow_id, method='get')

    def _flow(self, flow_id=0, method='', data=None):
        """ Generic implementation of the plugin communication with the
        remote controller through HTTP requests
        """

        allowed_methods = ["get", "put", "delete"]

        if flow_id < 1 or method not in allowed_methods:
            log.error("Invalid parameters in OLDPlugin flow handler")
            raise exceptions.ValueInvalid()

        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids) < 1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        return_flows = []
        for node_id in nodes_ids:
            path = "/restconf/config/opendaylight-inventory:nodes/node/%s/" \
                   "flow-node-inventory:table/0/flow/%s" % (node_id, flow_id)

            return_flows.append(
                self._request(
                    method=method, path=path, data=data, contentType='json'
                )
            )

        return return_flows

    def get_flows(self):
        """ Returns All flows for table 0 of all switches of a environment """

        nodes_ids = self._get_nodes_ids()
        if len(nodes_ids) < 1:
            raise exceptions.ControllerInventoryIsEmpty(msg="No nodes found")

        flows_list = {}
        for node_id in nodes_ids:
            try:
                path = "/restconf/config/opendaylight-inventory:nodes/node/" \
                       "%s/flow-node-inventory:table/0/" % (node_id)

                inventory = self._request(
                    method="get",
                    path=path,
                    contentType='json'
                )

                flows_list[node_id] = inventory["flow-node-inventory:table"]

            except HTTPError as e:
                if e.response.status_code == 404:
                    flows_list[node_id] = []
                else:
                    raise exceptions.CommandErrorException(
                        msg=self._parse_errors(e.response.json()))
            except Exception as e:
                raise e

        return flows_list

    def _get_nodes_ids(self):
        #TODO: We need to check on newer versions (later to Berylliun) if the
        # check on both config and operational is still necessary
        path1 = "/restconf/config/network-topology:network-topology/topology/flow:1/"
        path2 = "/restconf/operational/network-topology:network-topology/topology/flow:1/"
        nodes_ids={}
        try:
            topo1=self._request(method='get', path=path1, contentType='json')['topology'][0]
            if topo1.has_key('node'):
                for node in topo1['node']:
                    if node["node-id"] not in ["controller-config"]:
                        nodes_ids[node["node-id"]] = 1
        except HTTPError as e:
            if e.response.status_code!=404:
                raise e
        try:
            topo2 = self._request(method='get', path=path2, contentType='json')['topology'][0]
            if topo2.has_key('node'):
                for node in topo2['node']:
                    if node["node-id"] not in ["controller-config"]:
                        nodes_ids[node["node-id"]] = 1
        except HTTPError as e:
            if e.response.status_code!=404:
                raise e
        nodes_ids_list = nodes_ids.keys()
        nodes_ids_list.sort()
        return nodes_ids_list


    def _request(self, **kwargs):
        """ Sends request to controller """

        # Params and default values
        params = {
            'method': 'get',
            'path': '',
            'data': None,
            'contentType': 'json',
            'verify': False
        }

        # Setting params via kwargs or use the defaults
        for param in params:
            if param in kwargs:
                params[param] = kwargs.get(param)

        headers = self._get_headers(contentType=params["contentType"])
        uri = self._get_uri(path=params["path"])

        log.debug(
            "Starting %s request to controller %s at %s. Data to be sent: %s" %
            (params["method"], self.equipment.nome, uri, params["data"])
        )

        try:
            # Raises AttributeError if method is not valid
            func = getattr(requests, params["method"])
            request = func(
                uri,
                auth=self._get_auth(),
                headers=headers,
                verify=params["verify"],
                data=params["data"]
            )

            request.raise_for_status()

            try:
                return json.loads(request.text)
            except Exception as exception:
                log.error("Can't serialize as Json: %s" % exception)
                return

        except AttributeError:
            log.error('Request method must be valid HTTP request. '
                      'ie: GET, POST, PUT, DELETE')


    def _get_auth(self):
        return self._basic_auth()

    def _basic_auth(self):
        """ Create a HTTP Basic Authentication object """

        return HTTPBasicAuth(
            self.equipment_access.user,
            self.equipment_access.password
        )

    def _o_auth(self):
        pass

    def _get_headers(self, contentType):
        """ Creates HTTP headers needed by the plugin """
        types = {
            'json': 'application/yang.data+json',
            'xml':  'application/xml',
            'text': 'text/plain'
        }

        return {'content-type': types[contentType],
                'Accept': types[contentType]}

    def _get_equipment_access(self):
        """ Tries to get the equipment access """

        try:
            access = None
            try:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'https').uniqueResult()
            except ObjectDoesNotExist:
                access = EquipamentoAcesso.search(
                    None, self.equipment, 'http').uniqueResult()
            return access

        except Exception:

            log.error('Access type %s not found for equipment %s.' %
                      ('https', self.equipment.nome))
            raise exceptions.InvalidEquipmentAccessException()
