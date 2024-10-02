import random
import math
import json


# Configuration Parameters
n = 10  # Total number of nodes (vehicles)
f = 1  # Maximum number of crash-faulty nodes (controlled)
T = 3  # Number of stable rounds required before finalizing decision
max_rounds = 50  # Maximum rounds to reach consensus
epsilon = 0.01  # Precision for approximate consensus
value_range = (0, 1)  # Range for node values

ratio_one = 0  # Ratio of nodes initialized to value 1
message_loss_probability = 0.1  # Probability of message loss (10%)
message_loss_tracking = []
phase_progression = []  # Track phase evolution of each node per round
node_values_over_rounds = []  # To track node values over each round
stability_tracking = []  # To track stability per node per round


def calculate_pend(epsilon):
    return math.ceil(math.log(epsilon) / math.log(0.5))

# Node class


class Node:
    def __init__(self, initial_value, vehicle_id, epsilon):
        self.value = initial_value
        self.phase = 0  # Phase index starts at 0
        self.min_value = initial_value
        self.max_value = initial_value
        self.stable_rounds = 0  # Track number of stable rounds
        self.bit_vector = [0] * n  # Tracks received messages from nodes
        self.is_crashed = False  # Indicates if the node has crashed
        self.final_output = False  # Indicates if the node has reached pend
        self.vehicle_id = vehicle_id
        self.epsilon = epsilon
        self.final_decision = None

    # Function to receive values from other nodes
    def receive(self, value, phase, sender):
        if self.is_crashed or self.final_output:  # Ignore messages if crashed or has reached final decision
            return

        # Ignore if received value is None
        if value is None:
            print(
                f"Node {self.vehicle_id} received 'None' from Node {sender}. Ignoring...")
            return

        if phase > self.phase:
            # Update phase and adopt value if phase is higher
            self.phase = phase
            self.value = value
            self.reset_bit_vector()
        elif phase == self.phase and self.bit_vector[sender] == 0:
            self.bit_vector[sender] = 1
            self.store_value(value)

    # Store function updates min and max values
    def store_value(self, received_value):
        if received_value < self.min_value:
            self.min_value = received_value
        elif received_value > self.max_value:
            self.max_value = received_value

    # Update node state if quorum is reached and if it has not reached pend
    def update_state(self, pend):
        if self.is_crashed or self.final_output:  # Ignore state update if crashed or reached final decision
            return

        if self.phase < pend:  # Only update state if phase < pend
            if sum(self.bit_vector) >= (n // 2 + 1):  # Quorum: majority of nodes
                new_value = (self.min_value + self.max_value) / \
                    2
                # Check if value is stable (within epsilon range of previous value)
                if abs(self.value - new_value) < self.epsilon:
                    self.stable_rounds += 1
                    print(
                        f"Node {self.vehicle_id} is stable for {self.stable_rounds} rounds (Value: {self.value:.4f})")
                else:
                    self.stable_rounds = 0  # Reset stable rounds if value changes significantly
                self.value = new_value
                self.phase += 1  # Move to the next phase
                self.reset_bit_vector()

        if self.phase == pend and self.stable_rounds >= T:  # Stop after stabilization for T rounds
            if not self.final_output:  # Ensure we only decide once
                self.final_output = True  # Mark node as having reached final output
                self.final_decision = self.decide_final_output()

    # Reset function to prepare for the next phase
    def reset_bit_vector(self):
        self.bit_vector = [0] * n
        self.min_value = self.value
        self.max_value = self.value

    # ABC algorithm to decide the final binary output
    def decide_final_output(self):
        """Decide final output based on ABC algorithm"""
        if self.value < 0.25 - self.epsilon:
            return 0
        elif self.value > 0.25 + self.epsilon:
            return 1
        else:
            return None

    # Function to broadcast final decision
    def broadcast_final_decision(self, other_nodes):
        for node in other_nodes:
            if node != self and not node.is_crashed:  # Send to other non-crashed nodes
                node.receive(self.final_decision, self.phase, self.vehicle_id)

# Helper function to simulate message loss


def message_lost():
    return random.random() < message_loss_probability

# Function to simulate controlled crash behavior


def crash_behavior(node, round_num, crashed_nodes, max_crashes):
    if len(crashed_nodes) < max_crashes and random.random() < 0.1:
        node.is_crashed = True
        crashed_nodes.append(node)
        print(f"Node {node.vehicle_id} crashed in round {round_num}.")

# Function to create nodes with binary values (0 or 1) based on a ratio


def create_binary_nodes(ratio_one, epsilon):
    nodes = []
    num_ones = int(ratio_one * n)  # Number of nodes initialized with 1
    num_zeros = n - num_ones       # Remaining nodes initialized with 0
    values = [1] * num_ones + [0] * num_zeros
    random.shuffle(values)  # Shuffle to randomly assign 0s and 1s to nodes
    for vehicle_id, value in enumerate(values):
        nodes.append(Node(value, vehicle_id, epsilon))
    return nodes


# Initialize nodes with binary values
nodes = create_binary_nodes(ratio_one, epsilon)

# Set limit on maximum number of crashed nodes
max_crashes = f  # Controlled by the parameter 'f'
crashed_nodes = []  # Track crashed nodes

# Calculate pend using epsilon
pend = calculate_pend(epsilon)

# Simulate rounds of communication with detailed output and message loss tracking
for round_num in range(max_rounds):
    print(f"--- Round {round_num} ---")
    lost_messages = 0  # Track lost messages for this round
    round_values = []

    # Randomly crash some nodes during the rounds but within the max limit
    for node in nodes:
        crash_behavior(node, round_num, crashed_nodes, max_crashes)

    # Dictionary to hold received states for each node during this round
    received_states = {i: [] for i in range(n)}

    # Broadcast values from each node
    for i, node in enumerate(nodes):
        if node.is_crashed:
            print(f"Node {i} has crashed and will not participate further.")
            continue
        if node.final_output:
            # Broadcast final decision if phase pend is reached
            node.broadcast_final_decision(nodes)
            print(f"Node {i} broadcasts final decision: {node.final_decision}")
            round_values.append(node.value)  # Store the final value
            continue
        round_values.append(node.value)  # Store node value for this round
        print(f"Node {i} (Phase {node.phase}, Value {node.value:.4f}) sending:")
        for j in range(n):
            if i != j:
                if message_lost():  # Message lost
                    lost_messages += 1
                else:
                    print(f"    Node {i} sends {node.value:.4f} to Node {j}")
                    nodes[j].receive(node.value, node.phase, i)
                    received_states[j].append(node.value)
         # Append round's node values for convergence tracking
    node_values_over_rounds.append(round_values)

    # Print received states for each node in this round
    print("\nReceived states in this round:")
    for node_id, values in received_states.items():
        print(
            f"Node {node_id} received states: {[f'{val:.4f}' for val in values]}")

    # Place this code to track phase progression right here, before updating the state
    round_phase_data = []  # Track phase progression for this round
    for i, node in enumerate(nodes):
        if node.is_crashed:
            round_phase_data.append(
                {'Node': i, 'Phase': 'Crashed'})  # Record crash
            continue
        round_phase_data.append(
            {'Node': i, 'Phase': node.phase})  # Record phase

    phase_progression.append(round_phase_data)  # Track this round's phase data

    # Track stable rounds per node
    round_stability = []
    for i, node in enumerate(nodes):
        if node.is_crashed:
            round_stability.append(None)
            continue
        if node.stable_rounds >= T:
            round_stability.append(node.stable_rounds)
        else:
            round_stability.append(0)  # Node is not stable yet
    stability_tracking.append(round_stability)

    # Update node state based on received values

    for i, node in enumerate(nodes):
        if node.is_crashed:
            continue  # Skip crashed nodes
        node.update_state(pend)  # Only update if phase < pend
        if node.final_output:
            print(
                f"Node {i} has reached phase pend and stops updating its own state but continues broadcasting.")
            print(f"Node {i} final decision: {node.final_decision}")
        else:
            print(
                f"Node {i} updated to value: {node.value:.4f} (Min: {node.min_value:.4f}, Max: {node.max_value:.4f}, Phase: {node.phase})")

    # Track lost messages in this round
    message_loss_tracking.append(lost_messages)

    # Check if all nodes have reached the exact phase pend or crashed
    if all(node.final_output or node.is_crashed for node in nodes):
        print("Consensus reached based on phase index!")
        break

# Output final values of nodes
print("\nStability Summary:")
for i, node in enumerate(nodes):
    if node.final_output:
        #  print( f"Node {i}: Final Output = {node.final_decision}, Final Phase = {node.phase}")
        print(
            f"Node {i}: Final Output = {node.final_decision}, Stable for {node.stable_rounds} rounds")
    elif node.is_crashed:
        print(f"Node {i}: Crashed, no final output.")
    else:
        print(f"Node {i}: Did not reach stability.")


data_to_save = {
    'message_loss_tracking': message_loss_tracking,
    'phase_progression': phase_progression,
    'node_values_over_rounds': node_values_over_rounds,
    'stability_tracking': stability_tracking
}
with open('simulation_data_dac.json', 'w') as f:
    json.dump(data_to_save, f, indent=4)  # Save data to JSON


# Display message loss tracking in a list format
print("\nMessage lost per round:", message_loss_tracking)
