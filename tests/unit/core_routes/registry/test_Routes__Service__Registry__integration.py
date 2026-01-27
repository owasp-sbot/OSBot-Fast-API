from unittest                                                                                           import TestCase
from fastapi                                                                                            import FastAPI
from osbot_fast_api.api.Fast_API                                                                        import Fast_API
from osbot_fast_api.core_routes.registry.Routes__Service__Registry                                      import Routes__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry, Fast_API__Service__Registry
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode
from tests.unit.core_routes.registry.test_Routes__Service__Registry                                     import Fake__Cache__Client, Fake__Html__Client


class test_Routes__Service__Registry__integration(TestCase):

    @classmethod
    def setUpClass(cls):
        fast_api__service__registry.configs__save(clear_configs=True)

        # Register test services
        fast_api__service__registry.register(Fake__Cache__Client,
                                             Fast_API__Service__Registry__Client__Config(mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                                                                         base_url = 'https://cache.test.example.com'))
        fast_api__service__registry.register(Fake__Html__Client,
                                             Fast_API__Service__Registry__Client__Config(mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
                                                                                         fast_api_app = FastAPI() ))

        cls.app    = FastAPI()
        cls.registry = Fast_API__Service__Registry()
        cls.fast_api = Fast_API().add_routes(Routes__Service__Registry)                 # Create app using global registry (default)
        cls.client   = cls.fast_api.client()


    @classmethod
    def tearDownClass(cls):
        fast_api__service__registry.configs__restore()

    def test__uses_global_registry(self):
        response = self.client.get('/registry/status')

        assert response.status_code == 200
        data = response.json()
        assert data['registered_count'] == 2
        assert 'Fake__Cache__Client' in data['services']
        assert 'Fake__Html__Client'  in data['services']

    def test__services__from_global_registry(self):
        response = self.client.get('/registry/services')

        assert response.status_code == 200
        services = response.json()
        assert len(services) == 2