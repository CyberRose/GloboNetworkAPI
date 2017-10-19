# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from networkapi.api_asn.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


class Asn(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    name = models.CharField(
        blank=False,
        max_length=45
    )

    description = models.CharField(
        blank=True,
        null=False,
        max_length=200
    )

    def _get_asn_ip_equipment(self):
        return self.asnipequipment_set.all()

    asn_ip_equipment = property(_get_asn_ip_equipment)

    log = logging.getLogger('Asn')

    class Meta(BaseModel.Meta):
        db_table = u'asn'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get AS by id.

        :return: AS.

        :raise AsnNotFoundError: As not registered.
        :raise AsnError: Failed to search for the As.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return Asn.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'AS not found. pk {}'.format(id))
            raise exceptions.AsnNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the AS.')
            raise exceptions.AsnError(
                e, u'Failure to search the AS.')

    def create_v4(self, as_map):
        """Create ASN."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def update_v4(self, as_map):
        """Update ASN."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def delete_v4(self):
        """Delete ASN.

        :raise ASAssociatedToEquipmentError: AS cannot be deleted because it
                                             is associated to at least one
                                             equipment.
        """
        try:
            if self.asnipequipment_set.count() > 0:
                ids_ipv4_equipments = [asequipment.ipv4_equipment.
                                       equipamento.id for asequipment in
                                       self.asnipequipment_set.all()
                                       if asequipment.ipv4_equipment
                                       is not None]

                ids_ipv6_equipments = [asequipment.ipv6_equipment.
                                       equipamento_id for asequipment in
                                       self.asnipequipment_set.all()
                                       if asequipment.ipv6_equipment
                                       is not None]

                ids_equipments = list(set(ids_ipv4_equipments +
                                          ids_ipv6_equipments))

                ids_equipments = map(int, ids_equipments)
                msg = u'Cannot delete AS {} because it is associated ' \
                      u'with Equipments {}.'. \
                    format(self.id, ids_equipments)
                raise exceptions.AsnAssociatedToEquipmentError(
                    msg
                )

            super(Asn, self).delete()

        except exceptions.AsnAssociatedToEquipmentError, e:
            self.log.error(e)
            raise exceptions.AsnAssociatedToEquipmentError(e.detail)
        except Exception, e:
            self.log.error(e)
            raise exceptions.AsnErrorV4(e)

class AsnIpEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    asn = models.ForeignKey(
        'api_asn.Asn',
        db_column='id_as',
        null=False
    )

    ipv4_equipment = models.ForeignKey(
        'ip.IpEquipamento',
        db_column='id_ipv4_eqpt',
        null=True
    )

    ipv6_equipment = models.ForeignKey(
        'ip.Ipv6Equipament',
        db_column='id_ipv6_eqpt',
        null=True
    )

    log = logging.getLogger('AsnIpEquipment')

    class Meta(BaseModel.Meta):
        db_table = u'asn_ip_equipment'
        managed = True

    def create_v4(self):

        pass

    def update_v4(self):

        pass

    def delete_v4(self):

        pass