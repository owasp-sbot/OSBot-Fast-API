#!/usr/bin/env python3
import sys
from os.path import abspath, join
sys.path.append(abspath(join(__file__, '../../../../')))     # so that we can resolve osbot_fast_api

import uvicorn
from osbot_utils.utils.Files import path_combine
from Fast_API__With_API_Key  import Fast_API__With_API_Key

app = Fast_API__With_API_Key().app()

if __name__ == "__main__":
    port = 11111
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=True)
