import threading
import numpy as np
import carla
import random
import cv2
import os
import queue
import pickle
import time
import json
import subprocess
from PIL import Image, ImageDraw

from util.camera import CameraParameters, setup_camera, update_camera_params, setup_depth_camera
from util.weather import Weather, update_weather_params, modify_weather
from util.data import test_cases
from util.generate_traffic_specific import spawn_vehicle, spawn_walker
from util.image_adjusting import resize_image, print_adjust_parameters, image_cutting

path_locations = [
    carla.Location(x=-48.5, y=-45, z=0.6),        # Start point
    carla.Location(x=-48.5, y=100, z=0.6),
    carla.Location(x=-104, y=-20, z=0.6)       # Move straight along x-axis
]

def to_bgra_array(image):
    """Convert a CARLA raw image to a BGRA numpy array."""
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    return array

def to_rgb_array(image):
    """Convert a CARLA raw image to a RGB numpy array."""
    array = to_bgra_array(image)
    # Convert BGRA to RGB.
    array = array[:, :, :3]    # Extract RGB channels
    array = array[:, :, ::-1]  # Convert BGRA to RGB
    return array

def depth_to_array(image):
    """
    Convert an image containing CARLA encoded depth-map to a 2D array containing
    the depth value of each pixel normalized between [0.0, 1.0].
    """
    array = to_bgra_array(image)
    array = array.astype(np.float32)
    # Apply (R + G * 256 + B * 256 * 256) / (256 * 256 * 256 - 1).
    normalized_depth = np.dot(array[:, :, :3], [65536.0, 256.0, 1.0])
    normalized_depth /= 16777215.0  # (256.0 * 256.0 * 256.0 - 1.0)
    in_meters = 1000 * normalized_depth
    return in_meters

def save_case_to_json(case, case_number, output_dir):
    """Save the case parameters to a JSON file."""
    case_file_path = os.path.join(output_dir, f"case_{case_number + 1}.json")
    with open(case_file_path, 'w') as json_file:
        json.dump(case, json_file, indent=4)
    print(f"Saved case {case_number + 1} to {case_file_path}")

def reset_all_traffic_light(world):
    actors = world.get_actors()
    traffic_lights = [actor for actor in actors if isinstance(actor, carla.TrafficLight)]
    for traffic_light in traffic_lights:
        traffic_light.reset_group()
    print("All traffic lights have been reset to their initial state.")

def save_images_thread(image_pool, rgb_output, depth_output):
    """Independent thread to save image data to disk."""
    while True:
        if image_pool:
            rgb_image_np, depth_data, image_counter = image_pool.pop(0)
            
            # Save RGB image
            rgb_image_np_cutted = image_cutting(rgb_image_np)
            rgb_cutted_filename = f"{rgb_output}/{image_counter:06d}.png"
            cv2.imwrite(rgb_cutted_filename, cv2.cvtColor(rgb_image_np_cutted, cv2.COLOR_RGB2BGR))

            # Save depth image
            depth_cutted_data = image_cutting(depth_data)
            depth_cutted_filename = f"{depth_output}/{image_counter:06d}.npy"
            np.save(depth_cutted_filename, depth_cutted_data)
            cv2.imwrite(f"{depth_output}/{image_counter:06d}.png", depth_cutted_data)

            print(f"Image {image_counter} saved.")

        time.sleep(0.1)  # Delay to prevent excessive CPU usage

