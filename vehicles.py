import random


class Vehicle:
    def __init__(self, vehicle_id, initial_state, epsilon=0.001):

        self.vehicle_id = vehicle_id  # Assign the unique identifier to the vehicle
        self.current_state = initial_state
        self.epsilon = epsilon  # Set the tolerance for ε-agreement
        self.received_states = {}  # Dictionary to store states received from other vehicles

    def broadcast_state(self, all_vehicles, message_loss_rate):

        print(
            f"Vehicle {self.vehicle_id} broadcasting state {self.current_state} to all other vehicles.")

        for vehicle in all_vehicles:
            if vehicle.vehicle_id != self.vehicle_id:  # Avoid sending a message to itself
                if random.random() > message_loss_rate:  # Simulate message loss with a probability

                    vehicle.receive_state(self.vehicle_id, self.current_state)
                else:
                    print(
                        f"Message from Vehicle {self.vehicle_id} to Vehicle {vehicle.vehicle_id} lost due to message loss.")

    def receive_state(self, sender_id, state):

        print(
            f"Vehicle {self.vehicle_id} received state {state} from Vehicle {sender_id}.")
        # Store the received state keyed by the sender's ID
        self.received_states[sender_id] = state

    def update_state(self, total_vehicles):

        # Step 1: Gather all received states including the vehicle's own state
        all_states = [self.current_state] + list(self.received_states.values())
        print(f"Vehicle {self.vehicle_id} has all states: {all_states}")

        # Step 2: Fill in missing states with the vehicle's own state
        missing_states_count = total_vehicles - len(all_states)
        all_states.extend([self.current_state] * missing_states_count)
        print(
            f"Vehicle {self.vehicle_id} after filling missing states: {all_states}")

        # Step 3: Sort and trim the list of states to remove outliers
        trimmed_states = self.trim_states(all_states)
        print(f"Vehicle {self.vehicle_id} trimmed states: {trimmed_states}")

        # Step 4: Update the state to the average of the trimmed states
        self.current_state = sum(trimmed_states) / len(trimmed_states)
        print(f"Vehicle {self.vehicle_id} updated state: {self.current_state}")

        # Clear the received states for the next round
        self.received_states.clear()

    def trim_states(self, all_states):

        sorted_states = sorted(all_states)  # Sorting

        trimmed_states = sorted_states[1:-1]  # remove first and last
        return trimmed_states

    def decide_final_output(self):

        if self.current_state < 0.5 - self.epsilon / 2:
            print(f"Vehicle {self.vehicle_id} final decision: 0")
            return 0
        elif self.current_state > 0.5 + self.epsilon / 2:
            print(f"Vehicle {self.vehicle_id} final decision: 1")
            return 1
        else:
            print(
                f"Vehicle {self.vehicle_id} final decision: None (inconclusive)")
            return None
