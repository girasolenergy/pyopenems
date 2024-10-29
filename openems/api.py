"""OpenEMS API."""
import asyncio
import uuid

from jsonrpc_websocket import Server

import pandas as pd


class OpenEMSAPIClient():
    """OpenEMS API Client Class."""

    def __init__(self, server_url, username, password):
        """__init__."""
        self.server_url = server_url
        self.username = username
        self.password = password

    async def login(self):
        """login."""
        server = Server(self.server_url)
        await server.ws_connect()
        await server.authenticateWithPassword(username=self.username, password=self.password)
        return server

    def get_edges(self):
        """Call getEdges API."""
        async def f():
            server = await self.login()
            r = await server.getEdges(page=0, limit=20, searchParams={})
            return r['edges']
        return asyncio.run(f())

    def get_edge_config(self, edge_id):
        """Call getEdgeConfig API."""
        async def f():
            server = await self.login()
            r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                'jsonrpc': '2.0',
                'method': 'getEdgeConfig',
                'params': {
                },
                'id': str(uuid.uuid4()),
            })
            r = r_edge_rpc['payload']['result']
            return r
        return asyncio.run(f())

    def query_historic_timeseries_data(self, edge_id, start, end, channels, resolution_sec=None):
        """Call edgeRpc.queryHistoricTimeseriesData API."""
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
            r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                'jsonrpc': '2.0',
                'method': 'queryHistoricTimeseriesData',
                'params': params,
                'id': str(uuid.uuid4()),
            })
            r = r_edge_rpc['payload']['result']
            df = pd.DataFrame(r['data'], index=r['timestamps'])
            df.index.name = 'Time'
            df.index = pd.to_datetime(df.index)
            return df
        return asyncio.run(f())

    def update_component_config(self, edge_id, component_id, properties):
        """Call edgeRpc.updateComponentConfig API."""
        async def f():
            server = await self.login()
            r_edge_rpc = await server.edgeRpc(edgeId=edge_id, payload={
                'jsonrpc': '2.0',
                'method': 'updateComponentConfig',
                'params': {
                    'componentId': component_id,
                    'properties': properties,
                },
                'id': str(uuid.uuid4()),
            })
            r = r_edge_rpc['payload']['result']
            return r
        return asyncio.run(f())

    def update_component_config_from_name_value(self, edge_id, component_id, name, value):
        """Call edgeRpc.updateComponentConfig API.

        This function has name and value argument instead of properties argument of update_component_config method.
        """
        return self.update_component_config(
            edge_id,
            component_id,
            properties=[
                {'name': name, 'value': value},
            ],
        )

    def get_meter_list(self, edge_id):
        """Extract meter list form edge config."""
        edge_config = self.get_edge_config(edge_id)
        components = edge_config['components']
        return dict([(k, v) for (k, v) in components.items() if v['factoryId'].split('.')[0] == 'Meter'])

    def get_pvinverter_list(self, edge_id):
        """Extract pvinverter list form edge config."""
        edge_config = self.get_edge_config(edge_id)
        components = edge_config['components']
        return dict([(k, v) for (k, v) in components.items() if v['factoryId'].split('.')[0] == 'PVInverter'])
