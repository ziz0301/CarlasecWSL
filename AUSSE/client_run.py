#!/usr/bin/env python

# Copyright (c) 2018 Intel Labs.
# authors: German Ros (german.ros@intel.com)
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""Example of automatic vehicle control from client side."""

from __future__ import print_function

import argparse
import collections
import datetime
import glob
import logging
import math
import os
import numpy.random as random
import re
import sys
import weakref
import time
import subprocess
import threading
import can

try:
    import pygame
    from pygame.locals import KMOD_CTRL
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_q
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError(
        'cannot import numpy, make sure numpy package is installed')

# ==============================================================================
# -- Find CARLA module ---------------------------------------------------------
# ==============================================================================
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- Add PythonAPI for release mode --------------------------------------------
# ==============================================================================
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/carla')
except IndexError:
    pass

import carla
from carla import ColorConverter as cc
# Import Agent type
from agents.navigation.behavior_agent import BehaviorAgent  # pylint: disable=import-error
from agents.navigation.basic_agent import BasicAgent  # pylint: disable=import-error
from agents.navigation.constant_velocity_agent import ConstantVelocityAgent  # pylint: disable=import-error

# Import world setup
from world_setup.hud import HUD
from world_setup.world import World
from world_setup.spawn_random_actors import spawn_random_vehicles, spawn_random_walkers
from world_setup.utils import get_vehicle_locations, get_walker_locations, find_spawn_point, get_vehicle_and_walker_info, destroy_all_vehicles, destroy_all_walkers


# Import benchmark tools
from benchmark_tools.traffic_rule_infractions import CountOffRoadViolation, CountRunningRedLightViolation, CountRunningStopViolation
from benchmark_tools.data_exporter import DataExporter
from benchmark_tools.safety_metrics import SafetyMetrics


# Import invehicle network and protocol as Scenario
from invehicle_network.ivn.scenario import Scenario
from attacker.attackprofile import Attacker
from attacker.attackerhelper import start_dbus, start_gnome_terminal, stop_dbus


weather_presets = {
    "default": carla.WeatherParameters.ClearNoon,
    "night": carla.WeatherParameters(cloudiness=10.0, precipitation=0.0, sun_altitude_angle=-10.0),
    "rainynight": carla.WeatherParameters(cloudiness=90.0, precipitation=80.0, sun_altitude_angle=-15.0),
}


# ==============================================================================
# -- KeyboardControl -----------------------------------------------------------
# ==============================================================================


class KeyboardControl(object):
    def __init__(self, world):
        world.hud.notification("Press 'H' or '?' for help.", seconds=4.0)

    def parse_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYUP:
                if self._is_quit_shortcut(event.key):
                    return True

    @staticmethod
    def _is_quit_shortcut(key):
        """Shortcut for quitting"""
        return (key == K_ESCAPE) or (key == K_q and pygame.key.get_mods() & KMOD_CTRL)


# ==============================================================================
# -- Game Loop ---------------------------------------------------------
# ==============================================================================


def game_loop(args, filename, scenario):
    """
    Main loop of the simulation. It handles updating all the HUD information,
    ticking the agent and, if needed, the world.
    """

    pygame.init()
    pygame.font.init()
    world = None
    distances_log = []
    car_is_blocked = False
    fully_completed = False
    total_time = 0
    current_vector = None



    try:
        if args.seed:
            random.seed(args.seed)

        client = carla.Client(args.host, args.port)
        client.set_timeout(2.0)
        traffic_manager = client.get_trafficmanager()
        sim_world = client.get_world()

        ###VEL_Spawn vehicles and walker based on the user argument
        #spawn_random_vehicles(sim_world, client, traffic_manager, args.number_of_vehicles)
        #spawn_random_walkers(sim_world, client, args.number_of_walkers)

        ###VEL_Get list of vehicle and walkers location to note
        get_vehicle_locations(sim_world)
        get_walker_locations(sim_world)

        
        if args.sync:
            settings = sim_world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05
            sim_world.apply_settings(settings)
            traffic_manager.set_synchronous_mode(True)

        display = pygame.display.set_mode(
            (args.width, args.height),
            pygame.HWSURFACE | pygame.DOUBLEBUF)

        hud = HUD(args.width, args.height, filename)
        world = World(client.get_world(), hud, args)
        controller = KeyboardControl(world)
        
        
        ###VEL_Declare Scenario
        #scenario = Scenario()
        
        ###VEL_Declare DataExporter and SafetyMetrics
        data_exporter = DataExporter()
        safety_metrics = SafetyMetrics()
        attacker = Attacker()

        if args.agent == "Basic":
            agent = BasicAgent(world.player, 30)
            agent.follow_speed_limits(True)
        elif args.agent == "Constant":
            agent = ConstantVelocityAgent(world.player, 30)
            ground_loc = world.world.ground_projection(world.player.get_location(), 5)
            if ground_loc:
                world.player.set_location(ground_loc.location + carla.Location(z=0.01))
            agent.follow_speed_limits(True)
        elif args.agent == "Behavior":
            agent = BehaviorAgent(world.player, behavior=args.behavior)

        ###VEL_Set the spawnpoint based on the argument that user input
        if world.end_pos:
            destination = world.end_pos.location
            agent.set_destination(destination)
        else:
            spawn_points = world.map.get_spawn_points()
            destination = random.choice(spawn_points).location
            agent.set_destination(destination)

        ###VEL_Calculate the distance from start to destination
        #calc_distance = safety_metrics._calculate_distance(world.start_pos.location, destination)

        clock = pygame.time.Clock()

        ###VEL_Set the in-game time to 1
        start_time = time.time()
        running_time = 0



        ###VEL_Start recording and save the file as filename
        filename_record = filename + "_record.rec"
        client.start_recorder(filename_record)

        ###VEL_Setting up the couting of violations
        countoffroad = CountOffRoadViolation(world.player, world.map)
        countrunningredlight = CountRunningRedLightViolation(world.player, world.map, sim_world)
        countrunningstop = CountRunningStopViolation(world.player, world.map, sim_world)

        ###VEL_Setting up the gateway continuous listenning
        scenario.setup_common_environment()

        ###VEL_Setting up the UDS message
        vehicle = world.player
        control = carla.VehicleControl()
        scenario.create_uds_hack_scenario("diag_service","handle_uds_message", control, vehicle, carla.VehicleDoor)


        ###VEL_ATTACKER
        #attacker.run_attack('05310101A964', '05310201A964')
        #Setup the DBUS environment
        #if (args.attacker == True):
        #subprocess.run(['gnome-terminal', '--','bash', '--init-file', 'attacker.sh'])

        #Get red light to much faster
        actor_list = client.get_world().get_actors()
        for actor_ in actor_list:
            if isinstance(actor_, carla.TrafficLight):
                actor_.set_red_time(1.0)
                actor_.set_green_time (5.0)
                actor_.set_state(carla.TrafficLightState.Green)

        while True:
            clock.tick()
            if args.sync:
                world.world.tick()
            else:
                world.world.wait_for_tick()
            if controller.parse_events():
                return

            world.tick(clock)
            world.render(display)
            pygame.display.flip()

            ###VEL test threading
            #active_thread = threading.active_count()
            #print(f"Number of active thread is {active_thread}")

            if args.sniff == True:
                scenario.create_dump_message_scenario(world)

            #control = carla.VehicleControl()
            #control = hud.can.control_throttle_seperate(control)
            #world.player.apply_control(control)

            ###VEL_Couting the violation
            countoffroad.update()
            countrunningredlight.update()
            countrunningstop.update()



            ###VEL_Update distance every tick
            current_location = world.player.get_location()
            safety_metrics.update_distance(current_location)
            current_distance = safety_metrics.total_distance_meters
            distances_log.append(current_distance)
            

            ###VEL_Check if car block, if the car stop for more than stop_threshold (tick), then exit the in-game_loop
            stop_threshold = 3000
            if len(distances_log) > 100:
                if safety_metrics.is_car_blocked(distances_log, stop_threshold):
                    fully_completed = False
                    end_time = time.time()
                    total_time = end_time - start_time
                    print("Car is blocked. Terminating this run.")
                    break

            if agent.done():
                if args.loop:
                    agent.set_destination(random.choice(spawn_points).location)
                    world.hud.notification("Target reached", seconds=4.0)
                    fully_completed = True
                    print("The target has been reached, searching for another target")
                else:
                    ###VEL_Count the total distance that the car has run
                    print("---------------------- RESULTS --------------------")
                    total_distance_km = safety_metrics.get_total_distance_km()
                    print(f"Total distance traveled: {total_distance_km} km")
                    ###VEL_Count the total in-game time that the car run
                    end_time = time.time()
                    total_time = end_time - start_time
                    fully_completed = True
                    print(f"Total time taken: {total_time} seconds")
                    print("The target has been reached, stopping the simulation")
                    break





            ###VEL NORMAL AUTONOMOUS RUNNING - USE FOR NORMAL RUN AND UDS ATTACK
            #agent.update_information(world)
            control_auto = agent.run_step()
            control_auto.manual_gear_shift = False
            world.player.apply_control(control_auto)


            '''
            ###VEL TEST PRIORITY QUEUE
            scenario.inspect_priority_queue()
            control_auto = agent.run_step()
            control_auto.manual_gear_shift = False
            world.player.apply_control(control_auto)
            '''

            '''
            ###VEL CONTROL CAR STOP WHEN THERE IS A DOS ATTACK
            control = carla.VehicleControl()
            kcan_process = scenario.process_kcan_messages(world.player, control)
            if (scenario.dos == True):
                world.player.apply_control(kcan_process)
            else:
                control_auto = agent.run_step()
                control_auto.manual_gear_shift = False
                world.player.apply_control(control_auto)
            '''


            ###VEL CAN control everything here
            control = carla.VehicleControl()
            vcan_process = scenario.process_vcan_messages(control)
            kcan_process = scenario.process_kcan_messages(world.player, control)
            if(scenario.door_open == False):
                safety_metrics.log_door_status(filename, 'Close')
            else: 
                safety_metrics.log_door_status(filename, 'Open')

            if(scenario.kcan_dos == True):
                print(f"control_value:{kcan_process}")
                world.player.apply_control(kcan_process)
                break
            if vcan_process != None:
                #print(f"control_value:{vcan_process}")
                world.player.apply_control(vcan_process)
            else:
                control_auto = agent.run_step()
                #print(f"Control: {control_auto}")
                control_auto.manual_gear_shift = False
                world.player.apply_control(control_auto)


            #control_value = scenario.process_can_messages(carla.VehicleControl())
            #print(f"control: {control}")
            #if control == None:
            #    control1 = agent.run_step()
            #    control1.manual_gear_shift = False
            #    world.player.apply_control(control1)
            #else:
            #    world.player.apply_control(control)

    ###Printing and resetting after the car has reach the destination
    finally:
        num_of_vehicles = sim_world.get_actors().filter('vehicle.*')
        num_of_walkers = sim_world.get_actors().filter('walker.pedestrian.*')
        if world is not None:
            settings = world.world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            world.world.apply_settings(settings)
            traffic_manager.set_synchronous_mode(True)
            get_door_count = scenario.get_door_count()
            ###VEL_Count lane intersect and collision during the run
            #count_lane_invasion = world.lane_invasion_sensor.count_lane_intersect
            #count_collision = world.collision_sensor.count_all_collisions
            ###VEL_Calculate the percentage of violation
            #percentage_lane_invasion = safety_metrics.calculate_percentage_lane_invasion(count_lane_invasion)
            #percentage_light_violation = safety_metrics.calculate_percentage_traffic_light_violations(countrunningredlight.get_violation_count())
            #percentage_collision = safety_metrics.calculate_percentage_collision(count_collision)
            """
            VEL_Export into file
            """

            ###VEL_Infraction log exporter process
            data_exporter.infractions["Collisions with layout"].extend(world.collision_sensor.full_history["Collisions with layout"])
            data_exporter.infractions["Collisions with pedestrians"].extend(world.collision_sensor.full_history["Collisions with pedestrians"])
            data_exporter.infractions["Collisions with vehicles"].extend(world.collision_sensor.full_history["Collisions with vehicles"])
            data_exporter.infractions["Red lights infractions"].extend(countrunningredlight.infractions["Red lights infractions"])
            data_exporter.infractions["Stop sign infractions"].extend(countrunningstop.infractions["Stop sign infractions"])
            data_exporter.infractions["Off-road infractions"].extend(countoffroad.infractions["Off-road infractions"])
            print("Infractions:")
            for key, value in data_exporter.infractions.items():
                print(f"{key}: {value}")
            
           
            ###VEL_Information exporter process
            average_speed = safety_metrics.calculate_average_speed(safety_metrics.total_distance_meters, total_time)
            data_exporter.results["filename"] = filename
            data_exporter.results['weather']= args.weather
            data_exporter.results['number_of_vehicles']= len(num_of_vehicles)
            data_exporter.results['number_of_walker']= len(num_of_walkers)
            data_exporter.results['ego_vehicle']= world.player.type_id
            data_exporter.results['start_positon']= world.start_pos.location
            if world.end_pos != None:
                data_exporter.results['destination_position']= world.end_pos.location
            else:
                data_exporter.results['destination_position']= 'Do not set the end'
            data_exporter.results['fully_completed']= fully_completed
            data_exporter.results['total_time_run']= total_time
            data_exporter.results['total_metre_run']= safety_metrics.total_distance_meters
            data_exporter.results['average_speed']= average_speed
            data_exporter.results['count_collision_others']= world.collision_sensor.count_collision_others
            data_exporter.results['count_collision_pedestrians']= world.collision_sensor.count_collision_pedestrians
            data_exporter.results['count_collision_vehicles']= world.collision_sensor.count_collision_vehicles
            data_exporter.results['score_collision_others']= world.collision_sensor.score_collision_others
            data_exporter.results['score_collision_pedestrians']= world.collision_sensor.score_collision_pedestrians
            data_exporter.results['score_collision_vehicles']= world.collision_sensor.score_collision_vehicles
            data_exporter.results['count_off_road']= countoffroad.get_offroad_count()
            data_exporter.results['count_red_light_violation']= countrunningredlight.get_violation_count()
            data_exporter.results['count_stop_sign_violation']= countrunningstop.get_violation_count()
            data_exporter.results['count_stop_sign_violation']= countrunningstop.get_violation_count()
            data_exporter.results['door_open']= get_door_count

            print("Results:")
            for key, value in data_exporter.results.items():
                print(f"{key}: {value}")


            ###VEL_Get safety analysis
            safety_analyse = safety_metrics.safety_analysis(data_exporter.results)
            ###VEL_Export to simplistic_result
            data_exporter.export_simplistic_result(filename, safety_analyse, data_exporter.results, data_exporter.infractions)

            ###VEL_Export to detailed_result
            info = client.show_recorder_file_info(filename_record, True)
            collisions = client.show_recorder_collisions(filename_record, 'h', 'a')
            location_info = get_vehicle_and_walker_info(sim_world)
            record_collision = world.collision_sensor.get_collision_history()
            data_exporter.export_detailed_result(
                filename,
                safety_analyse,
                data_exporter.results,
                data_exporter.infractions,
                record_collision,
                location_info,
                info,
                collisions)

            
            world.destroy()

        pygame.quit()
        
        # Properly stop all threads
        scenario.stop_event.set()        
        scenario.listener_kcan4_thread.join()        
        scenario.listener_vcan0_thread.join()        
        scenario.udsserver_thread.join()        
        if scenario.virtualshell_thread is not None:
            scenario.virtualshell_thread.join()           
        if scenario.listener_virtualshell_thread is not None:
            scenario.listener_virtualshell_thread.join()
        
       

        print(f"Debug: kcan thread {scenario.listener_kcan4_thread}")
        print(f"Debug: vcan thread {scenario.listener_vcan0_thread}")
        print(f"Debug: uds thread {scenario.udsserver_thread}")
        print(f"Debug: virtualshell thread {scenario.virtualshell_thread}")
        print(f"Debug: listener virtualshell thread {scenario.listener_virtualshell_thread}")
        live_thread_count = len(threading.enumerate())
        print(f"Number of thread that is still alive {live_thread_count}")
        #pygame.quit()
# ==============================================================================
# -- main() --------------------------------------------------------------
# ==============================================================================


def main():
    """Main method"""
    argparser = argparse.ArgumentParser(description='CARLA Automatic Control Client')
    argparser.add_argument('--verbose',action='store_true',dest='debug',help='Print debug information')
    argparser.add_argument('--host',metavar='H',default='192.168.160.1',help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument('--port',metavar='P',default=2000,type=int,help='TCP port to listen to (default: 2000)')
    argparser.add_argument('--res',metavar='WIDTHxHEIGHT',default='889x500',help='Window resolution (default: 1280x720)')
    argparser.add_argument('--sync',action='store_true',help='Synchronous mode execution')
    argparser.add_argument('--filter',metavar='PATTERN',default='vehicle.mercedes.coupe_2020',help='Actor filter (default: "vehicle.*")')
    argparser.add_argument('--generation',metavar='G',default='2',help='restrict to certain actor generation (values: "1","2","All" - default: "2")')
    argparser.add_argument('--loop',action='store_true',dest='loop',help='Sets a new random destination upon reaching the previous one (default: False)')
    argparser.add_argument('--agent', type=str,choices=["Behavior", "Basic", "Constant"],help="select which agent to run",default="Basic")
    argparser.add_argument('--behavior', type=str,choices=["cautious", "normal", "aggressive"],help='Choose one of the possible agent behaviors (default: normal) ',default='normal')
    argparser.add_argument('--seed',help='Set seed for repeating executions (default: None)',default=None,type=int)
    #Adding argument for experiment
    argparser.add_argument('--weather', default='Default', help='Set of weather type to benchmark, by default "Default"')
    argparser.add_argument('--number-of-vehicles',metavar='N',default=0,type=int,help='Number of vehicles (default: 10)')
    argparser.add_argument('--number-of-walkers',metavar='W',default=0,type=int,help='Number of walkers (default: 10)')
    argparser.add_argument('--spawnpos', default='', help='comma-separated list of spawn point indices, e.g. "1,5"')
    argparser.add_argument('--autoloop', type=int, default=1, help='Number of times to run the experiment')
    argparser.add_argument('--basename', default='benign', help='Base name for saving file')
    argparser.add_argument('--attacker', default='false', help='There is a shell to inject attacker message')
    argparser.add_argument('--sniff', action='store_true', help='Dump vehicle CAN message')

    args = argparser.parse_args()
    args.width, args.height = [int(x) for x in args.res.split('x')]   
        
        
    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('Listening to server %s:%s', args.host, args.port)

    print(__doc__)

    
    stop_event = threading.Event()
    #Set file name for each run to export data to file:
    if args.basename:
        filename = args.basename

    for run in range(args.autoloop):
        runcount = run + 1
        filename_count = filename + "_" + str(runcount)
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'Run {run + 1} start at {start_time}')

        try:      
            args = argparser.parse_args()
            args.width, args.height = [int(x) for x in args.res.split('x')]
            scenario = Scenario(stop_event)
            game_loop(args, filename_count, scenario)
            
        except KeyboardInterrupt:
            scenario.stop_event.set()
            scenario.listener_kcan4_thread.join()
            scenario.listener_vcan0_thread.join()
            scenario.udsserver_thread.join()
            scenario.virtualshell_thread.join()
            scenario.listener_virtualshell_thread.join()
            print('\nCancelled by user. Bye!')
            break

        end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'Run {run + 1} end at {end_time}')


if __name__ == '__main__':
    main()
