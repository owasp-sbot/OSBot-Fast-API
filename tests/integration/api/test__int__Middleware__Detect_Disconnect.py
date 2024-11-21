import asyncio
import re
import pytest
import requests
from unittest                                                       import IsolatedAsyncioTestCase
from fastapi                                                        import FastAPI
from requests                                                       import ReadTimeout
from starlette.requests                                             import Request
from starlette.responses                                            import JSONResponse, StreamingResponse
from osbot_fast_api.api.middlewares.Middleware__Detect_Disconnect   import Middleware__Detect_Disconnect
from osbot_fast_api.utils.Fast_API_Server                           import Fast_API_Server
from osbot_utils.context_managers.capture_duration                  import capture_duration
from osbot_utils.testing.Stdout                                     import Stdout
from osbot_utils.utils.Threads                                      import invoke_async


class test__int__Middleware__Detect_Disconnect(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = FastAPI()
        cls.app.add_middleware(Middleware__Detect_Disconnect)

        @cls.app.get("/test")
        async def test_endpoint(request: Request):
            return JSONResponse({"is_disconnected": request.state.is_disconnected})

        @cls.app.get("/slow")
        async def slow_endpoint(request: Request):
            await asyncio.sleep(0.02)  # Simulate slow response
            return JSONResponse({"is_disconnected": request.state.is_disconnected})

        @cls.app.get("/with-streamed-response")
        def with_streamed_response(request: Request, log_data: bool = False):
            async def gen():
                for i in range(0,3):
                    data = f"item: {i} \n"
                    if log_data:
                        print(f'sending {data.strip()}')
                        #print(f'is_disconnected {request.state.is_disconnected}, {await request.is_disconnected()}')
                    yield data
                    #await asyncio.sleep(0.01)

            return StreamingResponse(gen(), media_type="text/event-stream")

        cls.fast_api_server = Fast_API_Server(app=cls.app)
        cls.fast_api_server.start()
        assert cls.fast_api_server.is_port_open() is True

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fast_api_server.stop()
        assert cls.fast_api_server.is_port_open() is False

    def test_setup(self):
        url = self.fast_api_server.url()
        assert type(self.app            )                     is FastAPI
        assert type(self.fast_api_server)                     is Fast_API_Server
        assert self.fast_api_server.app                       == self.app
        assert url.startswith('http://127.0.0.1')             is True
        assert requests.get(url + 'openapi.json').status_code == 200

        assert self.fast_api_server.requests_get('openapi.json').json().get('info') == {'title': 'FastAPI', 'version': '0.1.0'}

    def test_middleware_initialization(self):
        request = Request(scope={'type': 'http', 'state': {}, 'method': 'GET', 'path': '/' })
        assert hasattr(request.state, 'is_disconnected') is False

    def test_disconnect_message_handling(self):
        async def test_with_async():
           scope = {'type': 'http', 'state': {}}

           async def mock_app(scope, receive, send):
               message = await receive()
               assert message["type"] == "http.disconnect"

           middleware = Middleware__Detect_Disconnect(mock_app)

           async def mock_receive():
               return {"type": "http.disconnect"}

           async def mock_send(message):
               pass

           await middleware(scope, mock_receive, mock_send)
           assert scope['state']['is_disconnected'] is True

        invoke_async(test_with_async())

    def test_normal_request(self):
        with capture_duration() as duration:
            response = self.fast_api_server.requests_get("/test")
            assert response.status_code == 200
            assert response.json() == {"is_disconnected": False}
        assert duration.seconds < 0.010

    def test__http__show_request(self):
        with capture_duration() as duration:
            response = self.fast_api_server.requests_get("/slow")
            assert response.status_code == 200
            assert response.json() == {"is_disconnected": False}
        assert duration.seconds < 0.040

    def test__http__disconnect(self):                               # Simulate client disconnect by closing connection during request
        timeout        = 0.001
        port           = self.fast_api_server.port
        expected_match = f"HTTPConnectionPool(host='127.0.0.1', port={port}): Read timed out. (read timeout=0.001)"
        with pytest.raises(ReadTimeout, match=re.escape(expected_match)):
            self.fast_api_server.requests_get("/slow", timeout=timeout)

    def test__http__with_streamed_response(self):
        with Stdout() as stdout_1:
            response_1      = self.fast_api_server.requests_get("with-streamed-response", stream=True, params={'log_data': False})
            response_1_text = response_1.text

        with Stdout() as stdout_2:
            response_2 = self.fast_api_server.requests_get("with-streamed-response", stream=True, params={'log_data': True })
            lines      = []
            for line in response_2.iter_lines():
                lines.append(line)

        assert response_1.status_code == 200
        assert response_2.status_code == 200
        assert response_1_text        == 'item: 0 \nitem: 1 \nitem: 2 \n'
        assert lines                  == [b'item: 0 ', b'item: 1 ', b'item: 2 ']
        assert stdout_1.value()       == ''
        assert stdout_2.value()       == 'sending item: 0\nsending item: 1\nsending item: 2\n'

    # todo: figure out why the tests below are not working. I think it might be to do with the Fast_API_Server is setup
    #       since on live requests this works ok
    # def test__http__with_streamed_response_client_disconnect(self):
    #     with Stdout() as stdout:
    #         response = self.fast_api_server.requests_get("with-streamed-response", stream=True, params={'log_data': True })
    #
    #         lines = []
    #
    #         for line in response.iter_lines():                              # Read only the first line to simulate client reading part of the stream
    #             lines.append(line)
    #             if len(lines) == 5:
    #                 break
    #
    #         response.close()                                                # Close the response to simulate client disconnect
    #
    #         for line in response.iter_lines():                              # double check that nothing else was received
    #             lines.append(line)
    #
    #         #assert lines == [b'item: 0 ']                                   # Assert that we received only one line
    #         invoke_async(asyncio.sleep(1.5))                                # Wait for the server to process the disconnect
    #     print()
    #     print(stdout.value())
    #     #assert stdout.value() == 'sending item: 0\nsending item: 1\n'   # Confirm that the 2nd yield was not received

    # def test_with_httpx(self):
    #     async def run():
    #         import httpx
    #         async with httpx.AsyncClient() as client:
    #             response = await client.get(
    #                 self.fast_api_server.url() + "with-streamed-response",
    #                 params={'log_data': True})
    #             lines = []
    #             async for line in response.aiter_lines():
    #                 lines.append(line)
    #                 print(line)
    #                 if len(lines) == 5:
    #                     break
    #             await response.aclose()  # Close the connection to simulate disconnect
    #             await asyncio.sleep(1)   # Give server time to detect disconnect
    #
    #
    #     async_invoke_in_new_loop(run())
