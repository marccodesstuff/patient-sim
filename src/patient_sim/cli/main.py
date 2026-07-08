from __future__ import annotations

import typer

app = typer.Typer(add_completion=False)


@app.command()
def start(scenario: str, persona: str | None = None) -> None:
    """Start a new conversation session."""
    typer.echo(f"Starting scenario={scenario}" + (f" persona={persona}" if persona else ""))


@app.command()
def turn(session_id: str, message: str) -> None:
    """Send a message in an existing session."""
    typer.echo(f"session={session_id} message={message}")


@app.command()
def replay(session_id: str) -> None:
    """Replay a session from logs."""
    typer.echo(f"Replaying session={session_id}")


def main() -> None:
    app()
