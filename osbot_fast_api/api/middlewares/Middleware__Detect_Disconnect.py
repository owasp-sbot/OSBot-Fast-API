from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from starlette.types import ASGIApp, Receive, Scope, Send

class Middleware__Detect_Disconnect:
    def __init__(self, app: 'ASGIApp'):
        self.app = app

    async def __call__(self, scope: 'Scope', receive: 'Receive', send: 'Send'):
        async def disconnect_monitor_receive():
            message = await receive()
            if message["type"] == "http.disconnect":
                scope.get('state')['is_disconnected'] = True
            return message

        scope.get('state')['is_disconnected'] = False
        await self.app(scope, disconnect_monitor_receive, send)



# other experiments that worked but were not as cleaned as this middleware
#    the problem I was solving was how to detect when a client disconnects from the server and prevent yield inside a
#    StreamingResponse(gen, media_type="text/event-stream") generator

# async def dispatch(self, request: Request, call_next):
    #     print('***** in DisconnectMiddleware')
    #     # Add a flag to scope for tracking disconnects
    #     request.scope.get('state')['disconnect_flag'] = False
    #
    #     async def detect_disconnect() -> dict:
    #         while True:
    #             message = await request.receive()
    #             if message["type"] == "http.disconnect":
    #                 request.scope.get('state')['disconnect_flag']  = True
    #                 break
    #             return message
    #
    #     # Wrap the original receive to handle disconnects
    #     # receive = request.scope["receive"]
    #     # request.scope["receive"] = wrapped_receive
    #     # current_thread = threading.current_thread()
    #     # asyncio.run_coroutine_threadsafe(detect_disconnect(), current_thread.loop)
    #     # Call the next middleware or route handler
    #     response = await call_next(request)
    #     return response


# disconnected = False
        # async def check_disconnected():
        #     nonlocal disconnected
        #     print("----> check_disconnected")
        #     message = await request._receive()
        #     print(message)
        #     disconnected = True
        #
        # current_thread = threading.current_thread()
        # pprint(current_thread)
        # asyncio.run_coroutine_threadsafe(check_disconnected(), current_thread.loop)
        #
        # yield '{"its": "42"}'
        #
        # return
        #current_thread = threading.current_thread()

# future = Future()
                    # context = contextvars.copy_context()
                    # func    = my_task_function
                    # args = ("value1", "value2", request, current_thread.loop)
                    #
                    # cancel_scope = None
                    # task = (context, func, args, future, cancel_scope)
                    # current_thread.queue.put(task)

# def my_task_function(param1, param2, request, loop):
        #     print(f"Running my task with: {param1}, {param2}, {current_thread == threading.current_thread()}")
        #
        #     async def check_disconnected():
        #         print("----> check_disconnected")
        #         message = await request._receive()
        #         print(message)
        #         return 'here'
        #         #return await request.is_disconnected()
            #
            # # asyncio.set_event_loop(loop)
            # print("----> Running check_disconnected")
            # #is_disconnected = loop.run_until_complete(request.is_disconnected())
            # is_disconnected = anyio.from_thread.run_sync(request.is_disconnected())
            #future = asyncio.run_coroutine_threadsafe(check_disconnected(), loop)

            #print(f"Request disconnected: {future}")
            # try:
            #     is_disconnected = future.result()  # This blocks until the coroutine completes
            #     print(f"Request disconnected: {is_disconnected}")
            # except Exception as e:
            #     print(f"Error while checking disconnection: {e}")

        # async def check_disconnected():
        #     print("----> check_disconnected")
        #     message = await request._receive()
        #     print(message)
        #
        #
        # asyncio.run_coroutine_threadsafe(check_disconnected(), current_thread.loop)


# def monitor_request_state(request):
#     print(f'>>> starting monitor_request_state: {request}')
#     max = 10
#     while max > 0:
#         print(f'>>> {max} - {request._is_disconnected} {request._stream_consumed}')
#         max -= 1
#         time.sleep(1)
# # Create a new event loop for this thread
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
#
# while True:
#     # Use the event loop to call the async `is_disconnected` method
#     is_disconnected = loop.run_until_complete(check_disconnected_async())
#     if is_disconnected:
#         print("Client disconnected!")
#         break
#     print("Client still connected...")
#     time.sleep(1)  # Adjust the interval as needed

# Start the monitoring in a separate thread
# thread = threading.Thread(target=monitor_request_state, args=(request,))
# thread.start()