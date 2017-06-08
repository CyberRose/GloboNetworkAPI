# -*- coding: utf-8 -*-
import logging

from django.db import models

from networkapi.models.BaseModel import BaseModel


class VirtualInterface(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id')
    name = models.CharField(blank=False, max_length=45)

    log = logging.getLogger('VirtualInterface')

    class Meta(BaseModel.Meta):
        db_table = u'virtual_interface'
        managed = True

    @classmethod
    def get_by_pk(cls):
        pass

    def create_v3(self):
        pass

    def update_v3(self):
        pass

    def delete_v3(self):
        pass