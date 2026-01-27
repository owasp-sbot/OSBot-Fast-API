# ═══════════════════════════════════════════════════════════════════════════════
# Enum__Fast_API__Service__Registry__Client__Mode
# Defines the transport mode for service clients
# ═══════════════════════════════════════════════════════════════════════════════

from enum                                                                       import Enum


class Enum__Fast_API__Service__Registry__Client__Mode(Enum):
    IN_MEMORY = 'in_memory'                                                     # Uses FastAPI TestClient (no network)
    REMOTE    = 'remote'                                                        # Uses HTTP requests library
