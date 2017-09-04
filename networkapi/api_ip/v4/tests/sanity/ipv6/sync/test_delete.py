# -*- coding: utf-8 -*-
import logging

from django.test.client import Client

from networkapi.test.test_case import NetworkApiTestCase

log = logging.getLogger(__name__)


class IPv6DeleteTestCase(NetworkApiTestCase):

    fixtures = [
        'networkapi/system/fixtures/initial_variables.json',
        'networkapi/api_pools/fixtures/initial_optionspool.json',
        'networkapi/requisicaovips/fixtures/initial_optionsvip.json',
        'networkapi/healthcheckexpect/fixtures/initial_healthcheck.json',
        'networkapi/usuario/fixtures/initial_usuario.json',
        'networkapi/grupo/fixtures/initial_ugrupo.json',
        'networkapi/usuario/fixtures/initial_usuariogrupo.json',
        'networkapi/api_ogp/fixtures/initial_objecttype.json',
        'networkapi/api_ogp/fixtures/initial_objectgrouppermissiongeneral.json',
        'networkapi/grupo/fixtures/initial_permissions.json',
        'networkapi/grupo/fixtures/initial_permissoes_administrativas.json',
        'networkapi/api_ip/v4/fixtures/initial_base.json',
        'networkapi/api_ip/v4/fixtures/initial_base_v6.json',
        'networkapi/api_ip/v4/fixtures/initial_pool.json',
        'networkapi/api_ip/v4/fixtures/initial_vip_request_v6.json',
    ]

    def setUp(self):
        self.client = Client()
        self.authorization = self.get_http_authorization('test')

    def tearDown(self):
        pass

    def test_try_delete_existent_ipv6(self):
        """V4 Tests if NAPI can delete a existent IPv6 Address."""

        response = self.client.delete(
            '/api/v4/ipv6/1/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v4/ipv6/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1.',
            response.data['detail']
        )

    def test_try_delete_non_existent_ipv6(self):
        """V4 Tests if NAPI returns error on deleting
        a not existing IPv6 Addresses.
        """

        response = self.client.delete(
            '/api/v4/ipv6/1000/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1000.',
            response.data['detail']
        )

    def test_try_delete_two_non_existent_ipv6(self):
        """V4 Tests if NAPI returns error on deleting
        two not existing IPv6 Addresses.
        """

        response = self.client.delete(
            '/api/v4/ipv6/1000;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1000.',
            response.data['detail']
        )

    def test_try_delete_one_existent_and_non_existent_ipv6(self):
        """V4 Tests if NAPI deny delete at same time an existent
        and a not existent IPv6 Address.
        """

        response = self.client.delete(
            '/api/v4/ipv6/1;1001/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1001.',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v4/ipv6/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

    def test_try_delete_ipv6_assoc_to_equipment(self):
        """V4 Tests if NAPI can delete an IPv6 Address associated
        to some equipment.
        """

        response = self.client.delete(
            '/api/v4/ipv6/2/',
            HTTP_AUTHORIZATION=self.authorization
        )
        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/ipv6/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 2.',
            response.data['detail']
        )

    def test_try_delete_two_existent_ipv6(self):
        """V4 Tests of NAPI can delete at same time
        two existent IPv6 Addresses.
        """

        response = self.client.delete(
            '/api/v4/ipv6/1;2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v4/ipv6/1;2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 1.',
            response.data['detail']
        )

    def test_try_delete_ipv6_used_by_not_created_vip_request(self):
        """V4 Tests if NAPI can delete an IPv6 Address used
        in a not deployed VIP Request.
        """

        response = self.client.delete(
            '/api/v4/ipv6/4/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        # Does get request
        response = self.client.get(
            '/api/v4/ipv6/4/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Dont there is a IP by pk = 4.',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v3/vip-request/1/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            u'Vip Request Does Not Exist.',
            response.data['detail']
        )

    def test_try_delete_ipv6_used_by_created_vip_request(self):
        """V4 Tests if NAPI deny deleting of IPv6 Address used
        in deployed VIP Request.
        """

        response = self.client.delete(
            '/api/v4/ipv6/5/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)

        self.compare_values(
            u'IPv6 can not be removed because it is in use by Vip Request 2',
            response.data['detail']
        )

        # Does get request
        response = self.client.get(
            '/api/v3/vip-request/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(200, response.status_code)

    def test_delete_one_ipv6_with_equipment_and_virtual_interface_none(self):
        """V4 Test of success to delete ipv6 with equipment and virtual
            interface none.
        """

        response = self.client.delete(
            '/api/v4/ipv6/2/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(200, response.status_code)

        response = self.client.get(
            '/api/v4/ipv6/2/',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.authorization)

        self.compare_status(404, response.status_code)

        self.compare_values(
            'Dont there is a IP by pk = 2.',
            response.data['detail'])

    def test_delete_one_ipv6_with_equipment_and_virtual_interface_not_none(self):
        """V4 Test of error to delete ipv6 with equipment and virtual
            interface not none.
        """

        response = self.client.delete(
            '/api/v4/ipv6/6/',
            HTTP_AUTHORIZATION=self.authorization
        )

        self.compare_status(400, response.status_code)

        self.compare_values(
            'Error edit IP.: Causa: Cannot delete IpEquipment relationship '
            'because Virtual Interface 1 is related with Equipment 1 '
            'and Ipv6 6., Mensagem: None',
            response.data['detail']
        )
