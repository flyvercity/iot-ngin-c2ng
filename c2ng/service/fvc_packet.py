from marshmallow import Schema, fields, validate


class FVCDataPacketTime(Schema):
    unix = fields.Float(required=True)


class FVCLocation(Schema):
    lat = fields.Float(description='Latitude in degress', required=True)
    lon = fields.Float(description='Longitude in degress', required=True)
    alt = fields.Float(description='Geodetic altitude in meters')
    baro = fields.Float(description='Aircraft Barometric Altitude')


class FVCSpeeds(Schema):    
    vnorth = fields.Float(description='Aircraft North Velocity (meters per second)')
    veast = fields.Float(description='Aircraft Eest Velocity (meters per second)')
    vdown = fields.Float(description='Aircraft Downward Velocity (meters per second)')
    vair = fields.Float(description='Aircraft Air Speed (meters per second)')


class FVCAttiude(Schema):
    roll = fields.Integer(description='Aircraft Roll (degrees)')
    pitch = fields.Integer(description='Aircraft Pitch (degrees)')
    yaw = fields.Integer(description='Aircraft Yaw (degrees)')
    heading = fields.Float(description='Aircraft True Heading (degrees)')


class FVCPosition(Schema):
    location = fields.Nested(FVCLocation, required=True)
    attitude = fields.Nested(FVCAttiude)
    speeds = fields.Nested(FVCSpeeds)


class FVCSignal(Schema):
    radio = fields.String(validate=validate.OneOf([
        'UNKNOWN',
        '4G',
        '5GNSA',
        '5GSA'
    ]), description='Current Radio Mode', required=True)

    RSRP = fields.Integer(description='Reference Signal Received Power')
    RSRQ = fields.Integer(description='Reference Signal Received Quality')
    RSRP_4G = fields.Integer(description='Reference Signal Received Power (LTE)')
    RSRQ_4G = fields.Integer(description='Reference Signal Received Quality (LTE)')
    RSRP_5G = fields.Integer(description='Reference Signal Received Power (LTE)')
    RSRQ_5G = fields.Integer(description='Reference Signal Received Quality (NR)')
    cell = fields.String(description='Aircraft Serving physical cell identifier')
    band = fields.String(description='Aircraft Serving Frequency Band Identification')
    RSSI = fields.Integer(description='Received Signal Strength Indicator')
    SINR = fields.Integer(description='Signal to Interference & Noise Ratio')


class FVCPerf(Schema):
    heartbeat_loss = fields.Boolean(description='Heartbeat Loss Flag')
    RTT = fields.Float(description='Round-Trip Time (ms)')


class FVCPacket(Schema):
    timestamp = fields.Nested(FVCDataPacketTime, required=True)
    position = fields.Nested(FVCPosition)
    signal = fields.Nested(FVCSignal)
    perf = fields.Nested(FVCPerf)
