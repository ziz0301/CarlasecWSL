import cantools
import struct

# Load DBC
db = cantools.database.load_file("bmw.dbc")
msg = db.get_message_by_name("EngineData")

# Craft two signals
signals_1 = {
    "VehicleSpeed": 0,
    "MovingForward": 0,
    "MovingReverse": 0,
    "BrakePressed": 1.0,  # physical value
    "Brake_active": 1,
    "YawRate": 0,
    "Counter_416": 0,
    "Checksum_416": 0  # temp, we'll fill it later
}
data_1 = bytearray(msg.encode(signals_1))

# Compute checksum for first 6 bytes
checksum = sum(data_1[:6]) % 65536
data_1[6] = (checksum >> 8) & 0xFF
data_1[7] = checksum & 0xFF

print("Message for BrakePressed = 0.5:")
print(" ".join(f"{b:02X}" for b in data_1))

decoded = msg.decode(data_1)
print("Decode for test:")
print(decoded)