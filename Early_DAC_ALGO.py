import random
import math
import json
from collections import defaultdict

# Calculate pend


def calculate_pend(epsilon):
    return math.ceil(math.log(epsilon) / math.log(0.5))


class Node:
    def __init__(self, id, initial_value, total_nodes, f):
        self.id = id
        self.phase = 0
        self.value = initial_value
        # Bit vector tracking received messages (0 means no message received, 1 means received)
        self.R = [0] * total_nodes
        self.R[self.id] = 1  # Mark itself as received
        self.total_nodes = total_nodes
        self.f = f  # Number of faulty nodes
        self.faulty = False  # Node is non-faulty by default

    def reset_for_next_phase(self):
        """Reset the received message bit vector (R) after advancing to the next phase."""
        self.R = [0] * self.total_nodes
        self.R[self.id] = 1  # Mark itself as received again for the new phase


class EarlyDACAlgorithm:
    def __init__(self, total_nodes, num_faulty_nodes, message_loss_rate, initial_ratio, epsilon):
        self.total_nodes = total_nodes
        self.message_loss_rate = message_loss_rate
        self.pend = calculate_pend(epsilon)
        self.nodes = []
        self.faulty_nodes = random.sample(range(total_nodes), num_faulty_nodes)
        self.initialize_nodes(initial_ratio, num_faulty_nodes)

    def initialize_nodes(self, ratio, f):
        """Initialize the nodes with binary values based on the input ratio."""
        num_ones = int(self.total_nodes * ratio)
        values = [1] * num_ones + [0] * (self.total_nodes - num_ones)
        random.shuffle(values)

        # Assign values to the nodes
        for i in range(self.total_nodes):
            node = Node(i, values[i], self.total_nodes, f)
            if i in self.faulty_nodes:
                node.faulty = True
            self.nodes.append(node)

    def simulate_message_loss(self):
        """Simulate message loss based on the given loss rate."""
        return random.random() <= self.message_loss_rate

    def broadcast_messages(self):
        """Simulate the broadcast of messages by all nodes."""
        messages = defaultdict(list)
        for node in self.nodes:
            if node.faulty:
                print(f"Node {node.id} is faulty and does not broadcast.")
                continue
            message = (node.id, node.value, node.phase)
            print(
                f"Node {node.id} broadcasts: Value = {node.value}, Phase = {node.phase}")
            for other_node in self.nodes:
                if other_node.id != node.id and not self.simulate_message_loss():
                    messages[other_node.id].append(message)
        return messages

    def run(self):
        """Run the Early-DAC algorithm and count the number of rounds to termination."""
        rounds = 0

        while True:
            print(f"\n--- Round {rounds + 1} ---")  # Print each round
            rounds += 1
            all_terminated = all(
                node.phase == self.pend or node.faulty for node in self.nodes)
            if all_terminated:
                print(f"All nodes reached termination after {rounds} rounds.")
                break

            messages = self.broadcast_messages()
            for node in self.nodes:
                if node.faulty:
                    continue

                received_messages = messages[node.id]
                print(f"Node {node.id} received messages: {received_messages}")
                if received_messages:
                    min_value = min(vj for _, vj, _ in received_messages)
                    max_value = max(vj for _, vj, _ in received_messages)
                else:
                    min_value = None
                    max_value = None
                print(f"min value: {min_value} and max_value: {max_value}")

                if node.phase == self.pend:
                    # print(
                    #     f"Node {node.id} has reached pend and will not update its state.")
                    continue  # Node will broadcast but not update its state or jump phases

                # Only mark messages as received here, do not calculate min and max yet
                for sender_id, vj, pj in received_messages:
                    if pj > node.phase:
                        print(
                            f"Node {node.id} jumps to Phase {pj} with Value {vj} from Node {sender_id}")
                        node.value = vj
                        node.phase = pj
                        node.reset_for_next_phase()
                    elif pj == node.phase and node.R[sender_id] == 0:
                        # Mark that we received a message from this node
                        node.R[sender_id] = 1

                        # evaluate conditions based on the number of identical values
                        if sum(node.R) >= 2 * node.f + 1:

                            identical_values = [
                                vj for _, vj, _ in received_messages if pj == node.phase]
                            print(f"identical values:{identical_values}")
                            print(
                                f"Node {node.id} identical values count: {len(identical_values)}")

                            # Check if there are 2f + 1 identical values
                            if len(identical_values) >= 2 * node.f + 1:

                                print(
                                    f"lenght of identical value:{len(identical_values)}")
                                print(
                                    f"Node {node.id} enters Early-Stopping with Value {identical_values[0]}")
                                # Set to the identical value
                                node.value = identical_values[0]
                                node.phase = self.pend  # Early-stopping
                            elif len(identical_values) >= node.f + 1:
                                print(
                                    f"lenght of identical value:{len(identical_values)}")
                                print(
                                    f"Node {node.id} updates Value to {identical_values[0]} and advances to Phase {node.phase + 1}")
                                node.value = identical_values[0]
                                node.phase += 1
                            else:
                                # Calculate min and max from all received messages for fallback condition

                                new_value = (min_value + max_value) / 2
                                print(
                                    f"Node {node.id} updates Value to {new_value} when we have (min: {min_value}, max: {max_value}) and advances to Phase {node.phase + 1}")
                                node.value = new_value
                                node.phase += 1
                            node.reset_for_next_phase()
        return rounds

    def print_final_values(self):
        """Print the final state of all nodes."""
        for node in self.nodes:
            if node.faulty:
                print(f"Node {node.id} is faulty.")
            else:
                print(
                    f"Node {node.id}: Final Value = {node.value}, Final Phase = {node.phase}")


# Run the Early-DAC algorithm
if __name__ == "__main__":
    num_runs = int(
        input("How many times do you want to run each configuration? "))

    configurations = [
        {'N': 50, 'f': 15, 'message_loss_rate': 0.3,
            'initial_ratio': 0.2, 'epsilon': 0.001}
    ]
    results = []
    for config in configurations:
        for _ in range(num_runs):
            print(f"\nRunning Early-DAC with configuration: {config}")
            edac = EarlyDACAlgorithm(
                total_nodes=config['N'],
                num_faulty_nodes=config['f'],
                message_loss_rate=config['message_loss_rate'],
                initial_ratio=config['initial_ratio'],
                epsilon=config['epsilon']
            )
            rounds = edac.run()
            print(f"Total Rounds: {rounds}")
            edac.print_final_values()
            # Store results for each run
            result = {
                'config': config,
                'rounds': rounds,
                'num_nodes': config['N'],
                'message_loss_rate': config['message_loss_rate']
            }
            results.append(result)

    # Write results to JSON file
    with open('Early_DAC_Algorithm_Results.json', 'w') as f:
        json.dump(results, f, indent=4)
