import json
import matplotlib.pyplot as plt

# Load data from the saved JSON file
with open('all_simulation_results.json', 'r') as f:
    all_simulation_data = json.load(f)

# Extract rounds to reach consensus for each configuration
rounds_data_by_config = {}

for simulation in all_simulation_data:
    sim_id = simulation['simulation_id']
    # Using 'N' as the key for each configuration
    config_key = f"Config {sim_id.split('_')[0]}"

    # Initialize the list for this config if not already
    if config_key not in rounds_data_by_config:
        rounds_data_by_config[config_key] = []

    # Append the number of rounds to reach consensus for this simulation
    rounds_data_by_config[config_key].append(
        simulation['rounds_to_reach_consensus'])

# Prepare data for plotting
config_labels = []
rounds_to_plot = []

for config_key, rounds in rounds_data_by_config.items():
    config_labels.append(config_key)
    rounds_to_plot.append(rounds)

# Create the box plot
plt.figure(figsize=(10, 6))
plt.boxplot(rounds_to_plot, labels=config_labels, patch_artist=True,
            boxprops=dict(facecolor='lightblue', color='black'),
            whiskerprops=dict(color='black'),
            capprops=dict(color='black'),
            medianprops=dict(color='red'))

# Add labels and title
plt.title('Distribution of Rounds to Reach Consensus for Each Configuration')
plt.xlabel('Configuration')
plt.ylabel('Rounds to Reach Consensus')
plt.grid(True)

# Save and show plot
plt.savefig('rounds_to_reach_consensus_boxplot.png')
plt.show()
