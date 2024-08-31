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

        # Each vehicle updates its state based on the received messages
        for vehicle in vehicles:
            vehicle.update_state(total_vehicles, f)

        # Check if all vehicles have reached a consensus
        current_outputs = [vehicle.decide_final_output()
                           for vehicle in vehicles]
        # if all(output is not None for output in current_outputs):
        if all(output == current_outputs[0] for output in current_outputs if output is not None):
            rounds_to_reach_consensus = current_round + 1
            print(
                f"Consensus reached at round {rounds_to_reach_consensus}")
            break

    final_consensus_outputs = [vehicle.decide_final_output()
                               for vehicle in vehicles]

    return final_consensus_outputs, rounds_to_reach_consensus


def run_simulations_and_store_results(configurations, output_file):
    results = []

    for config in configurations:
        N = config['N']
        f = config['f']
        message_loss_rate = config['message_loss_rate']
        initial_ratio = config['initial_ratio']
        epsilon_value = config['epsilon']

        if N <= 3 * f:
            print(
                f"Invalid configuration for N={N} and f={f}: N must be greater than 3f.")
            continue

        print(f"Running simulation for configuration: {config}")
        num_repeats = int(input(
            f"How many times do you want to repeat the simulation for configuration {config}? "))

        rounds_results = []

        for repeat_index in range(num_repeats):
            print(
                f"\n--- Running Repeat {repeat_index + 1} for Configuration {config} ---")
            final_outputs, rounds_to_reach_consensus = consensus_simulation(
                N, total_rounds=10, message_loss_rate=message_loss_rate, epsilon_value=epsilon_value, f=f
            )

            # Store number of rounds it took for each vehicle to complete consensus (ABC)
            # vehicle_rounds = [{"vehicle_id": vehicle.vehicle_id,
            #    "rounds_to_complete": rounds_to_reach_consensus} for vehicle in vehicles]

            rounds_results.append(rounds_to_reach_consensus)

            # Print for each repeat
            print(
                f"Rounds to reach consensus for repeat {repeat_index + 1}: {rounds_to_reach_consensus}")

        # Calculate average and 99th percentile for this configuration
        average_rounds = np.mean(rounds_results)
        percentile_99 = np.percentile(rounds_results, 99)

        result = {
            'configuration': config,
            'average_rounds': average_rounds,
            '99th_percentile_rounds': percentile_99,
            'all_rounds': rounds_results,
            # 'vehicle_data_per_run': vehicle_rounds
        }

        results.append(result)

        # Print results for this configuration
        print(
            f"\nResults for Configuration: N={N}, f={f}, message_loss_rate={message_loss_rate}, initial_ratio={initial_ratio}")
        print(f"Average Rounds to Reach Consensus: {average_rounds}")
        print(f"99th Percentile Rounds to Reach Consensus: {percentile_99}")
        print(f"All Rounds to Reach Consensus: {rounds_results}\n")

    # json_file.save_results_to_json(results, output_file)
        json_file.save_results_to_json(results, output_file)


# Define configurations
# initial ratio (1:0)
configurations = [
    {'N': 8, 'f': 1, 'message_loss_rate': 0.4,
        'initial_ratio': 0.5, 'epsilon': 0.01},
    # Add more configurations as needed
]

# Run simulations and store results
run_simulations_and_store_results(
    configurations, output_file='simulation_results.json')
