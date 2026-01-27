# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry__Client__Base
# Abstract base class that all service clients must inherit
# Provides the contract for registration with Fast_API__Service__Registry
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe


class Fast_API__Service__Registry__Client__Base(Type_Safe):                     # Base class for all service clients
    pass                                                                        # Marker class - domain clients extend this
