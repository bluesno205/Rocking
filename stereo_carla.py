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
import copy

from camera import CameraParameters, setup_camera, update_camera_params, setup_depth_camera
from weather import Weather, update_weather_params, modify_weather
from data import test_cases
from generate_traffic_specific import spawn_vehicle, spawn_walker
from image_adjusting import resize_image, print_adjust_parameters, image_cutting

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
    array = array[:, :, :3]
    array = array[:, :, ::-1]
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

        output_path = 'output_stereo/test_stereo/'
        output_dir = f"{output_path}/test_case_{i + 1}"
        os.makedirs(output_dir, exist_ok=True)
        save_case_to_json(case, i, output_dir)

        offset_ranges = [0.1, 0.2, 0.3, 0.4, 0.5]  # different offset(parameter:baseline)
        queue_dict = {}

        for offset in offset_ranges:
            rgb_output = f"{output_path}/test_case_{i + 1}/rgb_{offset}"
            depth_output = f"{output_path}/test_case_{i + 1}/depth_{offset}"
            os.makedirs(rgb_output, exist_ok=True)
            os.makedirs(depth_output, exist_ok=True)

            queue_dict[offset] = {
                "rgb_left": queue.Queue(),
                "depth_left": queue.Queue(),
                "rgb_right": queue.Queue(),
                "depth_right": queue.Queue()
            }

        # Instantiate parameter objects
        weather_params = Weather(world)

        # Update weather parameters
        update_weather_params(weather_params, case)

        # Modify weather parameters
        modify_weather(world, weather_params)

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

        left_cameras = []
        right_cameras = []

        for offset in offset_ranges:
            camera_params_left = CameraParameters()
            camera_params_right = CameraParameters()

            case_left = copy.deepcopy(case)
            case_right = copy.deepcopy(case)

            case_left[1] = case[1] - offset
            case_right[1] = case[1] + offset
            print(case_left)
            print(case_right)

            # Update camera parameters
            update_camera_params(camera_params_left, case_left)
            update_camera_params(camera_params_right, case_right)

            print("----------CAMERA----------")
            print(f'--offset:{offset}-left-RGB--')
            rgb_camera_left =  setup_camera(world, vehicle, camera_params_left)
            print(f'--offset:{offset}-right-RGB--')
            rgb_camera_right =  setup_camera(world, vehicle, camera_params_right)

            print("-------DEPTHCAMERA--------")
            print(f'--offset:{offset}-left-DEPTH--')
            depth_camera_left =  setup_depth_camera(world, vehicle, camera_params_left)
            print(f'--{offset}-right-DEPTH--')
            depth_camera_right =  setup_depth_camera(world, vehicle, camera_params_right)

            left_cameras.append((rgb_camera_left, depth_camera_left))
            right_cameras.append((rgb_camera_right, depth_camera_right))

            rgb_camera_left.listen(queue_dict[offset]["rgb_left"].put)
            depth_camera_left.listen(queue_dict[offset]["depth_left"].put)
            rgb_camera_right.listen(queue_dict[offset]["rgb_right"].put)
            depth_camera_right.listen(queue_dict[offset]["depth_right"].put)

        print_adjust_parameters(case[14])

        time.sleep(1)

        start_time = time.time()  
        #duration = 60  
        image_counter = 1

        try:
            while True:

                world.tick() 
                '''
                if time.time() - start_time > duration:
                    break
                '''
                if image_counter > 160:
                    break
                
                for offset in offset_ranges:
                    try:
                        left_rgb_image = queue_dict[offset]["rgb_left"].get_nowait()
                        left_depth_image = queue_dict[offset]["depth_left"].get_nowait()

                        if left_rgb_image:
                            
                            left_rgb_image_np = to_rgb_array(left_rgb_image)
                            left_rgb_image_np = resize_image(left_rgb_image_np, case[14])
                            left_rgb_image_np_cutted = image_cutting(left_rgb_image_np)
                            rgb_output_left = os.path.join(f"{output_path}/test_case_{i + 1}/rgb_{offset}", f'%06d_{offset}_left.png')
R))
                            
                        if left_depth_image:
                            
                            left_depth_data = depth_to_array(left_depth_image)
                            left_depth_data = resize_image(left_depth_data, case[14])
                            left_depth_cutted_data = image_cutting(left_depth_data)
                            depth_output_left = os.path.join(f"{output_path}/test_case_{i + 1}/depth_{offset}", f'%06d_{offset}_left.npy')
                            depth_output_left_png = os.path.join(f"{output_path}/test_case_{i + 1}/depth_{offset}", f'%06d_{offset}_left.png')
                            
                    except queue.Empty:
                        pass  
                        
                    try:
                        right_rgb_image = queue_dict[offset]["rgb_right"].get_nowait()
                        right_depth_image = queue_dict[offset]["depth_right"].get_nowait()

                        if right_rgb_image:
                            
                            right_rgb_image_np = to_rgb_array(right_rgb_image))
                            right_rgb_image_np = resize_image(right_rgb_image_np, case[14])
                            right_rgb_image_np_cutted = image_cutting(right_rgb_image_np)
                            rgb_output_right = os.path.join(f"{output_path}/test_case_{i + 1}/rgb_{offset}", f'%06d_{offset}_right.png')
                           
                        if right_depth_image:
                            
                            right_depth_data = depth_to_array(right_depth_image)
                            right_depth_data = resize_image(right_depth_data, case[14])
                            right_depth_cutted_data = image_cutting(right_depth_data)
                            depth_output_right = os.path.join(f"{output_path}/test_case_{i + 1}/depth_{offset}", f'%06d_{offset}_right.npy')
                            depth_output_right_png = os.path.join(f"{output_path}/test_case_{i + 1}/depth_{offset}", f'%06d_{offset}_right.png')
                            if offset == offset_ranges[-1]:
                                image_counter += 1
                            
                    except queue.Empty:
                        pass 

        finally:
            vehicle.destroy()
            print("Main car destroyed")

            for rgb_camera_left, depth_camera_left in left_cameras:
                rgb_camera_left.stop()
                depth_camera_left.stop()
            for rgb_camera_right, depth_camera_right in right_cameras:
                rgb_camera_right.stop()
                depth_camera_right.stop()

            for rgb_camera_left, depth_camera_left in left_cameras:
                rgb_camera_left.destroy()
                depth_camera_left.destroy()
            for rgb_camera_right, depth_camera_right in right_cameras:
                rgb_camera_right.destroy()
                depth_camera_right.destroy()

            print("Cameras destroyed")

            for vehicle in vehicles:
                vehicle.destroy()
            for walker in walkers:
                walker.destroy()
            print("Following cars and walkers destroyed")

            world.tick()

            print(f"Completed test case {i + 1}\n")
            print("==============================")
            print(f"image_counter:{image_counter}")
            time.sleep(5)

if __name__ == "__main__":
    main()

