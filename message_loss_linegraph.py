import json
import matplotlib.pyplot as plt

# Load data from the saved JSON file
with open('all_simulation_results.json', 'r') as f:
    all_simulation_data = json.load(f)

# Plot Message Loss Over Rounds for each configuration
plt.figure(figsize=(10, 6))

# Loop through each simulation and plot the message loss per round
for simulation in all_simulation_data:
    sim_id = simulation['simulation_id']
    message_loss_tracking = simulation['message_loss_tracking']

    # Plot message loss per round for this simulation
    plt.plot(range(len(message_loss_tracking)), message_loss_tracking,
             marker='o', label=f'Simulation {sim_id}')

# Add labels and title
plt.title('Message Loss Per Round for Each Simulation Configuration')
plt.xlabel('Round')
plt.ylabel('Messages Lost')
plt.grid(True)

# Add legend to differentiate between the simulations
plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1), title="Simulations")

# Save and show plot
plt.tight_layout()  # Adjust the plot layout to fit everything
plt.savefig('message_loss_per_round_linegraph.png')
plt.show()
