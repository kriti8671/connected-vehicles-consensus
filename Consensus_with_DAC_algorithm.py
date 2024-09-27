import random
import math

# Configuration Parameters
n = 9  # Total number of nodes (vehicles)
f = 1  # Maximum number of Byzantine nodes
T = 3  # Number of rounds over which stability is ensured
max_rounds = 100  # Maximum rounds to reach consensus
epsilon = 0.001  # Precision for approximate consensus
value_range = (0, 1)  # Range for node values

ratio_one = 0.7  # Ratio of nodes initialized to value 1
message_loss_probability = 0.3  # Probability of message loss (10%)
message_loss_tracking = []  # List to track lost messages per round

# Helper function to calculate pend


def calculate_pend(epsilon):
    return math.ceil(math.log(epsilon) / math.log(0.5))

# Node class implementing DAC and ABC algorithm


class Node:
    def __init__(self, initial_value, vehicle_id, epsilon):
        # Node's actual value (not trimmed for calculations)
        self.value = initial_value
        self.phase = 0  # Phase index starts at 0
        self.min_value = initial_value  # Minimum observed value
        self.max_value = initial_value  # Maximum observed value
        self.received_values = []  # List of received values
        self.bit_vector = [0] * n  # Tracks received messages from nodes
        self.is_faulty = False  # Indicates if the node is Byzantine
        self.final_output = False  # Indicates if the node has reached pend
        self.vehicle_id = vehicle_id  # Unique ID for the vehicle
        self.epsilon = epsilon  # Epsilon for consensus tolerance
        self.final_decision = None  # Holds the final binary decision

    # Function to receive values from other nodes
    def receive(self, value, phase, sender):
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
        if self.phase < pend:  # Only update state if phase < pend
            if sum(self.bit_vector) >= (n // 2 + 1):  # Quorum: majority of nodes
                self.value = (self.min_value + self.max_value) / \
                    2  # Update value
                self.phase += 1  # Move to the next phase
                self.reset_bit_vector()

        if self.phase == pend:  # Stop updating after reaching pend
            if not self.final_output:  # Ensure we only decide once
                self.final_output = True  # Mark node as having reached final output
                # Decide final binary output using ABC
                self.final_decision = self.decide_final_output()

    # Reset function to prepare for the next phase
    def reset_bit_vector(self):
        self.bit_vector = [0] * n
        self.received_values = []
        self.min_value = self.value
        self.max_value = self.value

    # ABC algorithm to decide the final binary output
    def decide_final_output(self):
        """Decide final output based on ABC algorithm"""
        if self.value < 0.5 - self.epsilon / 2:
            # print(f"Node {self.vehicle_id} final decision: 0")
            return 0
        elif self.value > 0.5 + self.epsilon / 2:
            # print(f"Node {self.vehicle_id} final decision: 1")
            return 1
        else:
            # print(f"Node {self.vehicle_id} final decision: None")
            return None

# Helper function to simulate message loss


def message_lost():
    return random.random() < message_loss_probability

# Byzantine node behavior (sending conflicting information)


def byzantine_behavior(node):
    return random.uniform(value_range[0], value_range[1])

# Function to create nodes with binary values (0 or 1) based on a ratio


def create_binary_nodes(ratio_one, epsilon):
    nodes = []
    num_ones = int(ratio_one * n)  # Number of nodes initialized with 1
    num_zeros = n - num_ones       # Remaining nodes initialized with 0
    # Create list with required 1s and 0s
    values = [1] * num_ones + [0] * num_zeros
    random.shuffle(values)  # Shuffle to randomly assign 0s and 1s to nodes
    for vehicle_id, value in enumerate(values):
        nodes.append(Node(value, vehicle_id, epsilon))
    return nodes


# Initialize nodes with binary values
# Use ratio_one from configuration
nodes = create_binary_nodes(ratio_one, epsilon)

# Randomly select faulty nodes
byzantine_nodes = random.sample(nodes, f)
for node in byzantine_nodes:
    node.is_faulty = True

# Calculate pend using epsilon
pend = calculate_pend(epsilon)

# Simulate rounds of communication with detailed output and message loss tracking
for round in range(max_rounds):
    print(f"--- Round {round} ---")
    lost_messages = 0  # Track lost messages for this round

    # Dictionary to hold received states for each node during this round
    received_states = {i: [] for i in range(n)}

    # Broadcast values from each node
    for i, node in enumerate(nodes):
        # Trimming for display only
        print(f"Node {i} (Phase {node.phase}, Value {node.value:.4f}) sending:")
        for j in range(n):
            if i != j:
                if message_lost():  # Message lost
                    lost_messages += 1
                else:
                    if node.is_faulty:
                        sent_value = byzantine_behavior(node)
                        # Trimming for display
                        print(
                            f"    Node {i} (faulty) sends {sent_value:.4f} to Node {j}")
                        # Byzantine behavior
                        nodes[j].receive(sent_value, node.phase, i)
                    else:
                        # Trimming for display
                        print(
                            f"    Node {i} sends {node.value:.4f} to Node {j}")
                        # Normal node sends value
                        nodes[j].receive(node.value, node.phase, i)
                    # Collect received states for printing later
                    received_states[j].append(node.value)

    # Print received states for each node in this round
    print("\nReceived states in this round:")
    for node_id, values in received_states.items():
        # Trimming for display
        print(
            f"Node {node_id} received states: {[f'{val:.4f}' for val in values]}")

    # Update node state based on received values
    for i, node in enumerate(nodes):
        if node.received_values:
            # Trimming for display
            print(
                f"Node {i} received values: {[f'{val:.4f}' for val in node.received_values]}")
        node.update_state(pend)  # Only update if phase < pend
        if node.final_output:
            print(
                f"Node {i} has reached phase pend and stops updating  own state but continues broadcasting.")
            print(f"Node {i} final decision: {node.final_decision}")
        print(f"Node {i} updated to value: {node.value:.4f} (Min: {node.min_value:.4f}, Max: {node.max_value:.4f}, Phase: {node.phase})")

    # Track lost messages in this round
    message_loss_tracking.append(lost_messages)

    # Check if all nodes have reached the exact phase pend
    if all(node.final_output for node in nodes):
        print("Consensus reached based on phase index!")
        break

# Output final values of nodes
for i, node in enumerate(nodes):
    print(
        f"Node {i}: Final Outuput = {node.final_decision}, Final Phase = {node.phase}")

# Display message loss tracking in a list format
print("\nMessage lost per round:", message_loss_tracking)
