import click
import questionary

from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt
from tinydb import Query

from .config import *
from .model import *
from .time import *

@click.group()
def cli():
    pass

@cli.command()
@click.argument('title', type=click.STRING, nargs=-1)
@click.option('--tag', type=click.STRING, help='Comma-separated list of tags')
@click.option('--time', type=click.STRING, help='Datetime in ISO format (defaults to now)')
def add(title, tag, time):
    """Add a new item with TITLE, optional TAGS, and optional DATETIME."""
    timestamp = (parse_flexible_datetime(time) or datetime.now()).timestamp()

    if title:
        title_str = ' '.join(title)
    else:
        title_str = questionary.text('Title').ask()

    if not tag:
        tag = questionary.text('Tag (comma-separated)').ask().strip()
        tag = tag if len(tag) > 0 else None

    tag_list = [t.strip() for t in tag.split(',')] if tag else None

    item = Record(title=title_str, tags=tag_list, timestamp=timestamp)
    item.save()
    click.echo(f"Added: {item.title} with tags: {item.tags}")

@cli.command()
@click.option('--from', 'from_dt', default=None, help='Start datetime in ISO format (inclusive, defaults to 7 days ago)')
@click.option('--to', 'to_dt', default=None, help='End datetime in ISO format (inclusive, defaults to now)')
def list(from_dt, to_dt):
    """List all records from latest to past, optionally within a time range."""

    now = datetime.now()

    if from_dt:
        from_time = parse_flexible_datetime(from_dt)
        assert from_time is not None, f'{from_dt} is invalid'
    else:
        from_time = now - timedelta(days=7)

    if to_dt:
        to_time = parse_flexible_datetime(to_dt)
        assert to_time is not None, f'{from_dt} is invalid'
    else:
        to_time = now

    from_ts = int(from_time.timestamp())
    to_ts = int(to_time.timestamp())

    with DB() as db:
        records = db.all()
        records = [r for r in records if from_ts <= r['timestamp'] <= to_ts]
        records.sort(key=lambda r: r['timestamp'], reverse=True)

        table = Table(box=None)

        table.add_column('ID', justify='right', style='bright_cyan', no_wrap=True)
        table.add_column('Title')
        table.add_column('Tags')
        table.add_column('Date', style='cyan')

        for rec in records:
            record = Record(**rec)
            table.add_row(f'{record.id}', record.title, record.tags_str, record.datetime())

        Console().print(table)

@cli.command()
@click.argument('id', type=click.INT)
def edit(id):
    """Edit a record's title and tags by ID, with confirmation before saving."""
    with DB() as db:
        Q = Query()
        record = db.get(Q.id == id)
        if not record:
            click.echo(f"No record found with ID {id}.")
            return

        rec = Record(**record)
        Console().print(f"[bold yellow]Editing record:[/bold yellow] ID: {rec.id}\tTitle: {rec.title}")

        new_title = questionary.text("Title", default=rec.title, validate=lambda text: len(text.strip()) > 0 or "Title cannot be empty").ask()
        new_tags_str = questionary.text("New tags (comma-separated)", default=rec.tags_str or "").ask()
        new_tags = [t.strip() for t in new_tags_str.split(',')] if new_tags_str else []

        Console().print("[bold green]Review changes:[/bold green]")
        Console().print(f"ID: {rec.id}")
        Console().print(f"Title: {new_title}")
        Console().print(f"Tags: {', '.join(new_tags) if new_tags else '-'}")

        if not questionary.confirm('Submit changes?').ask():
            return

        # Update and save
        db.update({'title': new_title, 'tags': new_tags}, Q.id == id)
        click.echo('Updated')

@cli.command()
@click.argument('id', type=click.INT)
def delete(id):
    """Delete a record by ID, with confirmation."""
    with DB() as db:
        Q = Query()
        record = db.get(Q.id == id)
        if not record:
            click.echo(f"No record found with ID {id}.")
            return

        rec = Record(**record)
        Console().print("[bold red]About to delete:[/bold red]", end=" ")
        Console().print(f"ID: {rec.id}\tTitle: {rec.title}")

        if not questionary.confirm('Are you sure?').ask():
            return

        db.remove(Q.id == id)
        click.echo(f"Deleted record with ID {id}.")

if __name__ == '__main__':
    cli()
