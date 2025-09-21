from osbot_utils.helpers.duration.decorators.capture_duration import capture_duration
from osbot_utils.utils.Env                                    import in_github_action
from osbot_fast_api.api.Fast_API                              import Fast_API

# use these static versions of the Fast_API object on tests, so that we don't created a new Fast_API object for each test
with capture_duration() as duration:
    fast_api        = Fast_API().setup()
    fast_api_client = fast_api.client()

if in_github_action() is False:
    assert duration.seconds < 0.3       # make sure that the Fast_API object is created in less than 0.3 seconds