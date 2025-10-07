from typing                                                     import Optional, Dict
from osbot_fast_api.client.Client__Generator__AST               import Client__Generator__AST
from osbot_fast_api.client.Fast_API__Contract__Extractor        import Fast_API__Contract__Extractor
from osbot_fast_api.client.schemas.Schema__Service__Contract    import Schema__Service__Contract
from osbot_utils.type_safe.Type_Safe                            import Type_Safe
from osbot_fast_api.api.Fast_API                                import Fast_API


class Fast_API__Client__Generator(Type_Safe):
    fast_api : Fast_API                                                            # Fast_API instance to generate client for

    def extract_contract(self) -> Schema__Service__Contract:                       # Extract service contract from Fast_API instance

        extractor = Fast_API__Contract__Extractor(fast_api=self.fast_api)
        return extractor.extract_contract()

    def generate_client(self, client_name: Optional[str] = None                    # Optional client class name
                      ) -> Dict[str, str]:                                         # Generate client code from Fast_API instance
                                                                                   # Returns dictionary of filename -> code content
                                                                                   # Extract contract
        contract = self.extract_contract()
                                                                                   # Generate client code
        generator = Client__Generator__AST(contract    = contract    ,
                                           client_name = client_name  )

        return generator.generate_client_files()

    def save_client_files(self, output_dir   : str                 ,               # Directory to save files to
                              client_name    : Optional[str] = None                # Optional client class name
                        ):                                                         # Generate and save client files to directory

        from pathlib import Path
        import os
                                                                                   # Generate client code
        files = self.generate_client(client_name)
                                                                                   # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
                                                                                   # Save each file
        for file_path, content in files.items():
            file_full_path = output_path / file_path
                                                                                   # Create subdirectories if needed
            file_full_path.parent.mkdir(parents=True, exist_ok=True)
                                                                                   # Save file
            with open(file_full_path, 'w') as f:
                f.write(content)

        return list(files.keys())

    def print_client_summary(self):                                               # Print summary of what would be generated

        contract = self.extract_contract()

        print(f"Service: {contract.service_name} {contract.version}")
        print(f"Modules: {len(contract.modules)}")
        print(f"Total Endpoints: {len(contract.endpoints)}")
        print()

        for module in contract.modules:
            print(f"  Module '{module.module_name}':")
            print(f"    Classes: {', '.join(module.route_classes)}")
            print(f"    Endpoints: {len(module.endpoints)}")

            for endpoint in module.endpoints[:3]:                                 # Show first 3 endpoints
                print(f"      - {endpoint.method} {endpoint.path_pattern} ({endpoint.route_method})")

            if len(module.endpoints) > 3:
                print(f"      ... and {len(module.endpoints) - 3} more")
            print()


# Add method to Fast_API class
def generate_client(self, output_dir   : Optional[str] = None ,                   # Optional directory to save files
                         client_name   : Optional[str] = None                    # Optional name for the client
                   ) -> Dict[str, str]:                                           # Generate client code for this Fast_API service
                                                                                  # Args:
                                                                                  #     output_dir: Optional directory to save files to
                                                                                  #     client_name: Optional name for the client (defaults to service name)
                                                                                  # Returns:
                                                                                  #     Dictionary of filename -> code content

    generator = Fast_API__Client__Generator(fast_api=self)

    if output_dir:                                                                # Save to files and return filenames
        filenames = generator.save_client_files(output_dir, client_name)
        return {name: f"Saved to {output_dir}/{name}" for name in filenames}
    else:                                                                         # Return generated code
        return generator.generate_client(client_name)

# Monkey-patch the method onto Fast_API class
# This allows any Fast_API instance to generate a client
Fast_API.generate_client = generate_client