def main():
    # Load the following cars and walkers JSON data
    with open('car_info.json', 'r') as f:
        data = json.load(f)

    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    traffic_manager = client.get_trafficmanager()
    traffic_manager.set_global_distance_to_leading_vehicle(2.5)
    traffic_manager.set_respawn_dormant_vehicles(True)
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.no_rendering_mode = False
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)
    traffic_manager.set_synchronous_mode(True)

    blueprint_library = world.get_blueprint_library()
    blueprint_vehicle = world.get_blueprint_library().find('vehicle.tesla.model3')
    spawn_point = carla.Transform(carla.Location(x=-48.5, y=-45, z=0.6), carla.Rotation(yaw=90))

    for i, case in enumerate(test_cases):
 
        print(f"Starting test case {i + 1} with parameters: {case}")
        output_dir = "output_mono/test"
        os.makedirs(f"{output_dir}/test_case_{i+1}", exist_ok=True)

        # Save the case parameters to JSON
        save_case_to_json(case, i, f"{output_dir}/test_case_{i+1}")

        rgb_cutted_output = f"{output_dir}/test_case_{i + 1}/rgb_cutted"
        depth_cutted_output =f"{output_dir}/test_case_{i + 1}/depth_cutted"
        os.makedirs(rgb_cutted_output, exist_ok=True)
        os.makedirs(depth_cutted_output, exist_ok=True)

        # Instantiate parameter objects
        camera_params = CameraParameters()
        weather_params = Weather(world)

        # Update camera parameters
        update_camera_params(camera_params, case)

        # Update weather parameters
        update_weather_params(weather_params, case)

        vehicles = []
        walkers = []
        for vehicle_data in data['vehicles_info']:
            vehicle = spawn_vehicle(world, vehicle_data)
            path = []
            dest_location = carla.Location(
                x=vehicle_data['destination']['x'],
                y=vehicle_data['destination']['y'],
                z=0.6
            )
            path.append(dest_location)
            traffic_manager.random_left_lanechange_percentage(vehicle,0)
            traffic_manager.random_right_lanechange_percentage(vehicle,0)
            traffic_manager.auto_lane_change(vehicle, False)
            traffic_manager.set_path(vehicle,path)

            vehicles.append(vehicle)
        for walker_data in data['walkers_info']:
            walker = spawn_walker(world, walker_data)
            walkers.append(walker)
        for vehicle in vehicles:
            vehicle.set_autopilot(True, traffic_manager.get_port())  # Enable autopilot for vehicles

        for walker in walkers:
            controller_bp = world.get_blueprint_library().find('controller.ai.walker')
            controller = world.spawn_actor(controller_bp,carla.Transform(),attach_to = walker)
            controller.start()
            controller.go_to_location(world.get_random_location_from_navigation())
            controller.set_max_speed(1.5)
        print("All following vehicles and walkers are generated.")

        vehicle = world.spawn_actor(blueprint_vehicle, spawn_point)
        reset_all_traffic_light(world)
        vehicle.set_autopilot(True)
        traffic_manager.random_left_lanechange_percentage(vehicle,0)
        traffic_manager.random_right_lanechange_percentage(vehicle,0)
        traffic_manager.auto_lane_change(vehicle, False)
        traffic_manager.set_path(vehicle,path_locations)

        # Setup RGB camera
        print("----------CAMERA----------")
        rgb_camera =  setup_camera(world, vehicle, camera_params)

        # Setup depth camera
        print("-------DEPTHCAMERA--------")
        depth_camera =  setup_depth_camera(world, vehicle, camera_params)

        # Modify weather parameters
        modify_weather(world, weather_params)

        print_adjust_parameters(case[14])
        time.sleep(1)

        rgb_queue = queue.Queue()
        depth_queue = queue.Queue()
        rgb_camera.listen(rgb_queue.put)
        depth_camera.listen(depth_queue.put)

        start_time = time.time()  
        #duration = 60  Capture images for a fixed duration
        image_counter = 1

         # Start the image saving thread
        image_pool = []
        save_thread = threading.Thread(target=save_images_thread, args=(image_pool, rgb_cutted_output, depth_cutted_output))
        save_thread.daemon = True
        save_thread.start()

        # waiting cars to drive 
        try:
            while True:
                world.tick()  

                '''
                if time.time() - start_time > duration:
                    break
                '''
                if image_counter > 160:
                    break
                
                 # Retrieve RGB and depth images           
                try:
                    rgb_image = rgb_queue.get_nowait()
                    if rgb_image:
                        rgb_image_np = to_rgb_array(rgb_image)
                        rgb_image_np = resize_image(rgb_image_np, case[14])

                        depth_image = depth_queue.get_nowait()
                        if depth_image:
                            depth_data = depth_to_array(depth_image)
                            depth_data = resize_image(depth_data, case[14])

                             # Add images to the pool for saving
                            image_pool.append((rgb_image_np, depth_data, image_counter))
                            image_counter += 1
                except queue.Empty:
                    pass 
                    
        finally:
            rgb_camera.stop()
            depth_camera.stop()
            vehicle.destroy()
            print("Main car destroyed")

            rgb_camera.destroy()
            depth_camera.destroy()
            print("Camera destroyed")

            for vehicle in vehicles:
                vehicle.destroy()
            for walker in walkers:
                walker.destroy()
            print("Following cars and walkers destroyed")

            world.tick()

            print(f"Completed test case {i + 1}\n")
            print("==============================")

            time.sleep(5)

if __name__ == "__main__":
    main()

