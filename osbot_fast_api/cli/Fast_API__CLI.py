import code
import os
import signal
import subprocess
import typer
import readline

from typer import Typer

from osbot_fast_api.api.Fast_API import Fast_API
from osbot_fast_api.utils.Fast_API_Server import Fast_API_Server
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Objects import obj_data


class Fast_API__CLI(Type_Safe):
    app             : Typer           = None
    fast_api        : Fast_API        = None
    fast_api_server : Fast_API_Server = None

    def __init__(self):
        super().__init__()
        self.app = Typer(add_completion=False)
        self.fast_api        = self.fast_api        or Fast_API().setup()
        self.fast_api_server = self.fast_api_server or Fast_API_Server(app=self.fast_api.app())

    def setup(self):
        self.setup_commands()
        return self

    def setup_commands(self):
        self.app.command()(self.start )
        self.app.command()(self.stop  )
        self.app.command()(self.python)

    def registered_commands_names(self):
        commands_names = []
        for command in self.app.registered_commands:
            name = command.name or command.callback.__name__
            commands_names.append(name)
        return commands_names

    def command_completions(self, text='', line=''):
        """Return possible completions for a given command."""
        commands = []
        for command in self.app.registered_commands:
            name = command.name or command.callback.__name__
            commands.append(name)
        if not text and not line.strip():                                    # If the line is empty, suggest commands
            return commands
        else:
            return [cmd for cmd in commands if cmd.startswith(text)]

    def completer(self, text, state):
        """Tab completer function."""
        line        = readline.get_line_buffer()
        completions = self.command_completions(text, line)
        if state < len(completions):
            return completions[state]
        else:
            return None

    def repl(self):
        if 'libedit' in readline.__doc__:
            readline.parse_and_bind("bind ^I rl_complete")      # for OSx
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.completer)
        self.on_repl_start()
        while True:
            try:
                command = input(">>> ").strip()
                if command.lower() in ("exit", "quit"):
                    break
                if command:  # Avoid executing empty commands
                    self.app(command.split(), standalone_mode=False)
            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                typer.echo(f"Error: {e}")
        self.stop()

    def run(self):
        typer.echo("FastAPI CLI REPL. Type 'exit' or 'quit' to leave.")
        self.repl()

    def on_repl_start(self):            # for overloading
        self.app(["--help"], standalone_mode=False)
        self.app(["start" ], standalone_mode=False)
        #self.app(["python"], standalone_mode=False)

    # typer commands

    def python(self):
        """Start a Python REPL."""
        typer.echo("##############################################################################")
        typer.echo("Starting python shell - Important: use Ctrl+D to exit (not the exit() command)")
        typer.echo("##############################################################################")
        local_vars = {"self": self}

        typer.echo("Starting Python REPL. Type 'exit()' to leave.")
        import rlcompleter
        readline.parse_and_bind("tab: complete")
        code.interact(local=local_vars)
        #self.repl()

    def start(self):
        """Start the FastAPI server using fastapi-cli."""
        if self.fast_api_server.running is False:
            self.fast_api_server.start()
            typer.echo("Server started.")
            #typer.echo(f"   > port open : {self.fast_api_server.is_port_open()} : port: {self.fast_api_server.port} - {self.fast_api_server.url()}")
        else:
            typer.echo("Server is already running.")

    def stop(self):
        """Stop the FastAPI server."""
        if self.fast_api_server.running is True:
            self.fast_api_server.stop()
            typer.echo("Server stopped.")
        else:
            typer.echo("Server is not running.")

if __name__ == "__main__":
    cli = Fast_API__CLI().setup()
    cli.run()
