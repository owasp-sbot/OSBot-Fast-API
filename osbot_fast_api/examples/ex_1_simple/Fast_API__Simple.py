from osbot_utils.utils.Files import path_combine

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.examples     import ex_1_simple

EX_1__FOLDER_NAME__STATIC_FOLDER = 'static_files'

class Fast_API__Simple(Fast_API):

    def __init__(self):
        super().__init__()
        self.fast_api_setup()

    def path_static_folder(self):
        return path_combine(ex_1_simple.path, EX_1__FOLDER_NAME__STATIC_FOLDER)