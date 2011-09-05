
from pyramid import testing
import logging
try:
    import unittest2 as unittest
except:
    import unittest


log = logging.getLogger(__name__)


class ExceptionsTests(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_validate_error(self):

        from aybu.controlpanel.libs.exceptions import ValidationError

        error = ValidationError()
        self.assertEqual(str(error), 'ValidationError()')

        message = 'Message'
        error = ValidationError(message)
        self.assertEqual(str(error), message)

        error = ValidationError('Message', 'Arg 1', 'Arg 2')
        self.assertEqual(str(error),
                         "ValidationError('Message', 'Arg 1', 'Arg 2')")

        args = ('Error: %s, %s', 'arg1', 'arg2')
        error = ValidationError(*args)
        self.assertEqual(str(error), args[0] % (args[1], args[2]))
