import argparse
from threading import Thread
from can_attack import CANAttack
from uds_attack import UDSAttack

class Attacker:
    def __init__(self, can_interface):
        self.can_interface = can_interface
       # self.attack_type = attack_type
       # self.starttime = starttime

    def run_attacker(attack_type, starttime):
        starttime = self.starttime if self.starttime != 'random' else random.randint(1, 10)

        if attack_type in ['can_replay', 'can_dos', 'can_fuzzing']:
            attacker = CANAttacker(self.can_interface, starttime)
        elif attack_type in ['uds_replay', 'uds_fuzzing']:
            attacker = UDSAttacker(self.can_interface, starttime)
        attacker.execute_attack(attack_type, starttime)

    def attack_time_values(value):
        components = value.split(',')
        if len(components) != 4:
            raise argparse.ArgumentTypeError("attack-time must have four components: release time, duration, waiting time, period")

        def parse_component(comp):
            comp = comp.strip()
            if comp == 'random':
                return comp
            try:
                return int(comp)
            except ValueError:
                raise argparse.ArgumentTypeError(f"Invalid value '{comp}'. Must be an integer or 'random'")

        return tuple(parse_component(comp) for comp in components)



    def main(self):
        parser = argparse.ArgumentParser(description="Simulate vehicle security attacks.")
        parser.add_argument("--number-of-attackers", type=int, default=1, choices=range(0, 3))
        parser.add_argument("--location-to-goal", type=str, default="A", choices=["N", "A", "L", "P"])
        #goal need to be re-define, it is not logic yet
        parser.add_argument("--goals", type=str, default="subgoal_automotive", choices=["subgoal_it", "subgoal_automotive"])
        parser.add_argument("--attack-type", type=str, required=True, choices=["can-replay", "can-dos", "can-fuzzing", "uds-replay", "uds-fuzzing"])
        parser.add_argument("--windows-time-of-opportunity", nargs=2, default=("always", "always"))
        parser.add_argument("--starttime", type=int_or_random, default="random", help='Start time of the attack in seconds or "random"')
        parser.add_argument("--duration", type=int_or_random, default="random", description='Duration of one attack in seconds or "random"')
        parser.add_argument("--period", type=int_or_random, default="random", description='Period for next attack in seconds or "random"')
        parser.add_argument("--instance", type=int_or_random, default=0, description='Number of attack for each run in seconds or "random"')
        parser.add_argument("--attack-time", type=attack_time_values, default="0, 5, 5, 3", help='Comma-separated values for release time, duration, waiting time, period. Each can be an integer or "random".')


        args = parser.parse_args()

        if args.number_of_attackers < 0 or args.number_of_attackers > 3:
            logging.error("Number of attackers must be between 0 and 3.")
        return

        # Idea: using thread for multiple attacker - later

        # attackers = [Thread(target=run_attacker, args=(args,)) for _ in range(args.number_of_attackers)]
        # for attacker in attackers:
        #     attacker.start()
        # for attacker in attackers:
        #     attacker.join()


if __name__ == "__main__":
    attacker = Attacker("vcan0")
    attacker.main()
