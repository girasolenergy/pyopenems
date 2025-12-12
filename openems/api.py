"""OpenEMS API."""
import uuid

import jsonrpc_base

from jsonrpc_websocket import Server

import pandas as pd

from . import exceptions
from .utils.bridge import ASGIRefBridge


class OpenEMSAPIClient():
    """OpenEMS API Client Class."""

    def __init__(self, server_url, username, password):
        """Create client instance and initialize connection helpers.

        Args:
            server_url: OpenEMS server WebSocket URL.
            username: Username for authentication.
            password: Password for authentication.
        """
        self.server_url = server_url
        self.username = username
        self.password = password
        self._server = None
        self._bridge = ASGIRefBridge()

    def __del__(self):
        """Ensure connection is closed on garbage collection."""
        self._bridge.shutdown()

    async def login(self):
        """Return an authenticated websocket server connection.

        Returns:
            Server: Authenticated WebSocket server connection.

        Raises:
            APIError: If authentication fails.
            jsonrpc_base.jsonrpc.ProtocolError: If an unexpected protocol error occurs.
        """
        if self._server is None or not hasattr(self._server, 'connected') or not self._server.connected:
            server = Server(self.server_url)
            await server.ws_connect()
            try:
                await server.authenticateWithPassword(username=self.username, password=self.password)
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            self._server = server
        return self._server

    def get_edges(self):
        """Call getEdges API.

        Returns:
            list: List of edge devices with their configuration.
        """
        async def f():
            server = await self.login()
            page = 0
            limit = 100
            edges = []
            while True:
                try:
                    r = await server.getEdges(page=page, limit=limit, searchParams={})
                except jsonrpc_base.jsonrpc.ProtocolError as e:
                    if isinstance(e.args, tuple):
                        raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                    raise
                edges.extend(r['edges'])
                if len(r['edges']) < limit:
                    break
                page += 1
            return edges
        return self._bridge.run(f)

    def get_edge_config(self, edge_id):
        """Call getEdgeConfig API.

        Args:
            edge_id: Edge device ID.

        Returns:
            dict: Edge configuration including components and their settings.
        """
        async def f():
            server = await self.login()
            try:
                r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                    'jsonrpc': '2.0',
                    'method': 'getEdgeConfig',
                    'params': {
                    },
                    'id': str(uuid.uuid4()),
                })
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            r = r_edge_rpc['payload']['result']
            return r
        return self._bridge.run(f)

    def get_channels_of_component(self, edge_id, component_id):
        """Call getChannelsOfComponent API.

        Args:
            edge_id: Edge device ID.
            component_id: Component ID to query channels for.

        Returns:
            dict: Component channels information including channel IDs and metadata.
        """
        async def f():
            server = await self.login()
            try:
                r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                    'jsonrpc': '2.0',
                    'method': 'componentJsonApi',
                    'params': {
                        'componentId': '_componentManager',
                        'payload': {
                            'jsonrpc': '2.0',
                            'method': 'getChannelsOfComponent',
                            'params': {
                                'componentId': component_id,
                            },
                            'id': str(uuid.uuid4()),
                        },
                    },
                    'id': str(uuid.uuid4()),
                })
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            r = r_edge_rpc['payload']['result']
            return r
        return self._bridge.run(f)

    def query_historic_timeseries_data(self, edge_id, start, end, channels, resolution_sec=None):
        """Call edgeRpc.queryHistoricTimeseriesData API.

        Args:
            edge_id: Edge device ID.
            start: Start date for data query.
            end: End date for data query.
            channels: List of channel names to query (e.g., ['meter0/ActivePower']).
            resolution_sec: Optional data resolution in seconds.

        Returns:
            pd.DataFrame: Time-series data with timestamps as index and channels as columns.
        """
        async def f():
            server = await self.login()
            params = {
                'timezone': 'Asia/Tokyo',
                'fromDate': start.isoformat(),
                'toDate': end.isoformat(),
                'channels': channels,
            }
            if resolution_sec:
                params['resolution'] = {
                    'value': resolution_sec,
                    'unit': 'SECONDS',
                }
            try:
                r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                    'jsonrpc': '2.0',
                    'method': 'queryHistoricTimeseriesData',
                    'params': params,
                    'id': str(uuid.uuid4()),
                })
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            r = r_edge_rpc['payload']['result']
            df = pd.DataFrame(r['data'], index=r['timestamps'])
            df.index.name = 'Time'
            df.index = pd.to_datetime(df.index)
            return df
        return self._bridge.run(f)

    def update_component_config(self, edge_id, component_id, properties):
        """Call edgeRpc.updateComponentConfig API.

        Args:
            edge_id: Edge device ID.
            component_id: Component ID to update.
            properties: List of property dictionaries with 'name' and 'value' keys.

        Returns:
            dict: Update result from the API.
        """
        async def f():
            server = await self.login()
            try:
                r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                    'jsonrpc': '2.0',
                    'method': 'updateComponentConfig',
                    'params': {
                        'componentId': component_id,
                        'properties': properties,
                    },
                    'id': str(uuid.uuid4()),
                })
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            r = r_edge_rpc['payload']['result']
            return r
        return self._bridge.run(f)

    def update_component_config_from_name_value(self, edge_id, component_id, name, value):
        """Call edgeRpc.updateComponentConfig API.

        This function has name and value argument instead of properties argument of update_component_config method.

        Args:
            edge_id: Edge device ID.
            component_id: Component ID to update.
            name: Configuration parameter name.
            value: New value for the configuration parameter.

        Returns:
            dict: Update result from the API.
        """
        return self.update_component_config(
            edge_id,
            component_id,
            properties=[
                {'name': name, 'value': value},
            ],
        )

    def get_meter_list(self, edge_id):
        """Extract meter list from edge config.

        Args:
            edge_id: Edge device ID.

        Returns:
            dict: Dictionary of meter components keyed by component ID.
        """
        edge_config = self.get_edge_config(edge_id)
        components = edge_config['components']
        return dict([(k, v) for (k, v) in components.items() if v['factoryId'].split('.')[0] == 'Meter'])

    def get_pvinverter_list(self, edge_id):
        """Extract pvinverter list from edge config.

        Args:
            edge_id: Edge device ID.

        Returns:
            dict: Dictionary of PV inverter components keyed by component ID.
        """
        edge_config = self.get_edge_config(edge_id)
        components = edge_config['components']
        return dict([(k, v) for (k, v) in components.items() if v['factoryId'].split('.')[0] == 'PVInverter'])

    def query_futuristic_timeseries_data(self, edge_id, start, end, channels, component_id, resolution_sec=None):
        """Call edgeRpc.queryFuturisticTimeseriesData API.

        This API combines historical data from InfluxDB and future data from edge RPC.
        The backend automatically splits the time range at 'now':
        - [start, now): Retrieved from InfluxDB (historical)
        - [now, end]: Retrieved from edge via componentJsonApi.getTimeToRateMap (future)

        Args:
            edge_id: Edge device ID.
            start: Start date for data query.
            end: End date for data query.
            channels: List of channel names to query (e.g., ['ctrloutput0/GridOrderCurtailmentRate']).
            component_id: Component ID to query future data from (e.g., 'ctrloutput0', 'gridSchedule0').
            resolution_sec: Optional data resolution in seconds.

        Returns:
            pd.DataFrame: Time-series data with timestamps as index and channels as columns,
                         combining both historical and future data.
        """
        async def f():
            server = await self.login()
            params = {
                'timezone': 'Asia/Tokyo',
                'fromDate': start.isoformat(),
                'toDate': end.isoformat(),
                'channels': channels,
                'componentId': component_id,
            }
            if resolution_sec:
                params['resolution'] = {
                    'value': resolution_sec,
                    'unit': 'SECONDS',
                }
            try:
                r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                    'jsonrpc': '2.0',
                    'method': 'queryFuturisticTimeseriesData',
                    'params': params,
                    'id': str(uuid.uuid4()),
                })
            except jsonrpc_base.jsonrpc.ProtocolError as e:
                if isinstance(e.args, tuple):
                    raise exceptions.APIError(message=f'{e.args[0]}: {e.args[1]}', code=e.args[0])
                raise
            r = r_edge_rpc['payload']['result']
            df = pd.DataFrame(r['data'], index=r['timestamps'])
            df.index.name = 'Time'
            df.index = pd.to_datetime(df.index)
            return df
        return self._bridge.run(f)
