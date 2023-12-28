from unittest import TestCase

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import file_exists, file_contents
from osbot_utils.utils.Misc import trim

from osbot_fast_api.utils.Version import Version


class test_Version(TestCase):

    def setUp(self) -> None:
        self.version = Version()

    def test_path_code_code(self):
        path_code_root = self.version.path_code_root()
        assert path_code_root.endswith('/OSBot-Fast-API/osbot_fast_api')

    def test_path_version_file(self):
        path_version_file = self.version.path_version_file()
        assert file_exists(path_version_file)

    def test_value(self):
        assert self.version.value() == trim(file_contents(self.version.path_version_file()))

