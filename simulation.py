import random

from vehicles import Vehicle


def consensus_simulation(total_vehicles, total_rounds, message_loss_rate, epsilon_value):

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
            vehicle.update_state(total_vehicles)

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


# Simulation parameters
TOTAL_VEHICLES = int(input("Enter Total Vehicles: "))
TOTAL_ROUNDS = int(input("Total rounds: "))
MESSAGE_LOSS_RATE = float(input("Message_loss_rate: "))  # % message loss rate
EPSILON_VALUE = 0.001

# Run the simulation
final_consensus_outputs, rounds_to_reach_consensus = consensus_simulation(
    TOTAL_VEHICLES, TOTAL_ROUNDS, MESSAGE_LOSS_RATE, EPSILON_VALUE)


# Display the final outputs of all vehicles
print("\nFinal Outputs of all vehicles:", final_consensus_outputs)
print(f"Rounds to reach consensus: {rounds_to_reach_consensus}")
