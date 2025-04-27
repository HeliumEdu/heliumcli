__copyright__ = "Copyright (c) 2018 Helium Edu"
__license__ = "MIT"

from unittest import mock

from heliumcli import utils
from .helpers import testcase


class TestUtilsTestCase(testcase.HeliumCLITestCase):
    def test_sort_tags(self):
        # GIVEN
        tag1 = mock.MagicMock()
        tag1.name = "1.2.2"
        tag2 = mock.MagicMock()
        tag2.name = "1.2.3"
        tag3 = mock.MagicMock()
        tag3.name = "1.2.1"
        tag4 = mock.MagicMock()
        tag4.name = "0.1.5"
        tag5 = mock.MagicMock()
        tag5.name = "text-1.2.3"

        tags = [tag1, tag2, tag3, tag4, tag5]

        # WHEN
        sorted_tags = utils.sort_tags(tags)

        # THEN
        self.assertEqual(sorted_tags, [tag4, tag3, tag1, tag2])
