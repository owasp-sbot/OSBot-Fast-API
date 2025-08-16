from unittest                               import TestCase
from osbot_fast_api.api.Fast_API            import Fast_API
from osbot_fast_api.api.routes.Fast_API__Routes    import Fast_API__Routes


class test_Fast_API__Routes__with_path_params(TestCase):

    def test__get_method__with_path__params(self):

        class Param_Routes(Fast_API__Routes):
            tag = 'param'

            def an__guid(self, guid: str):
                return { 'method':'get', 'guid':guid }

            def an__guid__action(self, guid: str, action: str):
                return { 'method':'get', 'guid':guid, 'action':action }

            def an__guid_id__action(self, guid: str, action: str):
                return { 'method':'get', 'guid':guid, 'action':action }

            def an__guid__action_id(self, guid: str, action: str):
                return { 'method':'get', 'guid':guid, 'action':action }

            def an__guid_post(self, guid: str):
                return  { 'method':'post', 'guid':guid }

            def an__guid_put(self, guid: str):
                return  { 'method':'put', 'guid':guid }

            def an__guid_delete(self, guid: str):
                return  { 'method':'delete', 'guid':guid }

            def setup_routes(self):
                self.add_route_get   (self.an__guid            )       # will become '/param/an/{guid}'
                self.add_route_get   (self.an__guid_id__action )       # will become '/param/an/{guid}/id/{action}'
                self.add_route_get   (self.an__guid__action    )       # will become '/param/an/{guid}/{action}'
                self.add_route_get   (self.an__guid__action_id )       # will become '/param/an/{guid}/{action}/id'
                self.add_route_post  (self.an__guid_post       )
                self.add_route_put   (self.an__guid_put        )
                self.add_route_delete(self.an__guid_delete     )



        class An_Fast_API(Fast_API):
            default_routes = False

            def setup_routes(self):
                self.add_routes(Param_Routes)

        an_fast_api = An_Fast_API().setup()

        assert an_fast_api.routes_paths() ==[ '/param/an/{guid}'            ,
                                              '/param/an/{guid}/delete'     ,
                                              '/param/an/{guid}/id/{action}',
                                              '/param/an/{guid}/post'       ,
                                              '/param/an/{guid}/put'        ,
                                              '/param/an/{guid}/{action}'   ,
                                              '/param/an/{guid}/{action}/id']

        client = an_fast_api.client()
        assert client.get   ('/param/an/guid-1111'            ).json() == {                      'guid': 'guid-1111', 'method': 'get'   }
        assert client.delete('/param/an/guid-2222/delete'     ).json() == {                      'guid': 'guid-2222', 'method': 'delete'}
        assert client.get   ('/param/an/guid-3333/id/action-3').json() == {'action': 'action-3', 'guid': 'guid-3333', 'method': 'get'   }
        assert client.post  ('/param/an/guid-4444/post'       ).json() == {                      'guid': 'guid-4444', 'method': 'post'  }
        assert client.put   ('/param/an/guid-5555/put'        ).json() == {                      'guid': 'guid-5555', 'method': 'put'   }
        assert client.get   ('/param/an/guid-6666/action-6'   ).json() == {'action': 'action-6', 'guid': 'guid-6666', 'method': 'get'   }
        assert client.get   ('/param/an/guid-7777/action-7/id').json() == {'action': 'action-7', 'guid': 'guid-7777', 'method': 'get'   }
