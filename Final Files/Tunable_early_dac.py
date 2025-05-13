import random
import math
import json
from collections import defaultdict

# Calculate pend


def calculate_pend(epsilon):
    return math.ceil(math.log(epsilon) / math.log(0.5))


class Node:
    def __init__(self, id, initial_value, total_nodes):
        self.id = id
        self.phase = 0
        self.value = initial_value
        self.min_value = initial_value
        self.max_value = initial_value
        self.R = [0] * total_nodes  # Bit vector tracking received messages
        self.R[self.id] = 1  # Mark itself as received
        self.set = [0] * total_nodes  # set of received value
        self.total_nodes = total_nodes
        self.faulty = False  # Node is non-faulty by default

    def reset_for_next_phase(self):
        """Reset values related to state and the received message bit vector (R) after advancing to the next phase."""
        self.min_value = self.value
        self.max_value = self.value
        # Reset the bit vector for the new phase
        self.R = [0] * self.total_nodes
        self.R[self.id] = 1  # Mark itself as received again for the new phase
        self.set = [0] * self.total_nodes
        self.set[self.id] = self.value

    def update_value(self):
        """Update the node's value based on the min and max values received."""
        self.value = (self.min_value + self.max_value) / 2

    def make_final_decision(self, epsilon):
        """Decide the final output based on the final value and epsilon."""
        if self.value < 0.25 - epsilon:
            return 0
        elif self.value > 0.25 + epsilon:
            return 1
        else:
            return None


class DACAlgorithm:
    def __init__(self, total_nodes, num_faulty_nodes, message_loss_rate, initial_ratio, epsilon):
        self.total_nodes = total_nodes
        self.message_loss_rate = message_loss_rate
        self.pend = calculate_pend(epsilon)
        self.nodes = []
        self.num_faulty_nodes = num_faulty_nodes
        self.faulty_nodes = random.sample(range(total_nodes), num_faulty_nodes)
        self.initialize_nodes(initial_ratio)
        self.epsilon = epsilon

    def initialize_nodes(self, ratio):
        """Initialize the nodes with binary values based on the input ratio."""
        num_ones = int(self.total_nodes *
                       ratio)
        num_zeros = self.total_nodes - num_ones   # The rest will have value 0
        values = [1] * num_ones + [0] * num_zeros
        random.shuffle(values)

        # Assign the values to the nodes
        for i in range(self.total_nodes):
            node = Node(i, values[i], self.total_nodes)
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
                # print(f"Node {node.id} is crashed and does not participate.")
                continue
            message = (node.id, node.value, node.phase)
            for other_node in self.nodes:
                if other_node.id != node.id and not self.simulate_message_loss():
                    messages[other_node.id].append(message)
            # print(
            #     f"Node {node.id} (Phase {node.phase}) broadcasts value {node.value}.")
        return messages

    def run(self):
        """Run the DAC algorithm and count the number of rounds to termination."""
        rounds = 0  # Initialize round counter

        while True:
            rounds += 1  # Increment round count
            # print(f"\n--- Round {rounds} ---")
            # Check if all non-faulty nodes have reached the termination phase
            all_terminated = all(
                node.phase == self.pend or node.faulty for node in self.nodes)
            if all_terminated:
                print(f"All nodes reached termination after {rounds} rounds.")
                break

            messages = self.broadcast_messages()

            # Process messages for each node
            for node in self.nodes:
                if node.faulty:
                    continue  # Skip processing for faulty nodes

                # Current round's received messages
                received_messages = messages[node.id]

                # Create a dictionary to store unique messages per node, replacing old messages if a new one is received
                unique_messages = {}

                # Retain messages from previous rounds for the same phase
                for sender_id in range(self.total_nodes):
                    if node.R[sender_id] == 1 and sender_id != node.id:
                        unique_messages[sender_id] = (
                            sender_id, node.value, node.phase)

                # Process new messages received in the current round and replace previous messages if received again
                for sender_id, sender_value, sender_phase in received_messages:
                    unique_messages[sender_id] = (
                        sender_id, sender_value, sender_phase)

                accumulated_messages = list(unique_messages.values())
                # print(
                #     f"Node {node.id} (Phase {node.phase}) accumulated messages: {accumulated_messages}")

                if node.phase == self.pend:
                    # print(
                    #     f"Node {node.id} has reached pend and will not update its state.")
                    continue  # Node will broadcast but not update its state or jump phases

                for sender_id, sender_value, sender_phase in accumulated_messages:
                    if sender_phase > node.phase:
                        # print(
                        #     f"Node {node.id} jumps to phase {sender_phase} (from Node {sender_id})")
                        node.value = sender_value
                        node.phase = sender_phase
                        node.reset_for_next_phase()  # Reset after jumping to the new phase
                        # break  "we need to check all the receive message even after we update the phase"
                    elif sender_phase == node.phase and node.R[sender_id] == 0:
                        node.R[sender_id] = 1
                        node.set[sender_id] = sender_value
                        node.min_value = min(node.min_value, sender_value)
                        node.max_value = max(node.max_value, sender_value)

                if rounds <= 5:
                    node.value = node.min_value

                else:
                    # print("here")
                    if sum(node.R) >= (self.total_nodes-self.num_faulty_nodes) and node.phase < self.pend:
                        # print(
                        #     f"Node {node.id} advances to phase {node.phase + 1}.")

                        values = []

                        for i in range(0, node.total_nodes):
                            if node.R[i] == 1:
                                values.append(node.set[i])

                        maxValue = max(values)
                        minValue = min(values)

                        values.sort()

                        # print(f"Node {node.id}: {values}")

                        # print(maxValue - minValue)
                        # print(self.epsilon / 2)

                        if maxValue - minValue < self.epsilon / 2:
                            node.value = minValue
                            node.phase = self.pend

                        elif maxValue - values[self.num_faulty_nodes] < self.epsilon / 2:
                            node.value = values[self.num_faulty_nodes]
                            node.phase += 1

                        elif values[self.total_nodes - 2*self.num_faulty_nodes+1] < self.epsilon / 2:
                            node.value = values[self.total_nodes -
                                                2*self.num_faulty_nodes+1]
                            node.phase += 1

                        else:
                            node.update_value()
                            node.phase += 1

                        node.reset_for_next_phase()  # Reset only after advancing to the next phase
        return rounds

    def print_final_values(self):
        """Print the final state of all nodes."""
        print("\n--- Final Node States ---")
        for node in self.nodes:
            if node.faulty:
                print(f"Node {node.id} is crashed and has no final output.")
            else:
                decision = node.make_final_decision(0.01)  # Example epsilon
                print(
                    f"Node {node.id}: Final Value = {node.value}, Final Phase = {node.phase}, Decision = {decision}")


