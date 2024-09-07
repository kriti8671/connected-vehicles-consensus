import random


class Vehicle:
    def __init__(self, vehicle_id, initial_state, epsilon, is_byzantine=False):
        self.vehicle_id = vehicle_id
        self.initial_state = initial_state
        self.current_state = initial_state
        self.epsilon = epsilon
        self.is_byzantine = is_byzantine
        self.received_states = {}

# TODO:
# Implement additional Byzantine strategies for more realistic fault simulation

    def broadcast_state(self, all_vehicles, message_loss_rate):
        message_losses = 0  # Initialize counter for message losses
        if self.is_byzantine:
            print(
                f"Byzantine Vehicle {self.vehicle_id} broadcasting inconsistent states.")
            for vehicle in all_vehicles:
                if vehicle.vehicle_id != self.vehicle_id:
                    if random.random() > message_loss_rate:
                        # Send inconsistent states
                        state_to_send = random.choice([0, 1])
                        print(
                            f"Byzantine Vehicle {self.vehicle_id} sent state {state_to_send} to Vehicle {vehicle.vehicle_id}.")
                        vehicle.receive_state(self.vehicle_id, state_to_send)
                    else:
                        print(
                            f"Message from Byzantine Vehicle {self.vehicle_id} to Vehicle {vehicle.vehicle_id} lost due to message loss.")
                        message_losses += 1  # Increment for each lost message
        else:
            print(
                f"Vehicle {self.vehicle_id} broadcasting state {self.current_state} to all other vehicles.")
            for vehicle in all_vehicles:
                if vehicle.vehicle_id != self.vehicle_id:
                    if random.random() > message_loss_rate:
                        vehicle.receive_state(
                            self.vehicle_id, self.current_state)
                    else:
                        print(
                            f"Message from Vehicle {self.vehicle_id} to Vehicle {vehicle.vehicle_id} lost due to message loss.")
                        message_losses += 1  # Increment for each lost message

        return message_losses  # Return total message losses for this broadcast

    def receive_state(self, sender_id, state):
        """Receive state from another vehicle."""
        print(
            f"Vehicle {self.vehicle_id} received state {state} from Vehicle {sender_id}.")
        self.received_states[sender_id] = state

    def update_state(self, total_vehicles, f):
        """Update the vehicle's state based on received messages."""
        all_states = [self.current_state] + list(self.received_states.values())
        print(
            f"Vehicle {self.vehicle_id} has all states: {[f'{state}' for state in all_states]}")

        missing_states_count = total_vehicles - len(all_states)
        all_states.extend([self.current_state] * missing_states_count)
        print(
            f"Vehicle {self.vehicle_id} after filling missing states: {[f'{state}' for state in all_states]}")

        trimmed_states = self.trim_states(all_states, f)
        print(
            f"Vehicle {self.vehicle_id} trimmed states: {[f'{state}' for state in trimmed_states]}")

        self.current_state = sum(trimmed_states) / len(trimmed_states)
        print(
            f"Vehicle {self.vehicle_id} updated state: {self.current_state}")

        self.received_states.clear()

    def trim_states(self, all_states, f):
        """Trim the sorted list of states to remove f smallest and f largest values."""
        sorted_states = sorted(all_states)
        trimmed_states = sorted_states[f:-f]
        return trimmed_states

# Changes this functionn
    def decide_final_output(self, consensus_state):
        """Decide final output based on consensus state and vehicle's current state."""
        if abs(self.current_state - consensus_state) <= self.epsilon:
            # Vehicle's state is within the consensus range
            if consensus_state >= 0.5:
                print(f"Vehicle {self.vehicle_id} final decision: 1")
                return 1
            else:
                print(f"Vehicle {self.vehicle_id} final decision: 0")
                return 0
        else:
            # Vehicle's state is far from consensus, mark as None
            print(f"Vehicle {self.vehicle_id} final decision: None")
            return None

