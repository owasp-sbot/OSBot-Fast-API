# ═══════════════════════════════════════════════════════════════════════════════
# Schema__Registry__* - Response schemas for service registry routes
# ═══════════════════════════════════════════════════════════════════════════════

from typing                              import List, Optional
from osbot_utils.type_safe.Type_Safe     import Type_Safe


class Schema__Registry__Service__Health(Type_Safe):                             # Health status for a service
    service_name : str                                                          # Service name
    healthy      : bool                                                         # Health check result
    mode         : str                                                          # Current mode
    error        : str = None                                                   # Error message if unhealthy


class Schema__Registry__Status(Type_Safe):                                      # Overall registry status
    registered_count : int                                                      # Number of registered services
    stack_depth      : int                                                      # Config stack depth (for save/restore)
    services         : List[str]                                                # List of registered service names


class Schema__Registry__Health__Summary(Type_Safe):                             # Health summary for all services
    total_services  : int                                                       # Total registered
    healthy_count   : int                                                       # Number healthy
    unhealthy_count : int                                                       # Number unhealthy
    services        : List[Schema__Registry__Service__Health]                   # Individual results