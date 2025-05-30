import random
import carla
import logging


vehicles_list = []
walkers_list = []
all_id = []

def spawn_random_vehicles(world, client, traffic_manager, number_of_vehicles, safe=False):
    synchronous_master = False
    SpawnActor = carla.command.SpawnActor
    SetAutopilot = carla.command.SetAutopilot
    FutureActor = carla.command.FutureActor

    blueprints = world.get_blueprint_library().filter('vehicle.*')
    if safe:
        blueprints = [x for x in blueprints if x.get_attribute('base_type') == 'car']
    blueprints = sorted(blueprints, key=lambda bp: bp.id)

    spawn_points = world.get_map().get_spawn_points()
    number_of_spawn_points = len(spawn_points)

    if number_of_vehicles < number_of_spawn_points:
        random.shuffle(spawn_points)
    elif number_of_vehicles > number_of_spawn_points:
        logging.warning('Requested %d vehicles, but could only find %d spawn points',number_of_vehicles, number_of_spawn_points)
        number_of_vehicles = number_of_spawn_points

    batch = []
    for transform in spawn_points[:number_of_vehicles]:
        blueprint = random.choice(blueprints)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        batch.append(SpawnActor(blueprint, transform)
                     .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))
    for response in client.apply_batch_sync(batch, synchronous_master):
        if response.error:
            print(f"RESPONSE_ERROR: {response.error}")
        else:
            vehicles_list.append(response.actor_id)
    # Set automatic vehicle lights update if specified
    all_vehicle_actors = world.get_actors(vehicles_list)
    for actor in all_vehicle_actors:
        traffic_manager.update_vehicle_lights(actor, True)


def spawn_random_walkers(world, client, number_of_walkers):
    percentagePedestriansRunning = 0.0      # how many pedestrians will run
    percentagePedestriansCrossing = 0.0     # how many pedestrians will walk through the road
    SpawnActor = carla.command.SpawnActor
    walker_bp_library = world.get_blueprint_library().filter('walker.pedestrian.*')

    # Spawn points
    spawn_points = []
    for _ in range(number_of_walkers):
        spawn_point = carla.Transform()
        loc = world.get_random_location_from_navigation()
        if loc is not None:
            spawn_point.location = loc
            spawn_points.append(spawn_point)

    # Spawn walkers
    batch = []
    walker_speed = []
    for spawn_point in spawn_points:
        walker_bp = random.choice(walker_bp_library)
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')
        if walker_bp.has_attribute('speed'):
            if (random.random() > percentagePedestriansRunning):
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
            else:
                walker_speed.append(walker_bp.get_attribute('speed').recommended_values[2])
        else:
            print("Walker has no speed")
            walker_speed.append(0.0)
        batch.append(SpawnActor(walker_bp, spawn_point))
    results = client.apply_batch_sync(batch, True)
    walker_speed2 = []
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list.append({"id": results[i].actor_id})
            walker_speed2.append(walker_speed[i])
    walker_speed = walker_speed2
    # 3. we spawn the walker controller
    batch = []
    walker_controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    for i in range(len(walkers_list)):
        batch.append(SpawnActor(walker_controller_bp, carla.Transform(), walkers_list[i]["id"]))
    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if results[i].error:
            logging.error(results[i].error)
        else:
            walkers_list[i]["con"] = results[i].actor_id
    # 4. we put together the walkers and controllers id to get the objects from their id
    for i in range(len(walkers_list)):
        all_id.append(walkers_list[i]["con"])
        all_id.append(walkers_list[i]["id"])
    all_actors = world.get_actors(all_id)
    #print(f"{len(all_actors)} actors, include: {all_actors}")
    #print(f"{len(walkers_list)} walker list, include: {walkers_list}")
    # 5. initialize each controller and set target to walk to (list is [controler, actor, controller, actor ...])
    # set how many pedestrians can cross the road
    world.set_pedestrians_cross_factor(percentagePedestriansCrossing)
    for i in range(0, len(all_id), 2):
        all_actors[i].start()
        all_actors[i].go_to_location(world.get_random_location_from_navigation())
        all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))

    print('Spawned %d vehicles and %d walkers, press Ctrl+C to exit.' % (len(vehicles_list), len(walkers_list)))
