import carla
import time
import os

HOST = "192.168.160.1"
PORT = 2000
TIMEOUT = 60.0
WAIT_FOR_FRAMES = 10
SPAWN_DURATION = 60  # seconds
SAVE_DIR = "camera_output"

def wait_for_simulation_to_start(world, max_wait=10):
    print("Waiting for CARLA world to start ticking...")
    last_frame = world.get_snapshot().frame
    for i in range(max_wait):
        time.sleep(1)
        snapshot = world.get_snapshot()
        current_frame = snapshot.frame
        if current_frame != last_frame:
            print(f"World is running. Current frame: {current_frame}")
            return True
        print(f"...still frozen (frame {current_frame}), waiting...")
    print("World did not start ticking. Is CARLA paused?")
    return False

def main():
    try:
        client = carla.Client(HOST, PORT)
        client.set_timeout(TIMEOUT)

        world = client.get_world()

        if not wait_for_simulation_to_start(world, WAIT_FOR_FRAMES):
            return

        blueprint_library = world.get_blueprint_library()
        vehicle_bp = blueprint_library.find("vehicle.tesla.model3")
        spawn_points = world.get_map().get_spawn_points()
        if not spawn_points:
            print("No spawn points available.")
            return

        vehicle = world.spawn_actor(vehicle_bp, spawn_points[0])
        print("Vehicle spawned.")
        
        
        vehicle.set_autopilot(True) 

        # Prepare image save folder
        os.makedirs(SAVE_DIR, exist_ok=True)

        # Camera sensor
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '800')
        camera_bp.set_attribute('image_size_y', '600')
        camera_bp.set_attribute('fov', '90')

        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))  # hood position
        camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

        def save_image(image):
            filename = f"{SAVE_DIR}/frame_{image.frame}.png"
            image.save_to_disk(filename)
            print(f"Saved: {filename}")

        camera.listen(lambda image: save_image(image))

        print("Camera listening. Waiting for data...")

        time.sleep(SPAWN_DURATION)

    except Exception as e:
        print("Error:", e)

    finally:
        print("Cleaning up...")
        if 'camera' in locals():
            camera.stop()
            camera.destroy()
        if 'vehicle' in locals():
            vehicle.destroy()
        print("Done.")

if __name__ == "__main__":
    main()
