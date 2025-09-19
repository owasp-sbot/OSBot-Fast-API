from osbot_utils.type_safe.Type_Safe                                                import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.Random_Guid               import Random_Guid
from osbot_utils.type_safe.primitives.domains.identifiers.Safe_Id                   import Safe_Id
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now    import Timestamp_Now
from osbot_utils.utils.Env                                                          import get_env

ENV_NAME__FAST_API__SERVER_ID   = 'FAST_API__SERVER_ID'
ENV_NAME__FAST_API__SERVER_NAME = 'FAST_API__SERVER_NAME'

# use this class to capture server info
class Fast_API__Server_Info(Type_Safe):
    server_id         : Random_Guid  = get_env(ENV_NAME__FAST_API__SERVER_ID  )
    server_name       : Safe_Id      = get_env(ENV_NAME__FAST_API__SERVER_NAME)
    server_instance_id: Random_Guid
    server_boot_time  : Timestamp_Now


fast_api__server_info = Fast_API__Server_Info()