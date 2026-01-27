# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Service__Registry
# Central registry for service client configuration
# Stores configs keyed by client type - clients are stateless facades
# Supports save/restore and context managers for test isolation and hot-swapping
# ═══════════════════════════════════════════════════════════════════════════════

from contextlib                                                                                         import contextmanager
from osbot_fast_api.services.schemas.registry.Fast_API__Service__Registry__Client__Config               import Fast_API__Service__Registry__Client__Config
from osbot_fast_api.services.schemas.registry.collections.Dict__Fast_API__Service__Configs_By_Type      import Dict__Fast_API__Service__Configs_By_Type
from osbot_fast_api.services.schemas.registry.collections.List__Fast_API__Service__Configs_Stack        import List__Fast_API__Service__Configs_Stack
from osbot_utils.type_safe.Type_Safe                                                                    import Type_Safe
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                                          import type_safe


class Fast_API__Service__Registry(Type_Safe):                                   # Config store keyed by client type
    configs       : Dict__Fast_API__Service__Configs_By_Type                    # Current configs (auto-created)
    configs_stack : List__Fast_API__Service__Configs_Stack                      # Stack for save/restore (auto-created)

    # ───────────────────────────────────────────────────────────────────────────
    # Core Registry Operations
    # ───────────────────────────────────────────────────────────────────────────

    @type_safe
    def register(self                                                      ,    # Register config for a client type
                 client_type : type                                        ,
                 config      : Fast_API__Service__Registry__Client__Config
            ) -> None:
        self.configs[client_type] = config

    def config(self, client_type: type) -> Fast_API__Service__Registry__Client__Config:
        if client_type not in self.configs:                                     # Retrieve config by client type
            return None
        return self.configs[client_type]

    def is_registered(self, client_type: type) -> bool:
        return client_type in self.configs

    def clear(self) -> None:                                                    # Reset configs (not stack)
        self.configs.clear()

    # ───────────────────────────────────────────────────────────────────────────
    # Save / Restore - For setUp/tearDown patterns
    # ───────────────────────────────────────────────────────────────────────────

    def configs__save(self, clear_configs=True) -> None:                                            # Save current configs to stack
        snapshot = Dict__Fast_API__Service__Configs_By_Type()
        snapshot.update(self.configs)
        self.configs_stack.append(snapshot)
        if clear_configs:
            self.clear()
        return self


    def configs__restore(self) -> None:                                         # Restore configs from stack
        if len(self.configs_stack) > 0:
            saved = self.configs_stack.pop()
            self.configs.clear()
            self.configs.update(saved)
        return self

    def configs__stack_size(self) -> int:                                       # Check stack depth
        return len(self.configs_stack)

    # ───────────────────────────────────────────────────────────────────────────
    # Context Managers - For clean test isolation and hot-swapping
    # ───────────────────────────────────────────────────────────────────────────

    @contextmanager
    def with_registry(self, registry: 'Fast_API__Service__Registry'):           # Temporarily use another registry's configs
        self.configs__save()
        self.configs.clear()
        self.configs.update(registry.configs)
        try:
            yield self
        finally:
            self.configs__restore()

    @contextmanager
    def with_config(self, client_type: type,                                    # Temporarily override single client's config
                          config     : Fast_API__Service__Registry__Client__Config):
        self.configs__save(clear_configs=False)
        self.configs[client_type] = config
        try:
            yield self
        finally:
            self.configs__restore()


fast_api__service__registry = Fast_API__Service__Registry()                     # Singleton instance for convenience