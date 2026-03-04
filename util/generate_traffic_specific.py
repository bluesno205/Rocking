import carla
import json
import time
import threading



def spawn_vehicle(world, vehicle_data):
    """Spawn a vehicle in the CARLA world based on the provided data."""
    # Create a blueprint for the vehicle
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.find(vehicle_data['vehicle_model'])

    # Get the spawn location and rotation
    spawn_location = carla.Location(
        x=vehicle_data['position']['x'],
        y=vehicle_data['position']['y'],
        z=0.5
    )
    spawn_rotation = carla.Rotation(
        pitch=vehicle_data['orientation']['pitch'],
        yaw=vehicle_data['orientation']['yaw'],
        roll=vehicle_data['orientation']['roll']
    )
    # print(vehicle_data['vehicle_model'])
    # Spawn the vehicle
    vehicle = world.spawn_actor(vehicle_bp, carla.Transform(spawn_location, spawn_rotation))
    return vehicle

def spawn_walker(world, walker_data):
    """Spawn a walker in the CARLA world based on the provided data."""
    blueprint_library = world.get_blueprint_library()
    walker_bp = blueprint_library.find(walker_data['walker_name'])

    # Get the spawn location and rotation
    spawn_location = carla.Location(
        x=walker_data['position']['x'],
        y=walker_data['position']['y'],
        z=0.6
    )
    spawn_rotation = carla.Rotation(
        pitch=walker_data['orientation']['pitch'],
        yaw=walker_data['orientation']['yaw'],
        roll=walker_data['orientation']['roll']
    )
    # Spawn the walker
    walker = world.spawn_actor(walker_bp, carla.Transform(spawn_location, spawn_rotation))
    return walker

def main():
    # Load the JSON data
    with open('car_info.json', 'r') as f:
        data = json.load(f)

    # Initialize CARLA client
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

    vehicles = []

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

    # Spawn all walkers
    walkers = []
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

    print("All following vehicles and generated.")

    # Start time
    start_time = time.time()

    # Run the loop for 45 seconds
    while time.time() - start_time < 15:
        world.tick()

    # Step 2: Destroy all vehicles and walkers
    for vehicle in vehicles:
        vehicle.destroy()
    for walker in walkers:
        walker.destroy()

    world.tick()

    print("All following vehicles and walkers have been deleted.")


if __name__ == "__main__":
    main()

