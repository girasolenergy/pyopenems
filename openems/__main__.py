"""OpenEMS CLI."""
import json

import click

from . import api


@click.group()
@click.pass_context
@click.option('--server-url', default='ws://localhost:8081')
@click.option('--username', default='admin')
@click.option('--password', default='password')
def openems_cli(ctx, server_url, username, password):
    """OpenEMS CLI.

    Args:
        ctx: Click context object.
        server_url: OpenEMS server WebSocket URL.
        username: Username for authentication.
        password: Password for authentication.
    """
    client = api.OpenEMSAPIClient(server_url, username, password)
    ctx.obj = {
        'client': client,
    }


@openems_cli.command()
@click.pass_context
def get_edge_list(ctx):
    """Get OpenEMS Edge List.

    Args:
        ctx: Click context object.
    """
    edges = ctx.obj['client'].get_edges()

    for edge in edges:
        click.echo(click.style(edge['id'], fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
def get_edge_config(ctx, edge_id):
    """Get OpenEMS Edge Config.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
    """
    edge_config = ctx.obj['client'].get_edge_config(edge_id)

    click.echo(click.style(json.dumps(edge_config, indent=2), fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
def get_meter_list(ctx, edge_id):
    """Get OpenEMS Meter List.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
    """
    meters = ctx.obj['client'].get_meter_list(edge_id)

    for (k, _) in meters.items():
        click.echo(click.style(k, fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
def get_pvinverter_list(ctx, edge_id):
    """Get OpenEMS PVInverter List.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
    """
    pvinverters = ctx.obj['client'].get_pvinverter_list(edge_id)

    for (k, _) in pvinverters.items():
        click.echo(click.style(k, fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
@click.argument('component-id')
def get_channel_list(ctx, edge_id, component_id):
    """Get OpenEMS Channel List.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
        component_id: Component ID (e.g., meter ID, inverter ID).
    """
    channels = ctx.obj['client'].get_channels_of_component(edge_id, component_id)['channels']
    for channel in channels:
        click.echo(click.style(f'{component_id}/{channel["id"]}', fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
@click.argument('component-id')
@click.argument('name')
@click.argument('value')
def update_component_config(ctx, edge_id, component_id, name, value):
    """Update OpenEMS Component Config.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
        component_id: Component ID to update.
        name: Configuration parameter name.
        value: New value for the configuration parameter.
    """
    r = ctx.obj['client'].update_component_config_from_name_value(edge_id, component_id, name, value)
    click.echo(click.style(f'{r}', fg='green'))


@openems_cli.command()
@click.pass_context
@click.argument('edge-id')
@click.argument('channel')
@click.argument('start', type=click.DateTime(['%Y-%m-%d']))
@click.argument('end', type=click.DateTime(['%Y-%m-%d']))
@click.argument('resolution-sec', type=int)
def get_channel_data(ctx, edge_id, channel, start, end, resolution_sec):
    """Get OpenEMS Channel Data.

    Args:
        ctx: Click context object.
        edge_id: Edge device ID.
        channel: Channel name (e.g., 'meter0/ActivePower').
        start: Start date for data query.
        end: End date for data query.
        resolution_sec: Data resolution in seconds.
    """
    df = ctx.obj['client'].query_historic_timeseries_data(edge_id, start.date(), end.date(), [channel], resolution_sec)

    click.echo(click.style(df.to_csv(), fg='green'))


if __name__ == '__main__':
    openems_cli(auto_envvar_prefix='OPENEMS_CLI')
