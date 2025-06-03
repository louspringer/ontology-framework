import click

from .prompt_manager import PromptManager


@click.group()
def cli():
    """Prompt Manager"""
    pass


@cli.command()
@click.argument("name")
@click.argument("file")
@click.option("--category", help="Prompt category")
@click.option("--tags", help="Comma-separated tags")
def add(name, file, category, tags):
    """Add a new prompt"""
    pm = PromptManager()
    with open(file) as f:
        content = f.read()
    tag_list = tags.split(",") if tags else []
    pm.add_prompt(name, content, category, tag_list)
    click.echo(f"Added prompt: {name}")


@cli.command()
@click.argument("query")
def search(query):
    """Search for prompts"""
    pm = PromptManager()
    results = pm.search_prompts(query)
    for name, content, category, tags in results:
        click.echo(f"\n=== {name} ===")
        click.echo(f"Category: {category}")
        click.echo(f"Tags: {', '.join(tags) if tags else 'None'}")
        click.echo(f"\n{content}\n")
        click.echo("-" * 50)


@cli.command()
def list():
    """List all prompts"""
    pm = PromptManager()
    prompts = pm.list_prompts()
    if not prompts:
        click.echo("No prompts found")
        return

    for name, category, tags in prompts:
        click.echo(f"{name} ({category}) [{', '.join(tags) if tags else 'No tags'}]")


@cli.command()
def list_ids():
    """List all prompts with their IDs"""
    pm = PromptManager()
    prompts = pm.list_with_ids()
    for id, name, category, tags in prompts:
        click.echo(
            f"[{id}] {name} ({category}) [{', '.join(tags) if tags else 'No tags'}]",
        )


@cli.command()
@click.argument("id", type=int)
def get_raw(id):
    """Get raw prompt content by ID for piping"""
    pm = PromptManager()
    content = pm.get_by_id(id)
    if content:
        click.echo(
            content,
            nl=False,
        )  # nl=False to avoid extra newline for clean piping
    else:
        click.echo(f"No prompt found with ID {id}" err=True)


if __name__ == "__main__":
    cli()
