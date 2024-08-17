#!/usr/bin/env python3


"""Module for testing the GithubOrgClient utility"""


import unittest
from unittest.mock import patch, Mock, PropertyMock, call
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD
from requests import HTTPError


class TestGithubOrgClient(unittest.TestCase):
    """GithubOrgClient class test cases"""

    @parameterized.expand([
        ("google", {"google": True}),
        ("abc", {"abc": True})
    ])
    @patch('client.get_json')
    def test_org(self, org, expected, get_patch):
        """Test GithubOrgClient.org returns the expected result"""
        get_patch.return_value = expected
        gcl = GithubOrgClient(org)
        self.assertEqual(gcl.org, expected)
        get_patch.assert_called_once_with("https://api.github.com/orgs/" + org)

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url returns the correct URL"""
        correct = "www.yes.com"
        payload = {"repos_url": correct}
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock, return_value=payload):
            client = GithubOrgClient("test_org")
            self.assertEqual(client._public_repos_url, correct)

    @patch('client.get_json')
    def test_public_repos(self, get_json_mock):
        """Test GithubOrgClient.public_repos"""
        repos = [
            {"name": "Jeff", "license": {"key": "a"}},
            {"name": "Bobb", "license": {"key": "b"}},
            {"name": "Suee"}
        ]
        get_json_mock.return_value = repos
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock, return_value="www.yes.com"):
            client = GithubOrgClient("test_org")
            self.assertEqual(client.public_repos(), ['Jeff', 'Bobb', 'Suee'])
            self.assertEqual(client.public_repos("a"), ['Jeff'])
            self.assertEqual(client.public_repos("c"), [])
            self.assertEqual(client.public_repos(45), [])
            get_json_mock.assert_called_once_with("www.yes.com")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license correctly checks for licenses"""
        self.assertEqual(GithubOrgClient.has_license(
            repo, license_key), expected)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test cases for the GithubOrgClient class"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level mocks for the integration tests"""
        route_payload = {
            'https://api.github.com/orgs/google': cls.org_payload,
            'https://api.github.com/orgs/google/repos': cls.repos_payload,
        }

        def get_payload(url):
            if url in route_payload:
                return Mock(**{'json.return_value': route_payload[url]})
            return HTTPError

        cls.get_patcher = patch("requests.get", side_effect=get_payload)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level mocks after the integration tests"""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """GithubOrgClient.public_repos method with integration setup"""
        self.assertEqual(
            GithubOrgClient("google").public_repos(),
            self.expected_repos,
        )

    def test_public_repos_with_license(self) -> None:
        """GithubOrgClient.public_repos method with license filtering"""
        self.assertEqual(
            GithubOrgClient("google").public_repos(license="apache-2.0"),
            self.apache2_repos,
        )
