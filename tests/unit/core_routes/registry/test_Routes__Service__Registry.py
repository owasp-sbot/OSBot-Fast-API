# ═══════════════════════════════════════════════════════════════════════════════
# test_Routes__Service__Registry
# Tests for service registry introspection routes
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                                           import TestCase
from fastapi                                                                                            import FastAPI
from osbot_fast_api.api.Fast_API                                                                        import Fast_API
from starlette.testclient                                                                               import TestClient
from osbot_fast_api.core_routes.registry.Routes__Service__Registry                                      import Routes__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import Fast_API__Service__Registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry                                       import fast_api__service__registry
from osbot_fast_api.services.registry.Fast_API__Service__Registry__Client__Base                         import Fast_API__Service__Registry__Client__Base
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.enums.Enum__Fast_API__Service__Registry__Client__Mode     import Enum__Fast_API__Service__Registry__Client__Mode


# ═══════════════════════════════════════════════════════════════════════════════
# Status Endpoint Tests
# ═══════════════════════════════════════════════════════════════════════════════

class test_Routes__Service__Registry__status(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registry = Fast_API__Service__Registry()
        cls.fast_api = Fast_API().add_routes(Routes__Service__Registry, registry=cls.registry)
        cls.client   = cls.fast_api.client()

    def tearDown(self):
        self.registry.clear()

    def test_setUpClass(self):
        assert type(self.registry) is Fast_API__Service__Registry
        assert type(self.fast_api) is Fast_API
        assert type(self.client  ) is TestClient
        assert self.fast_api.routes_paths(include_default=False) == ['/registry/health',
                                                                     '/registry/health/{service_name}',
                                                                     '/registry/services',
                                                                     '/registry/services/{service_name}',
                                                                     '/registry/status']

    def test__status__empty_registry(self):
        response = self.client.get('/registry/status')

        assert response.status_code == 200
        data = response.json()
        assert data['registered_count'] == 0
        assert data['stack_depth']      == 0
        assert data['services']         == []

    def test__status__with_services(self):

        self.registry.register(Fake__Cache__Client, Fast_API__Service__Registry__Client__Config())
        self.registry.register(Fake__Html__Client , Fast_API__Service__Registry__Client__Config())

        response = self.client.get('/registry/status')

        assert response.status_code == 200
        data = response.json()
        assert data['registered_count'] == 2
        assert 'Fake__Cache__Client' in data['services']
        assert 'Fake__Html__Client'  in data['services']

    def test__status__shows_stack_depth(self):
        self.registry.register(Fake__Cache__Client, Fast_API__Service__Registry__Client__Config())
        self.registry.configs__save()
        self.registry.configs__save()

        response = self.client.get('/registry/status')

        assert response.status_code == 200
        data = response.json()
        assert data['stack_depth'] == 2


    # ═══════════════════════════════════════════════════════════════════════════════
    # Services Endpoint Tests
    # ═══════════════════════════════════════════════════════════════════════════════


    def test__services__empty_registry(self):

        response = self.client.get('/registry/services')

        assert response.status_code == 200
        assert response.json()      == []

    def test__services__lists_all(self):

        self.registry.register(Fake__Cache__Client,
                               Fast_API__Service__Registry__Client__Config(
                                   mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                   base_url = 'https://cache.example.com'
                               ))
        self.registry.register(Fake__Html__Client,
                               Fast_API__Service__Registry__Client__Config(
                                   mode         = Enum__Fast_API__Service__Registry__Client__Mode.IN_MEMORY,
                                   fast_api_app = FastAPI()
                               ))

        response = self.client.get('/registry/services')

        assert response.status_code == 200
        services = response.json()
        assert len(services) == 2

        # Find cache service
        cache_svc = next(s for s in services if s['service_name'] == 'Fake__Cache__Client')
        assert cache_svc['mode']         == 'remote'
        assert cache_svc['base_url']     == 'https://cache.example.com'
        assert cache_svc['has_fast_api'] is False

        # Find html service
        html_svc = next(s for s in services if s['service_name'] == 'Fake__Html__Client')
        assert html_svc['mode']         == 'in_memory'
        assert html_svc['has_fast_api'] is True

    def test__services__hides_api_key_values(self):
        self.registry.register(Fake__Cache__Client,
                               Fast_API__Service__Registry__Client__Config(
                                   mode          = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                   base_url      = 'https://cache.example.com'                           ,
                                   api_key_name  = 'X-API-KEY'                                           ,
                                   api_key_value = 'super-secret-key-12345'
                               ))


        response = self.client.get('/registry/services')

        assert response.status_code == 200
        services = response.json()
        cache_svc = services[0]

        # Should show has_api_key but NOT the actual value
        assert cache_svc['has_api_key'] is True
        assert 'api_key_value' not in cache_svc
        assert 'super-secret' not in str(cache_svc)

    def test__service__get__specific(self):
        self.registry.register(Fake__Cache__Client,
                               Fast_API__Service__Registry__Client__Config(
                                   mode     = Enum__Fast_API__Service__Registry__Client__Mode.REMOTE,
                                   base_url = 'https://cache.example.com'
                               ))
        self.registry.register(Fake__Html__Client, Fast_API__Service__Registry__Client__Config())

        response = self.client.get('/registry/services/Fake__Cache__Client')

        assert response.status_code == 200
        data = response.json()
        assert data['service_name'] == 'Fake__Cache__Client'
        assert data['base_url']     == 'https://cache.example.com'

    def test__service__get__not_found(self):
        response = self.client.get('/registry/services/NonExistent__Client')

        assert response.status_code == 200
        assert response.json() is None


    # ═══════════════════════════════════════════════════════════════════════════════
    # Health Endpoint Tests
    # ═══════════════════════════════════════════════════════════════════════════════


    def test__health__empty_registry(self):

        response = self.client.get('/registry/health')

        assert response.status_code == 200
        data = response.json()
        assert data['total_services']  == 0
        assert data['healthy_count']   == 0
        assert data['unhealthy_count'] == 0
        assert data['services']        == []

    def test__health__all_healthy(self):

        response = self.client.get('/registry/health')

        assert response.status_code == 200
        data = response.json()
        assert 'total_services'  in data
        assert 'healthy_count'   in data
        assert 'unhealthy_count' in data
        assert 'services'        in data

    def test__health__specific_service__not_found(self):

        response = self.client.get('/registry/health/NonExistent__Client')

        assert response.status_code == 200
        data = response.json()
        assert data['service_name'] == 'NonExistent__Client'
        assert data['healthy']      is False
        assert data['mode']         == 'NOT_REGISTERED'
        assert 'not found' in data['error'].lower()


    # ═══════════════════════════════════════════════════════════════════════════════
    # Integration Tests with Global Registry
    # ═══════════════════════════════════════════════════════════════════════════════




# ═══════════════════════════════════════════════════════════════════════════════
# Fake Clients for Testing
# ═══════════════════════════════════════════════════════════════════════════════

class Fake__Cache__Client(Fast_API__Service__Registry__Client__Base):
    def health(self):
        return True


class Fake__Html__Client(Fast_API__Service__Registry__Client__Base):
    def health(self):
        return True


class Fake__Unhealthy__Client(Fast_API__Service__Registry__Client__Base):
    def health(self):
        return False


class Fake__No_Health__Client(Fast_API__Service__Registry__Client__Base):
    pass  # No health method
