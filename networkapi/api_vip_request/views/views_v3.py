# -*- coding:utf-8 -*-
import logging

from django.db.transaction import commit_on_success

from networkapi.api_rest import exceptions as api_exceptions
from networkapi.api_vip_request import exceptions, facade
from networkapi.api_vip_request.permissions import Read, Write
from networkapi.api_vip_request.serializers import VipRequestSerializer
from networkapi.util import logs_method_apiview, permission_classes_apiview
from networkapi.util.json_validate import json_validate, raise_json_validate

from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


log = logging.getLogger(__name__)


@permission_classes((IsAuthenticated, Read))
class VipRequestListView(APIView):

    def post(self, request, *args, **kwargs):
        """Method to return a vip request list
        Param vip_request: vip request
        """
        try:
            search = request.DATA

            vip_map = facade.get_vip_request_by_search(search)

            log.info(vip_map)

            # serializer_vips = VipRequestListSerializer(
            #     vip_map.get('vips_requests'),
            #     many=True
            # )

            # data = dict()
            # data['vips_requests'] = serializer_vips.data
            # data['total'] = vip_map.get('total')

            # return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)


class VipRequestDBView(APIView):

    @permission_classes_apiview((IsAuthenticated, Read))
    @logs_method_apiview
    def get(self, request, *args, **kwargs):
        """Method to return a vip request by id
        Param vip_request_id: vip request id
        """
        try:
            if not kwargs.get('vip_request_ids'):
                search = request.GET or None
                vips_requests = facade.get_vip_request_by_search(search)
                serializer_vips = VipRequestSerializer(
                    vips_requests['vips'],
                    many=True
                )
                data = {
                    'vips': serializer_vips.data,
                    'total': vips_requests['total'],
                }

            else:
                vip_request_ids = kwargs['vip_request_ids'].split(';')

                vips_requests = facade.get_vip_request(vip_request_ids)

                if vips_requests:
                    serializer_vips = VipRequestSerializer(
                        vips_requests,
                        many=True
                    )
                    data = {
                        'vips': serializer_vips.data
                    }
                else:
                    raise exceptions.VipRequestDoesNotExistException()

            return Response(data, status.HTTP_200_OK)

        except Exception, exception:
            log.error(exception)
            raise api_exceptions.NetworkAPIException(exception)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    @commit_on_success
    def post(self, request, *args, **kwargs):
        """
        Method to save a vip request
        Param request.DATA['info']: info of vip request in dict
        """

        data = request.DATA

        json_validate('networkapi/api_vip_request/specs/vip_post.json').validate(data)

        response = {}
        for vip in data['vips']:
            facade.create_vip_request(vip)

        return Response(response, status.HTTP_201_CREATED)

    @permission_classes_apiview((IsAuthenticated, Write))
    @logs_method_apiview
    @raise_json_validate
    @commit_on_success
    def put(self, request, *args, **kwargs):
        """
        Method to save a vip request
        Param request.DATA['info']: info of vip request in dict
        """
        data = request.DATA

        json_validate('networkapi/api_vip_request/specs/vip_put.json').validate(data)

        response = {}
        for vip in data['vips']:
            facade.update_vip_request(vip)

        return Response(response, status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        Method to delete
        """
        vip_request_ids = kwargs['vip_request_ids'].split(';')
        response = {}
        facade.delete_vip_request(vip_request_ids)

        return Response(response)