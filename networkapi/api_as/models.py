# -*- coding: utf-8 -*-
import logging

from _mysql_exceptions import OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import get_model

from networkapi.api_as.v4 import exceptions
from networkapi.models.BaseModel import BaseModel


class As(BaseModel):

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

    def _get_equipments(self):
        return self.asequipment_set.all()

    equipments = property(_get_equipments)

    log = logging.getLogger('As')

    class Meta(BaseModel.Meta):
        db_table = u'as'
        managed = True

    @classmethod
    def get_by_pk(cls, id):
        """Get AS by id.

        :return: AS.

        :raise AsNotFoundError: As not registered.
        :raise AsError: Failed to search for the As.
        :raise OperationalError: Lock wait timeout exceeded
        """
        try:
            return As.objects.get(id=id)
        except ObjectDoesNotExist, e:
            cls.log.error(u'AS not found. pk {}'.format(id))
            raise exceptions.AsNotFoundError(id)
        except OperationalError, e:
            cls.log.error(u'Lock wait timeout exceeded.')
            raise OperationalError(
                e, u'Lock wait timeout exceeded; try restarting transaction')
        except Exception, e:
            cls.log.error(u'Failure to search the AS.')
            raise exceptions.AsError(
                e, u'Failure to search the AS.')

    def create_v4(self, as_map):
        """Create AS."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def update_v4(self, as_map):
        """Update AS."""

        self.name = as_map.get('name')
        self.description = as_map.get('description')

        self.save()

    def delete_v4(self):
        """Delete AS.

        :raise ASAssociatedToEquipmentError: AS cannot be deleted because it
                                             is associated to at least one
                                             equipment.
        """
        try:

            if self.asequipment_set.count() > 0:
                ids_equipments = [asequipment.equipment_id
                                  for asequipment
                                  in self.asequipment_set.all()]

                ids_equipments = map(int, ids_equipments)
                msg = u'Cannot delete AS {} because it is associated ' \
                      u'with Equipments {}.'.\
                    format(self.id, ids_equipments)
                raise exceptions.AsAssociatedToEquipmentError(
                    msg
                )

            super(As, self).delete()

        except exceptions.AsAssociatedToEquipmentError, e:
            self.log.error(e)
            raise exceptions.AsAssociatedToEquipmentError(e.detail)
        except Exception, e:
            self.log.error(e)
            raise exceptions.AsErrorV4(e)

class AsIpEquipment(BaseModel):

    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )

    asn = models.ForeignKey(
        'api_as.As',
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

    class Meta(BaseModel.Meta):
        db_table = u'as_ip_equipment'
        managed = True

    def create_v4(self):

        pass

    def update_v4(self):

        pass

    def delete_v4(self):

        pass