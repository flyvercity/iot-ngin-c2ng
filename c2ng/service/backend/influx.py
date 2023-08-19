# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements interface with InfluxDB.'''
import os
import logging as lg

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


MEASUREMENT_NAME = 'cell-signal'


class Influx():
    '''Influx Client Helper Class.'''

    def __init__(self, config: dict):
        '''Constructor.

        Args:
            config: `influx` section of the configurations dict.
        '''

        token = os.getenv('DOCKER_INFLUXDB_INIT_ADMIN_TOKEN')
        self._org = config['org']
        url = config['uri']
        self._client = InfluxDBClient(url=url, token=token, org=self._org)
        self._as_bucket = config['bucket']

    def write_signal(self, uasid: str, packet: dict):
        '''Write signal data to InfluxDB.

        Args:
            uasid: UAS identifier.
            packet: signal data packet.
        '''

        write_api = self._client.write_api(write_options=SYNCHRONOUS)

        lg.debug(f'Writing {packet} to {self._as_bucket}')

        position = packet.get('position')
        location = position.get('location') if position else None
        attitude = position.get('attitude') if position else None
        speeds = position.get('speeds') if position else None
        signal = packet.get('signal')
        perf = packet.get('perf')

        point = Point(MEASUREMENT_NAME).tag('uasid', uasid)

        if signal:
            point.tag('radio', signal.get('radio'))
            point.tag('cell', signal.get('radio'))
            point.tag('band', signal.get('band'))
            point.field('RSRP', signal.get('RSRP'))
            point.field('RSRP', signal.get('RSRP'))
            point.field('RSRQ', signal.get('RSRQ'))
            point.field('RSSI', signal.get('RSSI'))
            point.field('SINR', signal.get('SINR'))

        if location:
            point.field('latitude', location['lat'])
            point.field('longitude', location['lon'])
            point.field('altitude', location['alt'])
            point.field('baro', location.get('baro'))

        if attitude:
            point.field('roll', attitude.get('roll'))
            point.field('pitch', attitude.get('pitch'))
            point.field('yaw', attitude.get('yaw'))
            point.field('heading', attitude.get('heading'))

        if speeds:
            point.field('vnorth', speeds.get('vnorth'))
            point.field('veast', speeds.get('veast'))
            point.field('vdown', speeds.get('vdown'))
            point.field('vair', speeds.get('vair'))

        if perf:
            point.field('heartbeat_loss', perf.get('heartbeat_loss'))
            point.field('RTT', perf.get('RTT'))

        write_api.write(bucket=self._as_bucket, record=point, org=self._org)

    def read(self, uasid: str, value: str, window: int, function='mean'):
        '''Read signal data from InfluxDB.

        Args:
            uasid: UAS identifier.
            value: field name to read.
            window: time window in minutes.
            function: aggregation function (mean, max, min, etc.).

        Returns:
            List of values.
        '''

        query_api = self._client.query_api()
        bucket = self._as_bucket

        query = f'''
            from(bucket: "{bucket}")
                |> range(start: -{window}m)
                |> filter(fn: (r) => r._measurement == "{MEASUREMENT_NAME}")
                |> filter(fn: (r) => r.uasid == "{uasid}")
                |> filter(fn: (r) => r._field == "{value}")
                |> {function}()
        '''

        lg.debug(f'Querying InfluxDB: {query}')
        tables = query_api.query(query)
        return tables[0].records[0]['_value']
