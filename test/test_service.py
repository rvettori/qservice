import unittest
from qservice import service


class TestService(unittest.TestCase):

    def setUp(self):
        ...

    def test_default_return(self):
        """Should return structured namespace"""

        @service()
        def myservice():
            return 'ok'

        with self.subTest(): self.assertEqual(myservice().value, 'ok', 'value should be ok')
        with self.subTest(): self.assertTrue(hasattr(myservice(), 'ok'), 'should exists ok attribute')
        with self.subTest(): self.assertTrue(hasattr(myservice(), 'value'), 'should exists value attribute')
        with self.subTest(): self.assertTrue(hasattr(myservice(), 'errors'), 'should exists errors attribute')
        with self.subTest(): self.assertTrue(hasattr(myservice(), 'messages'), 'should exists messages attribute')
        with self.subTest(): self.assertTrue(callable(myservice().json), 'should exists json callable')
        with self.subTest(): self.assertTrue(callable(myservice().dict), 'should exists dict callable')


    def test_messages(self):
        """Should return messages in returned object"""

        @service()
        def myservice(fn):
            fn.add_message('the field message')
            return 'ok'

        with self.subTest(): self.assertEqual(myservice().value, 'ok', 'value should be ok')
        with self.subTest(): self.assertEqual(len(myservice().messages), 1, 'should exist one message')
        with self.subTest(): self.assertEqual(myservice().messages[0], 'the field message', 'should exist message')

    def test_errors(self):
        """Should return messages in returned object"""

        @service()
        def myservice(fn):
            fn.add_error('field','the field error')
            return 'ok'

        with self.subTest(): self.assertFalse(myservice().ok, 'ok should be false')
        with self.subTest(): self.assertEqual(myservice().value, 'ok', 'value should be ok')
        with self.subTest(): self.assertEqual(len(myservice().errors), 1, 'should exist one error')
        with self.subTest(): self.assertEqual(myservice().errors['field'], 'the field error', 'should exist error')


        @service()
        def myservice2(fn):
            fn.add_error('field','the field error')
            fn.add_error('field2','the field2 error')
            fn.validate()
            return 'ok'

        with self.subTest(): self.assertFalse(myservice2().ok, 'ok should be false')
        with self.subTest(): self.assertEqual(myservice2().value, None, 'value should be ok')
        with self.subTest(): self.assertEqual(len(myservice2().errors), 2, 'should exist two message')
        with self.subTest(): self.assertEqual(myservice2().errors['field'], 'the field error', 'should exist error')


        @service()
        def myservice3(fn):
            fn.add_error('field','the field error', True)
            fn.add_error('field2','the field2 error', True)
            return 'ok'

        with self.subTest(): self.assertFalse(myservice3().ok, 'ok should be false')
        with self.subTest(): self.assertEqual(myservice3().value, None, 'value should be ok')
        with self.subTest(): self.assertEqual(len(myservice3().errors), 1, 'should exist one message')
        with self.subTest(): self.assertEqual(myservice3().errors['field'], 'the field error', 'should exist error')

    def test_return_dict(self):
        """Should return messages in returned object"""

        @service()
        def myservice():
            return 'ok'

        _dict = myservice().dict
        with self.subTest(): self.assertTrue(callable(_dict), 'should be a method')
        with self.subTest(): self.assertTrue(_dict().get('ok'), 'should exists ok key')
        with self.subTest(): self.assertTrue(_dict().get('value'), 'should exists value key')
        with self.subTest(): self.assertTrue(_dict().get('errors')=={}, 'should exists errors key')
        with self.subTest(): self.assertTrue(_dict().get('messages')==[], 'should exists messages key')

    def test_return_json(self):
        """Should return messages in returned object"""

        @service()
        def myservice():
            return 'ok'

        _json = myservice().json
        with self.subTest(): self.assertTrue(callable(_json), 'should be a method')
        with self.subTest(): self.assertEqual(_json(), '{"ok": true, "errors": {}, "messages": [], "value": "ok"}', 'should exists ok key')

    def test_exception(self):

        @service()
        def myservice():
            x= 1/0
            return 'ok'

        with self.subTest(): self.assertEqual(myservice().value, None, 'value should be None')
        with self.subTest(): self.assertEqual(myservice().ok, False, 'value should be Flase')
        with self.subTest(): self.assertEqual(len(myservice().errors), 1, 'should exists errors attribute')
        with self.subTest(): self.assertEqual(myservice().errors['exception'], 'division by zero' , 'should exists errors attribute')

        @service(raise_exceptions=True)
        def myservice():
            x= 1/0
            return 'ok'

        with self.subTest(): self.assertRaises(Exception, myservice, 'should rise exception')


    def test_arguments_function(self):

        @service()
        def myservice(name, fn, **kwargs):
            return name

        self.assertEqual(myservice(name='myname').value, 'myname', 'value should be myname')




    def test_context_name(self):
        self.skipTest('TODO: test number')

