import logging
import ssl
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from amqpstorm import UriConnection

from amqpstorm.tests.utility import MockLoggingHandler

logging.basicConfig(level=logging.DEBUG)


class UriConnectionTests(unittest.TestCase):
    def setUp(self):
        self.logging_handler = MockLoggingHandler()
        logging.root.addHandler(self.logging_handler)

    def test_uri_default(self):
        connection = \
            UriConnection('amqp://guest:guest@localhost:5672/%2F', True)
        self.assertEqual(connection.parameters['hostname'], 'localhost')
        self.assertEqual(connection.parameters['username'], 'guest')
        self.assertEqual(connection.parameters['password'], 'guest')
        self.assertEqual(connection.parameters['virtual_host'], '/')
        self.assertEqual(connection.parameters['port'], 5672)
        self.assertEqual(connection.parameters['heartbeat'], 60)
        self.assertEqual(connection.parameters['timeout'], 30)
        self.assertFalse(connection.parameters['ssl'])
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_hostname(self):
        connection = \
            UriConnection('amqps://guest:guest@my-server:5672/%2F?'
                          'heartbeat=1337', True)
        self.assertIsInstance(connection.parameters['hostname'], str)
        self.assertEqual(connection.parameters['hostname'], 'my-server')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_username(self):
        connection = \
            UriConnection('amqps://username:guest@localhost:5672/%2F?'
                          'heartbeat=1337', True)
        self.assertIsInstance(connection.parameters['username'], str)
        self.assertEqual(connection.parameters['username'], 'username')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_password(self):
        connection = \
            UriConnection('amqps://guest:password@localhost:5672/%2F?'
                          'heartbeat=1337', True)
        self.assertIsInstance(connection.parameters['password'], str)
        self.assertEqual(connection.parameters['password'], 'password')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_port(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:1337/%2F', True)
        self.assertIsInstance(connection.parameters['port'], int)
        self.assertEqual(connection.parameters['port'], 1337)
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_heartbeat(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F?'
                          'heartbeat=1337', True)
        self.assertIsInstance(connection.parameters['heartbeat'], int)
        self.assertEqual(connection.parameters['heartbeat'], 1337)
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_timeout(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F?'
                          'timeout=1337', True)
        self.assertIsInstance(connection.parameters['timeout'], int)
        self.assertEqual(connection.parameters['timeout'], 1337)
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_virtual_host(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/travis', True)
        self.assertIsInstance(connection.parameters['virtual_host'], str)
        self.assertEqual(connection.parameters['virtual_host'], 'travis')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_set_ssl(self):
        connection = UriConnection('amqps://guest:guest@localhost:5671/%2F?'
                                   'ssl_version=protocol_tlsv1&'
                                   'cert_reqs=cert_required&'
                                   'keyfile=file.key&'
                                   'certfile=file.crt&'
                                   'ca_certs=test', True)
        self.assertTrue(connection.parameters['ssl'])
        self.assertEqual(connection.parameters['ssl_options']['ssl_version'],
                         ssl.PROTOCOL_TLSv1)
        self.assertEqual(connection.parameters['ssl_options']['cert_reqs'],
                         ssl.CERT_REQUIRED)
        self.assertEqual(connection.parameters['ssl_options']['keyfile'],
                         'file.key')
        self.assertEqual(connection.parameters['ssl_options']['certfile'],
                         'file.crt')
        self.assertEqual(connection.parameters['ssl_options']['ca_certs'],
                         'test')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_get_ssl_version(self):
        connection = \
            UriConnection('amqp://guest:guest@localhost:5672/%2F', True)
        self.assertEqual(ssl.PROTOCOL_TLSv1,
                         connection._get_ssl_version('protocol_tlsv1'))
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_get_invalid_ssl_version(self):
        connection = \
            UriConnection('amqp://guest:guest@localhost:5672/%2F', True)
        self.assertEqual(connection._get_ssl_version('protocol_test'),
                         ssl.PROTOCOL_TLSv1)
        self.assertIn("ssl_options: ssl_version 'protocol_test' not found "
                      "falling back to PROTOCOL_TLSv1.",
                      self.logging_handler.messages['warning'][0])

    def test_uri_get_ssl_validation(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F', True)
        self.assertEqual(ssl.CERT_REQUIRED,
                         connection._get_ssl_validation('cert_required'))
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_get_invalid_ssl_validation(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F', True)
        self.assertEqual(ssl.CERT_NONE,
                         connection._get_ssl_validation('cert_test'))
        self.assertIn("ssl_options: cert_reqs 'cert_test' not found "
                      "falling back to CERT_NONE.",
                      self.logging_handler.messages['warning'][0])

    def test_uri_get_ssl_options(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F', True)
        ssl_kwargs = {
            'cert_reqs': ['cert_required'],
            'ssl_version': ['protocol_tlsv1'],
            'keyfile': ['file.key'],
            'certfile': ['file.crt']
        }
        ssl_options = connection._parse_ssl_options(ssl_kwargs)
        self.assertEqual(ssl_options['cert_reqs'], ssl.CERT_REQUIRED)
        self.assertEqual(ssl_options['ssl_version'], ssl.PROTOCOL_TLSv1)
        self.assertEqual(ssl_options['keyfile'], 'file.key')
        self.assertEqual(ssl_options['certfile'], 'file.crt')
        self.assertFalse(self.logging_handler.messages['warning'])

    def test_uri_invalid_ssl_options(self):
        connection = \
            UriConnection('amqps://guest:guest@localhost:5672/%2F', True)
        ssl_kwargs = {
            'unit_test': ['not_required'],
        }
        ssl_options = connection._parse_ssl_options(ssl_kwargs)
        self.assertFalse(ssl_options)
        self.assertIn("invalid option: unit_test",
                      self.logging_handler.messages['warning'][0])


class UriConnectionExceptionTests(unittest.TestCase):
    """These tests are only so that we better understand when, and where
        UriConnection fails.
    """
    @unittest.skipIf(sys.version_info < (3, 3), 'Python 3.x test')
    def test_uri_py3_raises_on_empty(self):
        self.assertRaises(TypeError, UriConnection, '')
        self.assertRaises(TypeError, UriConnection, b'')

    @unittest.skipIf(sys.version_info < (3, 3), 'Python 3.x test')
    def test_uri_py3_raises_on_invalid_uri(self):
        self.assertRaises(ValueError, UriConnection, 'amqp://a:b')
        self.assertRaises(TypeError, UriConnection, 'amqp://a:')

    @unittest.skipIf(sys.version_info[0] == 3, 'Python 2.x test')
    def test_uri_py2_raises_on_empty(self):
        self.assertRaises(AttributeError, UriConnection, '')
        self.assertRaises(AttributeError, UriConnection, b'')

    @unittest.skipIf(sys.version_info[0] == 3, 'Python 2.x test')
    def test_uri_py2_raises_on_invalid_uri(self):
        self.assertRaises(ValueError, UriConnection, 'amqp://a:b')
        self.assertRaises((ValueError, AttributeError),
                          UriConnection, 'amqp://a:')

    def test_uri_raises_on_invalid_object(self):
        self.assertRaises(AttributeError, UriConnection, None)
        self.assertRaises(AttributeError, UriConnection, {})
        self.assertRaises(AttributeError, UriConnection, [])
        self.assertRaises(AttributeError, UriConnection, ())
