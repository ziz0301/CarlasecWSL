import carla

def check_traffic_light_violation(vehicle):
    # Check if the vehicle is at a traffic light
    if vehicle.is_at_traffic_light():
        traffic_light = vehicle.get_traffic_light()

        # If the traffic light is red and the vehicle is moving, it's a violation
        if traffic_light.get_state() == carla.TrafficLightState.Red and vehicle.get_velocity().length() > 0:
            print("Traffic light violation: Red light crossed!")
            return True

    return False
