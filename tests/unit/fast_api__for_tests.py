from osbot_fast_api.api.Fast_API                   import Fast_API
from osbot_utils.context_managers.capture_duration import capture_duration

# use these static versions of the Fast_API object on tests, so that we don't created a new Fast_API object for each test
with capture_duration() as duration:
    fast_api        = Fast_API().setup()
    fast_api_client = fast_api.client()


assert duration.seconds < 0.1       # make sure that the Fast_API object is created in less than 0.1 seconds