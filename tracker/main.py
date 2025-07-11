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

def _show_record(record: Record, prefix: str = ''):
    if prefix and len(prefix) > 0:
        click.echo(prefix)

    click.secho(f'ID:    ', nl=False)
    click.secho(f'{record.id}', fg='green')
    click.secho(f'Title: ', nl=False)
    click.secho(f'{record.title}', fg='green')
    click.secho(f'Tag:   ', nl=False)
    click.secho(f'{record.tags_str or ''}', fg='green')

@click.group()
def cli():
    pass

@cli.command()
@click.argument('title', type=click.STRING, nargs=-1)
@click.option('--tag', type=click.STRING, help='Comma-separated list of tags')
@click.option('--date', type=click.STRING, help='Datetime in ISO format (defaults to now)')
def add(title, tag, date):
    """Add a new item with TITLE, optional TAGS, and optional DATETIME."""
    timestamp = (parse_datetime(date) or datetime.now()).timestamp()

    if title:
        title_str = ' '.join(title)
    else:
        title_str = questionary.text('Title', validate=lambda x: True if len(x) > 0 else 'Title must not be empty').ask()
        if not title_str:
            raise click.Abort()

    if not tag:
        tag = questionary.text('Tag (comma-separated)').ask()
        tag = tag.strip() if tag and len(tag) > 0 else None

    tag_list = [t.strip() for t in tag.split(',')] if tag else None

    item = Record(title=title_str, tags=tag_list, timestamp=timestamp)
    item.save()
    _show_record(item, 'Record added:')

@cli.command()
@click.option('--from', 'from_dt', default=None, help='Start datetime in ISO format (inclusive, defaults to 7 days ago)')
@click.option('--to', 'to_dt', default=None, help='End datetime in ISO format (inclusive, defaults to now)')
def list(from_dt, to_dt):
    """List all records from latest to past, optionally within a time range."""

    now = datetime.now()

    if from_dt:
        from_time = parse_datetime(from_dt)
        assert from_time is not None, f'{from_dt} is invalid'
    else:
        from_time = now - timedelta(days=7)

    if to_dt:
        to_time = parse_datetime(to_dt)
        assert to_time is not None, f'{from_dt} is invalid'
    else:
        to_time = now

    from_ts = int(from_time.timestamp())
    to_ts = int(to_time.timestamp())

    assert from_ts <= to_ts, '<from> must be less or equal to <to> date'

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
        _show_record(rec, 'Record updated:')

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
        Console().print("[bold red]About to delete:[/bold red]")
        _show_record(rec)

        if not questionary.confirm('Are you sure?').ask():
            return

        db.remove(Q.id == id)
        click.echo(f"Deleted record with ID {id}.")

@cli.command('continue')
@click.argument('id', type=click.INT)
@click.option('--tag', type=click.STRING, help='Comma-separated list of tags')
@click.option('--date', type=click.STRING, help='Datetime in ISO format (defaults to now)')
def continue_cmd(id, tag, date):
    """Duplicate an existing record by ID."""
    with DB() as db:
        Q = Query()
        record = db.get(Q.id == id)
        if not record:
            click.echo(f"No record found with ID {id}.")
            return

        timestamp = (parse_datetime(date) or datetime.now()).timestamp()
        rec = Record(**record)

        title_str = questionary.text('Title', default=rec.title, validate=lambda x: True if len(x) > 0 else 'Title must not be empty').ask()
        if not title_str:
            raise click.Abort()

        if not tag:
            tag = questionary.text('Tag (comma-separated)', default=rec.tags_str or '').ask()
            tag = tag.strip() if tag and len(tag) > 0 else None

        tag_list = [t.strip() for t in tag.split(',')] if tag else None

        item = Record(title=title_str, tags=tag_list, timestamp=timestamp)
        item.save()
        _show_record(item, 'Record duplicated:')

if __name__ == '__main__':
    cli()
