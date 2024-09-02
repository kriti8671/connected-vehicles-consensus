import json
import matplotlib.pyplot as plt


json_file_path = 'simulation_results_sept2.json'

with open(json_file_path, 'r') as file:
    data = json.load(file)

# Extract relevant data
configurations = []
average_rounds = []

for entry in data:
    config = entry['configuration']
    N = config['N']  # Extract the number of vehicles N
    # Extract the average rounds to reach consensus
    avg_rounds = entry['summary']['average_rounds']

    configurations.append(f"N={N}")
    average_rounds.append(avg_rounds)

# Create a bar plot
plt.figure(figsize=(10, 6))
plt.bar(configurations, average_rounds, color='skyblue')
plt.xlabel('Configuration (Number of Vehicles, N)')
plt.ylabel('Average Rounds to Reach Consensus')
plt.title('Average Rounds to Reach Consensus for Different Vehicle Numbers (N)')
plt.grid(axis='y', linestyle='--')

# Display the graph
plt.show()
