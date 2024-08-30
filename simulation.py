import random
import numpy as np
import json_file
from vehicles import Vehicle


def consensus_simulation(total_vehicles, total_rounds, message_loss_rate, epsilon_value, f):

    # Initialize vehicles with random binary states (0 or 1)
    vehicles = [Vehicle(vehicle_id=i, initial_state=random.randint(
        0, 1), epsilon=epsilon_value) for i in range(total_vehicles)]

    # Initialize variable to track convergence
    rounds_to_reach_consensus = total_rounds

    # Simulate rounds of message passing and state updating
    for current_round in range(total_rounds):
        print(f"\n--- Round {current_round + 1} ---")

        # Each vehicle broadcasts its state to all others
        for vehicle in vehicles:
            vehicle.broadcast_state(vehicles, message_loss_rate)

        #  Each vehicle updates its state based on the received messages

        for vehicle in vehicles:
            vehicle.update_state(total_vehicles, f)

        # Check if all vehicles have reached a consensus

        current_outputs = [vehicle.decide_final_output()
                           for vehicle in vehicles]

        if all(output == current_outputs[0] for output in current_outputs if output is not None):
            rounds_to_reach_consensus = current_round + 1
            print(f"Consensus reached at round {rounds_to_reach_consensus}")
            break

    # Step 3: Determine final outputs after all rounds

    final_consensus_outputs = [vehicle.decide_final_output()

                               for vehicle in vehicles]
    # Return final outputs and rounds to reach consensus
    return final_consensus_outputs, rounds_to_reach_consensus


# # Simulation parameters
# TOTAL_VEHICLES = int(input("Enter Total Vehicles: "))
# TOTAL_ROUNDS = int(input("Total rounds: "))
# MESSAGE_LOSS_RATE = float(input("Message_loss_rate: "))  # % message loss rate
# EPSILON_VALUE = 0.001
# Run the simulation
# final_consensus_outputs, rounds_to_reach_consensus = consensus_simulation(
#     TOTAL_VEHICLES, TOTAL_ROUNDS, MESSAGE_LOSS_RATE, EPSILON_VALUE, f)


# # Display the final outputs of all vehicles
# print("\nFinal Outputs of all vehicles:", final_consensus_outputs)
# print(f"Rounds to reach consensus: {rounds_to_reach_consensus}")

def run_simulations_and_store_results(configurations, num_runs, output_file):
    results = []

    for config in configurations:
        N = config['N']
        f = config['f']
        message_loss_rate = config['message_loss_rate']
        initial_ratio = config['initial_ratio']
        epsilon_value = config['epsilon']
        total_rounds = int(
            input("How many times do you want to repeat each configuration:"))

        if N <= 3 * f:
            print(
                f"Invalid configuration for N={N} and f={f}: N must be greater than 3f.")
            continue

        print(f"Running simulation for configuration: {config}")
        rounds_results = []

        for _ in range(num_runs):
            final_outputs, rounds_to_reach_consensus = consensus_simulation(
                N, total_rounds, message_loss_rate, epsilon_value, f
            )
            rounds_results.append(rounds_to_reach_consensus)

        # Calculate average and percetile for this configuration
        average_rounds = np.mean(rounds_results)
        percentile_99 = np.percentile(rounds_results, 99)

        result = {
            'configuration': config,
            'average_rounds': average_rounds,
            '99th_percentile_rounds': percentile_99,
            'all_rounds': rounds_results
        }

        results.append(result)

        # Print results for this configuration
        print(
            f"\nResults for Configuration: N={N}, f={f}, message_loss_rate={message_loss_rate}, initial_ratio={initial_ratio}")
        print(f"Average Rounds to Reach Consensus: {average_rounds}")
        print(f"99th Percentile Rounds to Reach Consensus: {percentile_99}")
        print(f"All Rounds to Reach Consensus: {rounds_results}")

    # Save the results to a JSON file using the utility function
    # save_results_to_json(results, output_file)
    json_file.save_results_to_json(results, output_file)


# Define configurations
configurations = [
    {'N': 4, 'f': 1, 'message_loss_rate': 0.1,
        'initial_ratio': 0.5, 'epsilon': 0.001},
    {'N': 7, 'f': 2, 'message_loss_rate': 0.05,
        'initial_ratio': 0.7, 'epsilon': 0.001},
    # Add more configurations as needed
]

# Run simulations and store results
num_runs = int(
    input("how many times you want to repeat the entire simulation: "))

run_simulations_and_store_results(
    configurations, num_runs, output_file='simulation_results.json')

# num_runs= Repeats the simulation multiple times
# don't confuse with total runs ( this is for running a single configuration)
