# !/home/vel/miniforge3/envs/carlasec/bin/python
# This file can be run with python=3.8 and carla=0.9.14

# [11.05.2025] - [guhnn] - [ziz0301@gmail.com]
# This work pertains to a PhD project on vehicle security modeling.

# This class allows the Carla vehicle to connect with the CANBUS and dump/receive messages from it.
# The CAN message structure is taken from the bmw_e9x_e8x.dbc - commaai/opendbc
# Using WheelSpeeds, EngineAndBrake, SteeringWheelAngle, Speed, Door, Light, Gear

import threading
import queue
import time
import can
import cantools
import carla
import random


can_queue = queue.PriorityQueue()
class CAN():
    def __init__(self):
        self.db = cantools.database.load_file('bmw.dbc') # Define CAN-message format

        #Define CAN message by name
        self.door_message = self.db.get_message_by_name('DoorControlSensors')
        self.light_message = self.db.get_message_by_name('LightControl')
        self.wheelspeed_message = self.db.get_message_by_name('WheelSpeeds')
        self.enginedata_message = self.db.get_message_by_name('EngineData')
        self.handbrake_message = self.db.get_message_by_name('InstrumentHandBrake')
        self.steering_message = self.db.get_message_by_name('SteeringWheelAngle')
        self.gear_message = self.db.get_message_by_name('GearSelectorSwitch')
        self.gear_message_test = self.db.get_message_by_name('TransmissionDataTest')

    #---------------------------------------------------------
    # FUNCTIONS FOR DEFINEDING AND DUMPING CAN MESSAGES
    #---------------------------------------------------------

    # Define wheelspeed message
    def dump_wheelspeed(self,speed):
        with can.interface.Bus(bustype='socketcan', channel='kcan4') as kcan4:
            data = self.wheelspeed_message.encode({'Wheel_FL': speed,'Wheel_FR':speed, 'Wheel_RL':speed, 'Wheel_RR': speed})
            message = can.Message(arbitration_id=self.wheelspeed_message.frame_id, data=data)
            kcan4.send(message)
        #print(message)

    # Define door message
    def dump_door(self,world, trunk=0, mirror=2, checksum=0):
        with can.interface.Bus(bustype='socketcan', channel='kcan4') as kcan4:
            door_open = world.doors_are_open
            data = self.door_message.encode({'Door_FL': int(door_open),
                                             'Door_FR': int(door_open),
                                             'Door_RL': int(door_open),
                                             'Door_RR': int(door_open),
                                             'TrunkStatus': trunk,
                                             'MirrorStatus': mirror,
                                             'Checksum_416': checksum})
            message = can.Message(arbitration_id=self.door_message.frame_id, data=data)
            kcan4.send(message)

    # Define wheelspeed message
    def dump_light(self,vehicle):
        light_none, light_lowbeam, light_highbeam, light_reverse = False, False, False, False
        light_brake, light_rightblinker, light_leftblinker, light_fog = False, False, False, False
        light_interior, light_special1, light_special2= False, False, False
        with can.interface.Bus(bustype='socketcan', channel='kcan4') as kcan4:
            light_state = vehicle.get_light_state()
            #print(f"Light State: {light_state}")
            if light_state == carla.VehicleLightState.NONE:
                light_none = True
            elif light_state == carla.libcarla.VehicleLightState(3):
                light_lowbeam = True
            elif light_state == carla.VehicleLightState.HighBeam:
                light_highbeam = True
            elif light_state == carla.VehicleLightState.Reverse:
                light_reverse = True
            elif light_state == carla.VehicleLightState.Brake:
                light_brake = True
            elif light_state == carla.VehicleLightState.RightBlinker:
                light_rightblinker = True
            elif light_state == carla.VehicleLightState.LeftBlinker:
                light_leftblinker = True
            elif light_state == carla.VehicleLightState.Fog:
                light_fog = True
            elif light_state == carla.VehicleLightState.Interior:
                light_interior = True
            elif light_state == carla.VehicleLightState.Special1:
                light_special1 = True
            elif light_state == carla.VehicleLightState.Special2:
                light_special2 = True
            data = self.light_message.encode({'LowBeam':int(light_lowbeam),'HighBeam':int(light_highbeam), 'Reverse':int(light_reverse), 'LightOff':int(light_none), 'Brake':int(light_brake), 'RightBlinker':int(light_rightblinker), 'LeftBlinker':int(light_leftblinker), 'Fog':int(light_fog), 'Interior':int(light_interior), 'Special1':int(light_special1), 'Special2':int(light_special2)})
            message = can.Message(arbitration_id=self.light_message.frame_id, data=data)
            kcan4.send(message)

    # Define and dump throttle message
    def dump_throttle(self, control, speed, checksum=0):
        with can.interface.Bus(bustype='socketcan', channel='vcan0') as bus:
            brake_value = control.brake
            brake_flag = 1 if brake_value > 0.0 else 0

            data = bytearray(self.enginedata_message.encode({
                'VehicleSpeed': speed,
                'MovingForward': control.throttle,
                'MovingReverse': control.reverse,
                'BrakePressed': brake_value,
                'Brake_active': brake_flag,
                'YawRate': speed,
                'Counter_416': 0,
                'Checksum_416': 0  # temporary
            }))

            # Calculate checksum from first 7 bytes to store in 16 bits checksum
            checksum = sum(data[:6]) % 65536  
            data[6] = (checksum >> 8) & 0xFF  
            data[7] = checksum & 0xFF        

            
            message = can.Message(arbitration_id=self.enginedata_message.frame_id, data=data)
            bus.send(message)

    # Define and dump hand brake message
    def dump_handbrake(self, control, checksum=0):
        #print(f"Start sending CAN_speed message with ID {self.handbrake_message.frame_id}")
        with can.interface.Bus(bustype='socketcan', channel='vcan0') as bus:
            data = self.handbrake_message.encode({'HandbrakeActive':control.hand_brake,'Checksum_416': checksum})
            message = can.Message(arbitration_id=self.handbrake_message.frame_id, data=data)
            bus.send(message)

    # Define and dump steer message
    def dump_steering(self, control, vehicle, speed, checksum=0):
        #print(f"Start sending CAN_speed message with ID {self.steering_message.frame_id}")
        with can.interface.Bus(bustype='socketcan', channel='vcan0') as bus:
            print(f"[DEBUG] Steer position: {control.steer}")
            #print(f"[TX] Raw CAN data: {data.hex()}")
            encoded = self.steering_message.encode({'SteeringPosition': control.steer,
                                                'FrontWheel': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.Front_Wheel)),
                                                'BackWheel': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.Back_Wheel)),
                                                'SteeringWheelFL': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FL_Wheel)),
                                                'SteeringWheelFR': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FR_Wheel)),
                                                'SteeringWheelBL': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.BL_Wheel)),
                                                'SteeringWheelBR': float(vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.BR_Wheel)),
                                                'Checksum_416': checksum})
            data = bytearray(encoded)
            checksum = sum(data[:7]) % 256 
            data[7] = checksum  # Set byte 7 with calculated checksum
            message = can.Message(arbitration_id=self.steering_message.frame_id, data=data)            
            bus.send(message)

    # Define and dump gear message
    def dump_gear(self, control, checksum=0):
        with can.interface.Bus(bustype='socketcan', channel='vcan0') as bus:
            data = self.gear_message.encode({'Checksum': checksum, 'Shifting':control.manual_gear_shift,'GearRatio': random.randint(0,255), 'GearTar': control.gear, 'Checksum_416': checksum})
            #print(f"Gear Value: {control.gear}")
            message = can.Message(arbitration_id=self.gear_message.frame_id, data=data)
            bus.send(message)

    def dump_gear_test(self, control, checksum=0):
        with can.interface.Bus(bustype='socketcan', channel='vcan0') as bus:
            data = self.gear_message_test.encode({'GearTar': -1})
            message = can.Message(arbitration_id=self.gear_message_test.frame_id, data=data)
            bus.send(message)


    #---------------------------------------------------------
    # FUNCTIONS FOR CONVERT CAN MESSAGE TO CARLA.VEHICLE.CONTROL
    #---------------------------------------------------------

    # Convert WheelSpeed message to carla vehicle
    def control_wheelspeed(self,velocity):
        kcan4 = can.interface.Bus(bustype='socketcan', channel='vcan0')
        print("KCAN4 is listening")
        while True:
            try:
                msg = kcan4.recv()
                if msg is not None:
                    data = self.wheelspeed_message.decode(msg.data)
                    self.can_speed = data.get("Wheel_FL")
                    print(data)
                    return self.can_speed
                else:
                    return velocity
            except Exception as e:
                print(f"Exception in CAN Bus Listener: {e}")

    # Convert door message to carla vehicle
    def control_door(self, vehicle, msg):
        #can_queue.put((msg.arbitration_id, msg))
        data = self.door_message.decode(msg.data)
        print (f"data: {data}")
        if data.get("Door_FL") == 1 and data.get("Door_RL") == 1 and data.get("Door_FR") == 1 and data.get("Door_RR") == 1:
            print ("Door Open")
            return vehicle.open_door(carla.VehicleDoor.All)
        if data.get("Door_FL") == 0 and data.get("Door_RL") == 0 and data.get("Door_FR") == 0 and data.get("Door_RR") == 0:
            print (vehicle)
            return vehicle.close_door(carla.VehicleDoor.All)

    # Convert light message to carla vehicle
    def control_light(self, vehicle, msg):
        #can_queue.put((msg.arbitration_id, msg))
        data = self.light_message.decode(msg.data)
        if data.get("LowBeam") == 1:
            light_mask=carla.VehicleLightState.LowBeam
            return vehicle.set_light_state(carla.VehicleLightState(light_mask))
        elif data.get("HighBeam") == 1:
            light_mask=carla.VehicleLightState.HighBeam
            return vehicle.set_light_state(carla.VehicleLightState(light_mask))
        elif data.get("Reverse") == 1:
            light_mask=carla.VehicleLightState.Reverse
            return vehicle.set_light_state(carla.VehicleLightState(light_mask))
        elif data.get("LightOff") == 1:
            light_mask=carla.VehicleLightState.NONE
            return vehicle.set_light_state(carla.VehicleLightState(light_mask))

        else:
            print("ERROR")

    # Convert Throttle message to carla vehicle control
    def control_throttle(self, control, msg):
        #vcan0 = can.interface.Bus(bustype='socketcan', channel='vcan0')
        #msg = self.vcan0.recv()
        #print(f"Message information: {msg.data}")
        data = self.throttle_message.decode(msg.data)
        print(data)
        if data.get("Checksum_416") == 15:
            control.throttle = data.get("MovingForward")
            control.reverse = data.get("MovingReverse")
            control.manual_gear_shift = True
        else:
            control.manual_gear_shift = False
        #print(control)
        return control

    
    def control_enginedata_seperate(self, control, msg):
        data = self.enginedata_message.decode(msg.data)
        #print("[DEBUG] Raw engine data values:", data)
        if data.get("Checksum_416") != 0:
            moving_forward = data.get("MovingForward", 0)
            moving_reverse = data.get("MovingReverse", 0)
            brake_active = data.get("Brake_active", 0)
            brake_value = data.get("BrakePressed", 0.0)
            brake_value = max(0.0, min(brake_value, 1.0))
            
            if moving_forward == 1 and moving_reverse == 1:
                print("Conflict: Both forward and reverse set. Ignoring input.")
                return None
            if brake_active == 1:
                control.brake = brake_value
            else:
                speed = data.get("VehicleSpeed", 0)
                throttle_value = min(speed / 100.0, 1.0)
                if moving_forward == 1:
                    control.throttle = throttle_value
                    control.reverse = False
                elif moving_reverse == 1:
                    control.throttle = throttle_value
                    control.reverse = True
                else:
                    control.throttle = 0.0
                    control.reverse = False
            return control
        else:
            control.manual_gear_shift = False
            return None

    def control_steering_seperate(self, vehicle, control, msg):
        data = self.steering_message.decode(msg.data)        
        #print("[DEBUG] Raw steering control values:", data)
        if data.get("Checksum_416") != 0 :
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.FL_Wheel, float(data.get("SteeringWheelFL")))
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.FR_Wheel, float(data.get("SteeringWheelFR")))
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.BL_Wheel, float(data.get("SteeringWheelBL")))
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.BR_Wheel, float(data.get("SteeringWheelBR")))
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.Front_Wheel, float(data.get("FrontWheel")))
            vehicle.set_wheel_steer_direction(carla.VehicleWheelLocation.Back_Wheel, float(data.get("BackWheel")))
            control.steer = data.get("SteeringPosition")
            return control
            #return None;
        else:
            #print("No hack")
            return None
    
    #------------------------------------------------------------------------------
    # OLD FUNCTION, PUT HERE TO STORE
    # TESTING ONLY - FUNCTIONS FOR CONVERT CAN MESSAGE TO CARLA.VEHICLE.CONTROL
    # Using cansend vcan0 to test
    #-----------------------------------------------------------------------------

    # Convert Speed message to carla vehicle control seperatly - For test only

    def control_wheelspeed_seperate(self, control, msg):
        data = self.enginedata_message.decode(msg.data)

        '''
        control.throttle = data.get("MovingForward")
        control.reverse = data.get("MovingReverse")
        control.manual_gear_shift = True
        '''

        if data.get("Checksum_416") != 0 :
            print(data)
            control.throttle = data.get("MovingForward")
            control.reverse = data.get("MovingReverse")
            #control.manual_gear_shift = True
            return control
            #control_can.gear = 2
        else:
            control.manual_gear_shift = False
            #print("No hack")
            return None

        #print(control)
        #return control


    def control_gear_seperate(self, control, msg):
        data = self.gear_message.decode(msg.data)
        #print(f"Message data:{msg.data}")
        if data.get("Checksum_416") != 0 :
            #print(f"Decode data:{data}")
            control.gear = data.get("GearTar")
            control.manual_gear_shift = data.get("Shifting")
            return control
        else:
            #print("No hack")
            return None


    

    # Convert door message to carla vehicle control seperatly. Done, has been used for counting door open time
    def control_door_seperate1(self, vehicle, msg):
        data = self.door_message.decode(msg.data)
        if data.get("Checksum_416") != 0:
            #print(data)
            if data.get("Door_FL") == 1 and data.get("Door_RL") == 1 and data.get("Door_FR") == 1 and data.get(
                    "Door_RR") == 1:
                vehicle.open_door(carla.VehicleDoor.All)
                return 1
            if data.get("Door_FL") == 0 and data.get("Door_RL") == 0 and data.get("Door_FR") == 0 and data.get(
                    "Door_RR") == 0:
                vehicle.close_door(carla.VehicleDoor.All)
                return 0
        else:
            #print("No hack")
            return
            
            
    #while true; do cansend kcan4 000002f6#0000000000000100; done
    def control_light_seperate(self, vehicle, msg):
        data = self.light_message.decode(msg.data)
        #print("[DEBUG] Raw light control values:", data)
        light_mask = 0
        if data.get("LowBeam") == 1:
            light_mask |= carla.VehicleLightState.LowBeam
        if data.get("HighBeam") == 1:
            light_mask |= carla.VehicleLightState.HighBeam
        if data.get("Reverse") == 1:
            light_mask |= carla.VehicleLightState.Reverse
        if data.get("Brake") == 1:
            light_mask |= carla.VehicleLightState.Brake
        if data.get("RightBlinker") == 1:
            light_mask |= carla.VehicleLightState.RightBlinker
        if data.get("LeftBlinker") == 1:
            light_mask |= carla.VehicleLightState.LeftBlinker
        if data.get("Fog") == 1:
            light_mask |= carla.VehicleLightState.Fog
        if data.get("Interior") == 1:
            light_mask |= carla.VehicleLightState.Interior      

        # If LightOff is 1, override everything
        if data.get("LightOff") == 1:
            light_mask = carla.VehicleLightState.NONE

        if light_mask != 0 or data.get("LightOff") == 1:
            return vehicle.set_light_state(carla.VehicleLightState(light_mask))
        else:
            #print("ERROR sending light message: no valid bit set")
            return




    def control_wheelspeed_seperate1(self, vehicle, message):
        kcan4 = can.interface.Bus(bustype='socketcan', channel='vcan0')
        while True:
            try:
                msg = kcan4.recv()
                if msg is not None:
                    print(f"Listenner received message with CAN ID: {hex(msg.arbitration_id)}")
                    data = self.wheelspeed_message.decode(msg.data)
                    self.wheelspeed_message = data.get("Wheel_FL")
                    print(data)
                    return self.wheelspeed_message
                else:
                    print("Listener time out, no message received")
            except Exception as e:
                print(f"Exception in CAN Bus Listener: {e}")


    # Convert door message to carla vehicle control seperatly - For test only
    def control_door_seperate(self, vehicle):
        kcan4 = can.interface.Bus(bustype='socketcan', channel='kcan4')
        msg = kcan4.recv()
        data = self.door_message.decode(msg.data)
        if data.get("Door_FL") == 1 and data.get("Door_RL") == 1 and data.get("Door_FR") == 1 and data.get("Door_RR") == 1:
            print (vehicle)
            return vehicle.open_door(carla.VehicleDoor.All)
        if data.get("Door_FL") == 0 and data.get("Door_RL") == 0 and data.get("Door_FR") == 0 and data.get("Door_RR") == 0:
            print (vehicle)
            return vehicle.close_door(carla.VehicleDoor.All)

    

    # Convert Throttle message to carla vehicle control seperatly - For test only
    def control_throttle_seperate(self, control):
        vcan0 = can.interface.Bus(bustype='socketcan', channel='vcan0')
        msg = vcan0.recv()
        #print(f"Message information: {msg.data}")
        data = self.throttle_message.decode(msg.data)
        print(data)
        if data.get("Checksum_416") == 15:
            control.throttle = data.get("MovingForward")
            control.gear = data.get("MovingReverse")
            control.manual_gear_shift = True
        else:
            control.manual_gear_shift = False
        #print(control)
        return control
