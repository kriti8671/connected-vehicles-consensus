import random
import json


class Node:
    def __init__(self, id, initial_value):
        self.id = id
        self.value = initial_value
        self.crashed = False  # Indicates if the node is crashed

    def broadcast_value(self):

        return self.value

    def update_value(self, received_values):
        """Update value """
        for v_j in received_values:
            self.value = (self.value + v_j) / 2
            print(
                f'updated value by node id{self.id}: {self.value} when we have {v_j}')


class ACAlgorithm:
    def __init__(self, total_nodes, num_faulty_nodes, message_loss_rate, epsilon, initial_ratio):
        self.nodes = self.initialize_nodes(
            total_nodes, num_faulty_nodes, initial_ratio)
        self.total_nodes = total_nodes
        self.num_faulty_nodes = num_faulty_nodes
        self.message_loss_rate = message_loss_rate
        self.epsilon = epsilon
        self.initialize_crash_nodes()

    def initialize_nodes(self, total_nodes, f, initial_ratio):
        """Initialize nodes with values in a specified ratio."""
        num_ones = int((total_nodes) * initial_ratio)
        initial_values = [1] * num_ones + [0] * ((total_nodes) - num_ones)
        # Shuffle to distribute 1s and 0s randomly
        random.shuffle(initial_values)
        return [Node(i, initial_values[i]) for i in range(total_nodes)]

    def initialize_crash_nodes(self):
        """Randomly crash `f` nodes that will no longer participate in the algorithm."""
        crash_nodes = random.sample(self.nodes, self.num_faulty_nodes)
        for node in crash_nodes:
            node.crashed = True
            print(f"Node {node.id} has crashed and will not participate.")

    def run(self):
        """Run the consensus algorithm until values converge within epsilon."""
        rounds = 0
        while True:
            rounds += 1
            # Initialize message storage
            messages = {node.id: [] for node in self.nodes if not node.crashed}

            print(f"\n--- Round {rounds} ---")

            # Each node broadcasts its value to all other nodes
            for node in self.nodes:
                if not node.crashed:
                    broadcasted_value = node.broadcast_value()
                    # Distribute broadcasted value to all other non-crashed nodes
                    for recipient_node in self.nodes:
                        if recipient_node.id != node.id and not recipient_node.crashed:
                            # Simulate message loss
                            if random.random() > self.message_loss_rate:
                                messages[recipient_node.id].append(
                                    (node.id, broadcasted_value))

            # Print message logs for this round
            # print("Message Logs:")
            for receiver_id, msg_list in messages.items():
                log = [(sender_id, value) for sender_id, value in msg_list]
                # print(f"Node {receiver_id} received messages: {log}")

            # Each node updates its value based on each received message individually
            for node in self.nodes:
                if not node.crashed:
                    received_values = [value for _,
                                       value in messages.get(node.id, [])]
                    node.update_value(received_values)

            # Check convergence among non-crashed nodes
            values = [node.value for node in self.nodes if not node.crashed]
            if max(values) - min(values) < self.epsilon:
                print(f"\nConverged in {rounds} rounds.")
                break

        return rounds

    def print_final_values(self):
        """Print the final values of each node (indicating crashed nodes)."""
        for node in self.nodes:
            if not node.crashed:
                print(f"Node {node.id}: Final Value = {node.value}")
            else:
                print(f"Node {node.id}: Crashed")


if __name__ == "__main__":
    # Run configurations
    num_runs = int(
        input("How many times do you want to run each configuration? "))

    configurations = [
        # works for => n ≥ 2f + 1.
        {'N': 50, 'f': 23, 'message_loss_rate': 0.05,
            'epsilon': 0.01, 'initial_ratio': 0.8},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.1,
            'epsilon': 0.01, 'initial_ratio': 0.8},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.15,
            'epsilon': 0.01, 'initial_ratio': 0.8},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.2,
            'epsilon': 0.01,  'initial_ratio': 0.8},
        {'N': 50, 'f': 9, 'message_loss_rate': 0.25,
            'epsilon': 0.01, 'initial_ratio': 0.8},
    ]

    results = []

    for config in configurations:
        for _ in range(num_runs):
            print(f"\nRunning AC with configuration: {config}")
            ac = ACAlgorithm(
                total_nodes=config['N'],
                num_faulty_nodes=config['f'],
                message_loss_rate=config['message_loss_rate'],
                epsilon=config['epsilon'],
                initial_ratio=config['initial_ratio']
            )
            rounds = ac.run()
            ac.print_final_values()

            # Store results for each run
            result = {
                'config': config,
                'rounds': rounds,
                'num_nodes': config['N'],
                'message_loss_rate': config['message_loss_rate']
            }
            results.append(result)

    # Write results to JSON file
    with open('AC_Algorithm_Results.json', 'w') as f:
        json.dump(results, f, indent=4)
    print("Results saved to AC_Algorithm_Results.json")
