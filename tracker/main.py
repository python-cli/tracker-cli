import click

from .config import *
from .model import *
from .time import *

@click.group()
def cli():
    pass

@cli.command()
@click.argument('title', nargs=-1)
@click.option('--tags', help='Comma-separated list of tags')
@click.option('--time', help='Datetime in ISO format (defaults to now)')
def add(title, tags, time):
    """Add a new item with TITLE, optional TAGS, and optional DATETIME."""
    time = parse_time_str(time)

    # id is timestamp in milliseconds
    id = int(time.timestamp() * 1000)
    tag_list = list(map(lambda x: x.strip(), tags.split(','))) if tags else None
    title_str = ' '.join(title)
    item = Record(id=id, title=title_str, tags=tag_list)
    item.save()
    click.echo(f"Added: {item.title} with tags: {item.tags}")

@cli.command()
@click.option('--from', 'from_dt', default=None, help='Start datetime in ISO format (inclusive, defaults to 3 days ago)')
@click.option('--to', 'to_dt', default=None, help='End datetime in ISO format (inclusive, defaults to now)')
def list(from_dt, to_dt):
    """List all records from latest to past, optionally within a time range."""
    from datetime import datetime, timedelta
    from tinydb import Query

    now = datetime.now()

    if from_dt:
        from_time = datetime.fromisoformat(from_dt)
    else:
        from_time = now - timedelta(days=3)
        
    if to_dt:
        to_time = datetime.fromisoformat(to_dt)
    else:
        to_time = now

    from_id = int(from_time.timestamp() * 1000)
    to_id = int(to_time.timestamp() * 1000)

    with DB() as db:
        records = db.all()
        # Filter by id (timestamp in ms)
        records = [r for r in records if from_id <= r['id'] <= to_id]
        # Sort by id descending (latest first)
        records.sort(key=lambda r: r['id'], reverse=True)

        for rec in records:
            click.echo(f"{rec['id']}: {rec['title']} [tags: {' '.join(rec['tags'] or [])}]")

if __name__ == '__main__':
    cli()
