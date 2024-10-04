import random
import math
import json


# function to calculate pend
def calculate_pend(epsilon):
    return math.ceil(math.log(epsilon) / math.log(0.5))

# Node class


class Node:
    def __init__(self, initial_value, vehicle_id, epsilon, n):
        self.value = initial_value
        self.phase = 0
        self.min_value = initial_value
        self.max_value = initial_value
        self.stable_rounds = 0
        self.bit_vector = [0] * n
        self.is_crashed = False
        self.final_output = False
        self.vehicle_id = vehicle_id
        self.epsilon = epsilon
        self.final_decision = None

    def receive(self, value, phase, sender, n):
        if self.is_crashed or self.final_output:
            return
        if value is None:
            print(
                f"Node {self.vehicle_id} received 'None' from Node {sender}. Ignoring...")
            return
        if phase > self.phase:
            self.phase = phase
            self.value = value
            self.reset_bit_vector(n)
        elif phase == self.phase and self.bit_vector[sender] == 0:
            self.bit_vector[sender] = 1
            self.store_value(value)

    def store_value(self, received_value):
        if received_value < self.min_value:
            self.min_value = received_value
        elif received_value > self.max_value:
            self.max_value = received_value

    def update_state(self, pend, n, T):
        if self.is_crashed or self.final_output:
            return
        if self.phase < pend:
            if sum(self.bit_vector) >= (n // 2 + 1):
                new_value = (self.min_value + self.max_value) / 2
                if abs(self.value - new_value) < self.epsilon:
                    self.stable_rounds += 1
                else:
                    self.stable_rounds = 0
                self.value = new_value
                self.phase += 1
                self.reset_bit_vector(n)
        if self.phase == pend and self.stable_rounds >= T:
            if not self.final_output:
                self.final_output = True
                self.final_decision = self.decide_final_output()

    def reset_bit_vector(self, n):
        self.bit_vector = [0] * n
        self.min_value = self.value
        self.max_value = self.value

    def decide_final_output(self):
        if self.value < 0.25 - self.epsilon:
            return 0
        elif self.value > 0.25 + self.epsilon:
            return 1
        else:
            return None

    def broadcast_final_decision(self, other_nodes, n):
        for node in other_nodes:
            if node != self and not node.is_crashed:
                node.receive(self.final_decision,
                             self.phase, self.vehicle_id, n)


#  function to simulate message loss
def message_lost(message_loss_probability):
    return random.random() < message_loss_probability

# Function to simulate controlled crash behavior


def crash_behavior(node, round_num, crashed_nodes, max_crashes):
    if len(crashed_nodes) < max_crashes and random.random() < 0.1:
        node.is_crashed = True
        crashed_nodes.append(node)
        print(f"Node {node.vehicle_id} crashed in round {round_num}.")

# Function to create nodes with binary values


def create_binary_nodes(ratio_one, epsilon, n):
    nodes = []
    num_ones = int(ratio_one * n)
    num_zeros = n - num_ones
    values = [1] * num_ones + [0] * num_zeros
    random.shuffle(values)
    for vehicle_id, value in enumerate(values):
        nodes.append(Node(value, vehicle_id, epsilon, n))
    return nodes

# Function to run the DAC algorithm simulation


def run_simulation(n, f, T, max_rounds, epsilon, ratio_one, message_loss_probability, simulation_id):
    message_loss_tracking = []
    phase_progression = []
    node_values_over_rounds = []
    stability_tracking = []

    # Initialize nodes
    nodes = create_binary_nodes(ratio_one, epsilon, n)
    max_crashes = f
    crashed_nodes = []
    pend = calculate_pend(epsilon)

    # Track rounds to reach consensus
    rounds_to_reach_consensus = 0

    for round_num in range(max_rounds):
        print(f"--- Simulation {simulation_id}, Round {round_num} ---")
        lost_messages = 0
        round_values = []

        for node in nodes:
            crash_behavior(node, round_num, crashed_nodes, max_crashes)

        received_states = {i: [] for i in range(n)}

        for i, node in enumerate(nodes):
            if node.is_crashed:
                continue
            if node.final_output:
                node.broadcast_final_decision(nodes, n)
                round_values.append(node.value)
                continue
            round_values.append(node.value)
            for j in range(n):
                if i != j:
                    if message_lost(message_loss_probability):
                        lost_messages += 1
                    else:
                        nodes[j].receive(node.value, node.phase, i, n)
                        received_states[j].append(node.value)

        node_values_over_rounds.append(round_values)
        round_phase_data = [
            {'Node': i, 'Phase': node.phase if not node.is_crashed else 'Crashed'} for i, node in enumerate(nodes)]
        phase_progression.append(round_phase_data)

        round_stability = [
            node.stable_rounds if not node.is_crashed else None for node in nodes]
        stability_tracking.append(round_stability)

        for i, node in enumerate(nodes):
            if node.is_crashed:
                continue
            node.update_state(pend, n, T)

        message_loss_tracking.append(lost_messages)

        if all(node.final_output or node.is_crashed for node in nodes):
            rounds_to_reach_consensus = round_num
            print("Consensus reached based on phase index!")
            break

    return {
        'simulation_id': simulation_id,
        'message_loss_tracking': message_loss_tracking,
        'phase_progression': phase_progression,
        'node_values_over_rounds': node_values_over_rounds,
        'stability_tracking': stability_tracking,
        'rounds_to_reach_consensus': rounds_to_reach_consensus
    }


# Predefined configurations for multiple runs
configurations = [
    {'N': 15, 'f': 2, 'message_loss_rate': 0.1,
        'initial_ratio': 0.8, 'epsilon': 0.01, 'max_rounds': 100},
    {'N': 20, 'f': 3, 'message_loss_rate': 0.1,
        'initial_ratio': 0.8, 'epsilon': 0.01, 'max_rounds': 100}
]

all_simulation_data = []

# Run simulations for each configuration
for config in configurations:
    num_repeats = int(input(
        f"How many times do you want to repeat the simulation for this configuration? "))
    for sim_id in range(1, num_repeats + 1):
        simulation_result = run_simulation(
            n=config['N'],
            f=config['f'],
            T=3,
            max_rounds=config['max_rounds'],
            epsilon=config['epsilon'],
            ratio_one=config['initial_ratio'],
            message_loss_probability=config['message_loss_rate'],
            simulation_id=f"{config['N']}_{sim_id}"
        )
        all_simulation_data.append(simulation_result)

# Save all results in a single file
with open('all_simulation_results.json', 'w') as f:
    json.dump(all_simulation_data, f, indent=4)

print("All simulation data saved to 'all_simulation_results.json'")
