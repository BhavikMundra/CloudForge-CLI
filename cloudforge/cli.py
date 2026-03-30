"""Main CLI entry point for CloudForge."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import typer
from github import Github, GithubException
from github.Auth import Token
from rich.console import Console
from rich.panel import Panel

# Support running as either `python -m cloudforge.cli` or `python cloudforge/cli.py`.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

console = Console()

app = typer.Typer(
    name="cloudforge",
    help="CloudForge CLI",
    add_completion=False,
)
create_app = typer.Typer(help="Create cloud resources and project scaffolds.")


@create_app.command("lambda")
def create_lambda(
    github_repo_name: str = typer.Option(
        ...,
        "--github-repo-name",
        prompt="GitHub repository name",
        help="Name of the GitHub repository to create.",
    )
) -> None:
    """Prompt for a GitHub repo name, then create it on GitHub."""
    console.print(Panel(
        f"[bold]Repository name:[/bold] {github_repo_name}",
        title="Your Input",
        expand=False,
    ))

    if not typer.confirm("Create this repository on GitHub?"):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit(code=0)

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        console.print(
            "[bold red]Error:[/bold red] GITHUB_TOKEN environment variable is not set.\n"
            "Set it with: [cyan]$env:GITHUB_TOKEN = 'your_token'[/cyan]"
        )
        raise typer.Exit(code=1)

    console.print(f"Creating repository [bold]{github_repo_name}[/bold]...")

    try:
        gh = Github(auth=Token(token))
        user = gh.get_user()
        repo = user.create_repo(name=github_repo_name, private=False, auto_init=True)
        console.print(
            Panel(
                f"[bold green]Repository created successfully![/bold green]\n"
                f"[bold]URL:[/bold] {repo.html_url}",
                title="Done",
                expand=False,
            )
        )
    except GithubException as exc:
        # 401 = bad credentials, 422 = already exists / validation error
        if exc.status == 401:
            console.print("[bold red]Error:[/bold red] GitHub token is invalid or expired.")
        elif exc.status == 422:
            console.print(
                f"[bold red]Error:[/bold red] Repository [bold]{github_repo_name}[/bold] "
                "already exists or the name is invalid."
            )
        else:
            console.print(f"[bold red]GitHub API error {exc.status}:[/bold red] {exc.data.get('message', exc)}")
        raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[bold red]Unexpected error:[/bold red] {exc}")
        raise typer.Exit(code=1)


app.add_typer(create_app, name="create")


if __name__ == "__main__":
    app()
