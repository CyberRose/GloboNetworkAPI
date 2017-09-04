# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import FieldError
from django.db.transaction import commit_on_success
from networkapi.plugins.factory import PluginFactory
from networkapi.infrastructure.ipaddr import IPAddress

from networkapi.api_vrf.models import Vrf
from networkapi.api_as.models import As
from networkapi.api_virtual_interface.models import VirtualInterface
from networkapi.api_virtual_interface.v4.serializers import \
    VirtualInterfaceV4Serializer
from networkapi.api_neighbor.models import Neighbor
from networkapi.api_neighbor.v4 import exceptions
from networkapi.api_neighbor.v4.exceptions import NeighborErrorV4
from networkapi.api_neighbor.v4.exceptions import NeighborNotFoundError
from networkapi.api_neighbor.v4.exceptions import NeighborError
from networkapi.api_neighbor.v4.exceptions import NeighborAlreadyCreated
from networkapi.api_neighbor.v4.exceptions import NeighborNotCreated
from networkapi.api_rest.exceptions import NetworkAPIException
from networkapi.api_rest.exceptions import ObjectDoesNotExistException
from networkapi.api_rest.exceptions import ValidationAPIException
from networkapi.api_as.v4.serializers import AsV4Serializer
from networkapi.api_vrf.serializers import VrfV3Serializer

from networkapi.infrastructure.datatable import build_query_to_datatable_v3
from networkapi.equipamento.models import Equipamento

log = logging.getLogger(__name__)

def get_neighbor_by_search(search=dict()):
    """Return a list of Neighbor's by dict."""

    try:
        neighbors = Neighbor.objects.filter()
        neighbor_map = build_query_to_datatable_v3(neighbors, search)
    except FieldError as e:
        raise ValidationAPIException(str(e))
    except Exception as e:
        raise NetworkAPIException(str(e))
    else:
        return neighbor_map


def get_neighbor_by_id(neighbor_id):
    """Return an Neighbor by id.

    Args:
        neighbor_id: Id of Neighbor
    """

    try:
        neighbor = Neighbor.get_by_pk(id=neighbor_id)
    except NeighborNotFoundError, e:
        raise exceptions.NeighborDoesNotExistException(str(e))

    return neighbor


def get_neighbor_by_ids(neighbor_ids):
    """Return Neighbor list by ids.

    Args:
        neighbor_ids: List of Ids of Neighbors.
    """

    ids = list()
    for neighbor_id in neighbor_ids:
        try:
            neighbor = get_neighbor_by_id(neighbor_id).id
            ids.append(neighbor)
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))

    neighbors = Neighbor.objects.filter(id__in=ids)

    return neighbors


def update_neighbor(neighbor):
    """Update Neighbor."""

    try:
        neighbor_obj = get_neighbor_by_id(neighbor.get('id'))
        neighbor_obj.update_v4(neighbor)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except exceptions.NeighborDoesNotExistException, e:
        raise ObjectDoesNotExistException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return neighbor_obj


def create_neighbor(neighbor):
    """Create Neighbor."""

    try:
        neighbor_obj = Neighbor()
        neighbor_obj.create_v4(neighbor)
    except NeighborErrorV4, e:
        raise ValidationAPIException(str(e))
    except ValidationAPIException, e:
        raise ValidationAPIException(str(e))
    except Exception, e:
        raise NetworkAPIException(str(e))

    return neighbor_obj


def delete_neighbor(neighbor_ids):
    """Delete Neighbor."""

    for neighbor_id in neighbor_ids:
        try:
            neighbor_obj = get_neighbor_by_id(neighbor_id)
            neighbor_obj.delete_v4()
        except exceptions.NeighborDoesNotExistException, e:
            raise ObjectDoesNotExistException(str(e))
        except NeighborError, e:
            raise NetworkAPIException(str(e))
        except Exception, e:
            raise NetworkAPIException(str(e))


def get_equipment(id_, remote_ip):

    version_ip = IPAddress(remote_ip).version

    if version_ip == 4:
        return Equipamento.objects.get(
            ipequipamento__virtual_interface__neighbor=id_)
    else:
        return Equipamento.objects.get(
            ipv6equipament__virtual_interface__neighbor=id_)


@commit_on_success
def deploy_neighbors(neighbors):

    deployed_ids = list()
    for neighbor in neighbors:
        id_ = neighbor['id']

        if neighbor['created'] is True:
            raise NeighborAlreadyCreated(id_)

        remote_ip = neighbor['remote_ip']
        try:

            equipment = get_equipment(id_, remote_ip)

            plugin = PluginFactory.factory(equipment)

            asn = As.objects.get(asequipment__equipment=equipment.id)
            vrf = Vrf.objects.get(virtualinterface__id=
                                     neighbor['virtual_interface'])
            virtual_interface = VirtualInterface.get_by_pk(
                neighbor['virtual_interface'])

            asn = AsV4Serializer(asn).data
            vrf = VrfV3Serializer(vrf).data
            virtual_interface = VirtualInterfaceV4Serializer(
                virtual_interface).data

            plugin.bgp(neighbor, virtual_interface, asn, vrf).deploy_neighbor()

        except Exception as e:
            raise NetworkAPIException(e.message)

        deployed_ids.append(id_)

    neighbors_obj = Neighbor.objects.filter(id__in=deployed_ids)
    neighbors_obj.update(created=True)


@commit_on_success
def undeploy_neighbors(neighbors):

    undeployed_ids = list()
    for neighbor in neighbors:
        id_ = neighbor['id']

        if neighbor['created'] is False:
            raise NeighborNotCreated(id_)

        remote_ip = neighbor['remote_ip']
        try:

            equipment = get_equipment(id_, remote_ip)

            plugin = PluginFactory.factory(equipment)

            asn = As.objects.get(asequipment__equipment=equipment.id)
            vrf = Vrf.objects.get(virtualinterface__id=
                                     neighbor['virtual_interface'])
            virtual_interface = VirtualInterface.get_by_pk(
                neighbor['virtual_interface'])

            asn = AsV4Serializer(asn).data
            vrf = VrfV3Serializer(vrf).data
            virtual_interface = VirtualInterfaceV4Serializer(
                virtual_interface).data

            plugin.bgp(neighbor, virtual_interface, asn, vrf).\
                undeploy_neighbor()

        except Exception as e:
            raise NetworkAPIException(e.message)

        undeployed_ids.append(id_)

    neighbors_obj = Neighbor.objects.filter(id__in=undeployed_ids)
    neighbors_obj.update(created=False)
