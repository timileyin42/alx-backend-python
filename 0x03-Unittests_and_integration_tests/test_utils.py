#!/usr/bin/env python3


"""Module for testing utility functions"""


from unittest import TestCase, mock
from unittest.mock import patch, Mock
from utils import access_nested_map
from utils import memoize
from utils import get_json
from parameterized import parameterized


class TestAccessNestedMap(TestCase):
    """Test cases for the access_nested_map function"""
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {'b': 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, map, path, expected_output):
        """Test access_nested_map with valid inputs"""
        real_output = access_nested_map(map, path)
        self.assertEqual(real_output, expected_output)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(self, map, path, wrong_output):
        """Test access_nested_map raises KeyError for invalid paths"""
        with self.assertRaises(KeyError) as e:
            access_nested_map(map, path)
            self.assertEqual(wrong_output, e.exception)


class TestGetJson(TestCase):
    """Test cases for the get_json func"""
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        """Get_json returns the expected JSON payload"""
        res = Mock()
        res.json.return_value = test_payload
        with patch('requests.get', return_value=res):
            real_response = get_json(test_url)
            self.assertEqual(real_response, test_payload)
            res.json.assert_called_once()


class TestMemoize(TestCase):
    """Test cases for the memoize decorator"""

    def test_memoize(self):
        """Memoize caches the result of the method"""

        class TestClass:
            """Test class for memoize"""

            def a_method(self):
                """Method returns a const value"""
                return 42

            @memoize
            def a_property(self):
                """Memoized property"""
                return self.a_method()

        with patch.object(TestClass, 'a_method', return_value=42) as patched:
            tst = TestClass()
            r = tst.a_property

            self.assertEqual(r, 42)
            patched.assert_called_once()
