# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module implements interface with InfluxDB.'''
import os

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


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

    def write_signal(self, uasid: str, measurement: dict):
        write_api = self._client.write_api(write_options=SYNCHRONOUS)

        point = (
            Point('cell-signal')
            .tag('UasID', uasid)
            .tag('Radio', measurement.get('Radio'))
            .tag('Cell', measurement.get('Cell'))
            .tag('FrequencyBand', measurement.get('FrequencyBand'))
            .field('Latitude', measurement['Waypoint']['Latitude'])
            .field('Longitude', measurement['Waypoint']['Longitude'])
            .field('Altitude', measurement['Waypoint']['Altitude'])
            .field('Roll', measurement.get('Roll'))
            .field('Pitch', measurement.get('Pitch'))
            .field('Yaw', measurement.get('Yaw'))
            .field('VNorth', measurement.get('VNorth'))
            .field('VEast', measurement.get('VEast'))
            .field('VDown', measurement.get('VDown'))
            .field('VAir', measurement.get('VAir'))
            .field('Baro', measurement.get('Baro'))
            .field('Heading', measurement.get('Heading'))
            .field('RSRP', measurement.get('RSRP'))
            .field('RSRP', measurement.get('RSRP'))
            .field('RSRQ', measurement.get('RSRQ'))
            .field('RSSI', measurement.get('RSSI'))
            .field('SINR', measurement.get('SINR'))
            .field('Heartbeat', measurement.get('HeartbeatLoss'))
            .field('RTT', measurement.get('RTT'))
        )

        write_api.write(bucket=self._as_bucket, record=point, org=self._org)

    def read(self, uasid: str):
        query_api = self._client.query_api()

        query = f'''
            from(bucket: "{self._as_bucket}")
            |> range(start: -10m)
            |> filter(fn: (r) => r._measurement == f"{uasid}")
        '''

        tables = query_api.query(query)

        for table in tables:
            for record in table.records:
                print(record)
