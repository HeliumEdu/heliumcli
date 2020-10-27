from unittest import mock

from heliumcli import utils
from .helpers import testcase

__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Helium Edu"
__version__ = "1.6.0"


class TestUtilsTestCase(testcase.HeliumCLITestCase):
    def test_sort_tags(self):
        # GIVEN
        tag1 = mock.MagicMock()
        tag1.tag = mock.MagicMock()
        tag1.tag.tag = "1.2.2"
        tag2 = mock.MagicMock()
        tag2.tag = mock.MagicMock()
        tag2.tag.tag = "1.2.3"
        tag3 = mock.MagicMock()
        tag3.tag = mock.MagicMock()
        tag3.tag.tag = "1.2.1"
        tag4 = mock.MagicMock()
        tag4.tag = mock.MagicMock()
        tag4.tag.tag = "0.1.5"
        tag5 = mock.MagicMock()
        tag5.tag = mock.MagicMock()
        tag5.tag.tag = "text-1.2.3"

        tags = [tag1, tag2, tag3, tag4, tag5]

        # WHEN
        sorted_tags = utils.sort_tags(tags)

        # THEN
        self.assertEqual(sorted_tags, [tag4, tag3, tag1, tag2])
