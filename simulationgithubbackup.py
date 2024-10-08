import random
import numpy as np
import json_file
from vehicles import Vehicle


def consensus_simulation(total_vehicles, total_rounds, message_loss_rate, epsilon_value, f, byzantine_vehicles=None):
    # Initialize vehicles with given parameters
    vehicles = [
        Vehicle(
            vehicle_id=i,
            initial_state=random.randint(0, 1),
            epsilon=epsilon_value,
            is_byzantine=(i in byzantine_vehicles)
        ) for i in range(total_vehicles)
    ]

    message_losses_per_round = []  # Initialize list to track message losses per round
    inconclusive_count = 0
    final_decisions = []  # Initialize list to track final decisions
    rounds_to_reach_consensus = None

    # Simulate rounds of message passing and state updating
    for current_round in range(total_rounds):
        print(f"\n--- Round {current_round + 1} ---")
        round_message_losses = 0  # Initialize counter for message losses in this round
        inconclusive_count = 0  # Initialize counter for inconclusive decisions

        # Each vehicle broadcasts its state to all other vehicles
        for vehicle in vehicles:
            # Count message losses for each vehicle and add to the round's total
            round_message_losses += vehicle.broadcast_state(
                vehicles, message_loss_rate)

        # Record message losses for the round
        message_losses_per_round.append(round_message_losses)

        # Update state for each vehicle
        for vehicle in vehicles:
            vehicle.update_state(total_vehicles, f)

        # **After each round**, check for convergence among correct vehicles
        correct_vehicle_states = [
            v.current_state for v in vehicles if not v.is_byzantine]
        if max(correct_vehicle_states) - min(correct_vehicle_states) <= epsilon_value:
            rounds_to_reach_consensus = current_round + 1
            print(f"Consensus reached at round {rounds_to_reach_consensus}")
            break

    else:

        # If no convergence is reached within the total rounds
        print("Consensus not reached within the specified rounds.")

    # **After** the for-loop ends, decide the final output for each vehicle
    final_decisions = []
    for vehicle in vehicles:
        decision = vehicle.decide_final_output()
        final_decisions.append(decision)
        if decision is None:
            inconclusive_count += 1

    # Prepare the results dictionary to return
    return {
        'rounds_to_reach_consensus': rounds_to_reach_consensus,
        'initial_binary_states': [vehicle.initial_state for vehicle in vehicles],
        'inconclusive_counts': inconclusive_count,
        'message_losses_per_round': message_losses_per_round,
        'final_decisions': [final_decisions]
    }


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

        runs_data = []

        for repeat_index in range(num_repeats):
            print(
                f"\n--- Running Repeat {repeat_index + 1} for Configuration {config} ---")
            result = consensus_simulation(
                N, total_rounds=10, message_loss_rate=message_loss_rate,
                epsilon_value=epsilon_value, f=f, byzantine_vehicles=random.sample(
                    range(N), f)
            )

            run_result = {
                'run_number': repeat_index + 1,
                'rounds_to_reach_consensus': result['rounds_to_reach_consensus'],
                'initial_binary_states': result['initial_binary_states'],
                'inconclusive_outputs': result['inconclusive_counts'],
                'message_losses_per_round': result['message_losses_per_round'],
                'final_decisions': result['final_decisions']
            }

            runs_data.append(run_result)
            print(
                f"Rounds to reach consensus for repeat {repeat_index + 1}: {result['rounds_to_reach_consensus']}")

        all_rounds = [run['rounds_to_reach_consensus'] for run in runs_data]
        # average_rounds = np.mean(all_rounds)
        # percentile_99 = np.percentile(all_rounds, 99)
        # Filter out None values from all_rounds
        valid_rounds = [round for round in all_rounds if round is not None]

        # Calculate average and 99th percentile only for valid rounds
        average_rounds = np.mean(valid_rounds) if valid_rounds else None
        percentile_99 = np.percentile(
            valid_rounds, 99) if valid_rounds else None

        result_summary = {
            'configuration': config,
            'summary': {
                'average_rounds': average_rounds,
                '99th_percentile_rounds': percentile_99
            },
            'runs': runs_data
        }

        results.append(result_summary)

        print(
            f"\nResults for Configuration: N={N}, f={f}, message_loss_rate={message_loss_rate}, initial_ratio={initial_ratio}")
        print(f"Average Rounds to Reach Consensus: {average_rounds}")
        print(f"99th Percentile Rounds to Reach Consensus: {percentile_99}")
        print(f"All Rounds to Reach Consensus: {all_rounds}\n")

    json_file.save_result_to_json(results, output_file)


configurations = [

    {'N': 20, 'f': 5, 'message_loss_rate': 0.7,
        'initial_ratio': 0.7, 'epsilon': 0.01},

    # {'N': 20, 'f': 1, 'message_loss_rate': 0.1,
    #     'initial_ratio': 0.7, 'epsilon': 0.01},

    # {'N': 25, 'f': 1, 'message_loss_rate': 0.1,
    #     'initial_ratio': 0.7, 'epsilon': 0.01}

]

run_simulations_and_store_results(
    configurations, output_file='simulation_results.json')