if __name__ == "__main__":
    num_runs = int(
        input("How many times do you want to run each configuration? "))

    configurations = [

        # Vary N and f with message loss rate 80%
        # {'N': 15, 'f': 4, 'message_loss_rate': 0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 30, 'f': 9, 'message_loss_rate':  0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 75, 'f': 24, 'message_loss_rate':  0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 125, 'f': 40, 'message_loss_rate': 0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 250, 'f': 80, 'message_loss_rate': 0.5,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},


        # Vary N and f with message loss rate 80%
        # {'N': 15, 'f': 4, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 30, 'f': 9, 'message_loss_rate':  0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 75, 'f': 24, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 125, 'f': 40, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 250, 'f': 80, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},

        # COnverence vs Initial ratio
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.1, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.2, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.3, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.4, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.5, 'epsilon': 0.001},

        # 10%
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0.1, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0.2, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0.3, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0.4, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #  'initial_ratio': 0.5, 'epsilon': 0.001},

        # 80%message loss
        # {'N': 15, 'f': 4, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 30, 'f': 9, 'message_loss_rate':  0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 75, 'f': 24, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 125, 'f': 40, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 250, 'f': 80, 'message_loss_rate': 0.8,
        #  'initial_ratio': 0.8, 'epsilon': 0.001},

        #  10%message loss
        {'N': 15, 'f': 4, 'message_loss_rate': 0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},
        {'N': 30, 'f': 9, 'message_loss_rate':  0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},
        {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},
        {'N': 75, 'f': 24, 'message_loss_rate': 0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},
        {'N': 125, 'f': 40, 'message_loss_rate': 0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},
        {'N': 250, 'f': 80, 'message_loss_rate': 0.1,
         'initial_ratio': 0.8, 'epsilon': 0.001},

        # Vary Message_loss_rate
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.1,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.2,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.3,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.4,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.5,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.6,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.7,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},
        # {'N': 50, 'f': 15, 'message_loss_rate': 0.8,
        #     'initial_ratio': 0.8, 'epsilon': 0.001},



    ]

    results = []  # This will store results for the JSON file

    for config in configurations:
        for _ in range(num_runs):
            print(f"\nRunning DAC with configuration: {config}")
            dac = DACAlgorithm(
                total_nodes=config['N'],
                num_faulty_nodes=config['f'],
                message_loss_rate=config['message_loss_rate'],
                initial_ratio=config['initial_ratio'],
                epsilon=config['epsilon']
            )
            rounds = dac.run()
            # dac.print_final_values()

            # Store results for each run
            result = {
                'config': config,
                'rounds': rounds,
                'num_nodes': config['N'],
                'message_loss_rate': config['message_loss_rate'],
                'initial_ratio': config['initial_ratio']
            }
            results.append(result)

    # Write results to JSON file
    with open('Tunable_Early-DAC(5)_AlgoResults.json', 'w') as f:
        json.dump(results, f, indent=4)
