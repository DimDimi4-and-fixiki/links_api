import click
import uvicorn

import config


@click.group()
def cli():
    pass


@cli.command()
def run_server():
    uvicorn.run(
        'commands.run_server:main_app',
        host=config.HOST,
        port=config.PORT,
        log_level='info',
    )


if __name__ == '__main__':
    cli()
