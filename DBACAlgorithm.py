import random
import math
import json


def calculate_p_end(n, epsilon):
    return 7  # use smaller pend for easy run
   # return math.ceil(math.log(epsilon) / math.log(1 - 2 ** -n))


class Node:
    def __init__(self, node_id, is_byzantine=False):
        self.node_id = node_id
        self.vi = random.uniform(0, 1)
        self.phase = 0
        self.is_byzantine = is_byzantine
        self.Ri = [0] * n
        self.Ri[node_id] = 1  # Mark self as received (including self-message)
        self.Ri_low = []
        self.Ri_high = []
        self.buffer = {}  # Buffer to store latest messages for each phase
        self.received_messages = []  # To store received messages for printing

    def byzantine_strategy_1(self):
        """Strategy 1: Send a unique random value to each recipient."""
        return random.uniform(0, 1)

    def byzantine_strategy_2(self, recipient_phase):
        """Strategy 2: Send high values for higher-phase nodes, low values for lower-phase nodes."""
        if recipient_phase > self.phase:
            # High value for nodes with higher phases
            return random.uniform(0.75, 1)
        else:
            # Low value for nodes with lower phases
            return random.uniform(0, 0.25)

    def broadcast(self, nodes):

        if self.is_byzantine:
            # Randomly select one strategy for the entire broadcast round
            chosen_strategy = random.choice(
                [self.byzantine_strategy_1, self.byzantine_strategy_2]
            )
            print(
                f"Byzantine Node {self.node_id} chose {'Strategy 1' if chosen_strategy == self.byzantine_strategy_1 else 'Strategy 2'}")

            broadcast_value = {}

            for node in nodes:
                if node.node_id == self.node_id:
                    continue  # Skip sending a message to itself

                # Use the chosen strategy for all recipients in this round
                if chosen_strategy == self.byzantine_strategy_1:
                    broadcast_value[node.node_id] = self.byzantine_strategy_1()
                else:
                    broadcast_value[node.node_id] = self.byzantine_strategy_2(
                        node.phase)

            print(
                f"Byzantine Node {self.node_id} (Phase {self.phase}) broadcasting inconsistent values: {broadcast_value}"
            )
            return self.node_id, broadcast_value, self.phase

        else:
            # Normal node broadcasts its value consistently
            broadcast_value = self.vi
            print(
                f"Node {self.node_id} (Phase {self.phase}) broadcasting: {broadcast_value:.4f}"
            )
            return self.node_id, broadcast_value, self.phase

    def receive_message(self, sender_id, value, phase, message_loss_rate):
        # Simulate message loss for each received message
        if random.random() < message_loss_rate:
            print(f"Node {self.node_id} lost message from Node {sender_id}.")
            return  # Simulate lost message by returning early

        # Handle inconsistent values from Byzantine nodes
        received_value = value if not isinstance(
            value, dict) else value.get(self.node_id, random.uniform(0, 1))

        # Check if the message meets the required condition
        if self.phase < p_end and phase >= self.phase and self.Ri[sender_id] == 0:
            self.Ri[sender_id] = 1  # Mark sender as received
            self.STORE(received_value)

            self.received_messages = [(s_id, p, v) for (
                s_id, p, v) in self.received_messages if s_id != sender_id]
            self.received_messages.append((sender_id, phase, received_value))
            # print(f"Node {self.node_id} received from Node {sender_id} - Phase {phase}, Value {received_value:.4f}")

    def STORE(self, value):
        if len(self.Ri_low) < f + 1:
            self.Ri_low.append(value)
        elif value < max(self.Ri_low):
            self.Ri_low[self.Ri_low.index(max(self.Ri_low))] = value

        if len(self.Ri_high) < f + 1:
            self.Ri_high.append(value)
        elif value > min(self.Ri_high):
            self.Ri_high[self.Ri_high.index(min(self.Ri_high))] = value

    def count_received_messages(self):
        self.Ri[self.node_id] = 1  # Count self-message
        return sum(self.Ri)

    def reset_after_phase_increment(self):
        self.Ri = [0] * n
        self.Ri[self.node_id] = 1  # Mark itself as received
        self.buffer = {}
        self.Ri_low = []
        self.Ri_high = []
        self.received_messages = []


class DBACAlgorithm:
    def __init__(self, total_nodes, faulty_nodes, message_loss_rate, epsilon):
        global n, f, p_end
        n = total_nodes
        f = faulty_nodes
        p_end = calculate_p_end(n, epsilon)
        self.message_loss_rate = message_loss_rate
        self.nodes = [Node(node_id, is_byzantine=(node_id < f))
                      for node_id in range(n)]
        self.round_counter = 0
        # self.total_byzantine = faulty_nodes

    def run(self):
        """Runs the DBAC algorithm until all nodes reach p_end."""
        termination = False
        while not termination:
            self.round_counter += 1
            print(f"\n--- Round {self.round_counter} ---")

            # Each node broadcasts its current value
            messages = [node.broadcast(self.nodes) for node in self.nodes]

            for node in self.nodes:
                node.received_messages = []
                for sender_id, value, phase in messages:
                    if sender_id != node.node_id:
                        node.receive_message(
                            sender_id, value, phase, self.message_loss_rate)
                # print(f"Node {node.node_id} received messages: {node.received_messages}")

            # Check phase update condition for each node
            for node in self.nodes:
                if node.phase == p_end:
                    print(
                        f"Node {node.node_id} has reached termination phase {p_end}.")
                    continue  # Node reached final phase, only broadcasts

                received_count = node.count_received_messages()
                # print(f"Node {node.node_id} count messages: {received_count}")
                if received_count >= (n + 3 * f) // 2 + 1:
                    node.vi = (max(node.Ri_low) + min(node.Ri_high)) / 2
                    node.phase += 1
                    # print(f"Node {node.node_id} Ri_low: {node.Ri_low}, Ri_high: {node.Ri_high}")
                    print(
                        f"Node {node.node_id} updated to new phase {node.phase} with vi = {node.vi:.4f}")
                    node.reset_after_phase_increment()
                else:
                    print(
                        f"Node {node.node_id} did not receive enough messages to update Phase {node.phase}.")

            termination = all(node.phase == p_end for node in self.nodes)

        return self.round_counter

    def print_final_values(self):
        """Prints final values of each node after consensus is reached."""
        print(f"\n--- Final Results ---")
        for node in self.nodes:
            print(
                f"Node {node.node_id}: final value = {node.vi:.4f}, final phase = {node.phase}")


if __name__ == "__main__":
    num_runs = int(
        input("How many times do you want to run each configuration? "))
    configurations = [
        {'N': 50, 'f': 9, 'message_loss_rate': 0.05,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.2,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.15,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.2,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.25,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.3,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.35,
            'epsilon': 0.01},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.4,
            'epsilon': 0.01},

    ]

    results = []  # Store results for JSON

    for config in configurations:
        for _ in range(num_runs):
            print(f"\nRunning DBAC with configuration: {config}")
            dbac = DBACAlgorithm(
                total_nodes=config['N'],
                faulty_nodes=config['f'],
                message_loss_rate=config['message_loss_rate'],
                epsilon=config['epsilon']
            )
            rounds = dbac.run()
            dbac.print_final_values()

            # Store results for each run
            result = {
                'config': config,
                'rounds': rounds,
                'num_nodes': config['N'],
                'message_loss_rate': config['message_loss_rate']
            }
            results.append(result)

    # Write results to JSON file
    with open('dbac_results.json', 'w') as f:
        json.dump(results, f, indent=4)
