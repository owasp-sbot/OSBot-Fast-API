import os
from unittest import TestCase
from unittest.mock import patch

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import parent_folder
from osbot_utils.utils.Misc import obj_info

import osbot_fast_api
from osbot_fast_api.utils.Version import Version

EXPECTED_PACKAGES = ['osbot_fast_api'                                   ,
                     'osbot_fast_api.utils'                             ,
                     'osbot_fast_api.examples'                          ,
                     'osbot_fast_api.api'                               ,
                     'osbot_fast_api.examples.ex_1_simple'              ,
                     'osbot_fast_api.examples.ex_1_simple.static_files' ,
                     'osbot_fast_api.api.routes'                        ]

class test_setup(TestCase):


    @patch('setuptools.setup')                                                      # this prevents the sys.exit() from being called
    def test_setup(self, mock_setup):
        parent_path = parent_folder(osbot_fast_api.path)                            # get the root of the repo
        os.chdir(parent_path)                                                       # change current directory to root so that the README.me file can be resolved
        import setup                                                                # do the import
        args, kwargs = mock_setup.call_args                                         # capture the params used on the setup call

        if kwargs.get('name') == 'osbot_fast_api':                                  # make sure we imported the correct setup (submodules will imapct this)
            assert kwargs.get('description'     ) == 'OWASP Security Bot - Fast API'
            assert kwargs.get('long_description') == setup.long_description
            assert kwargs.get('version'         ) == Version().value()
            assert kwargs.get('packages'        ) == EXPECTED_PACKAGES