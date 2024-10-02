import json
import matplotlib.pyplot as plt

# Load data from JSON
with open('simulation_data_dac.json', 'r') as f:
    data = json.load(f)

# Extract message loss tracking data
message_loss_tracking = data['message_loss_tracking']
phase_progression = data['phase_progression']

# Plot Message Loss Over Rounds
plt.figure(figsize=(10, 6))
plt.plot(range(len(message_loss_tracking)), message_loss_tracking, marker='o')
plt.title('Message Loss Per Round')
plt.xlabel('Round')
plt.ylabel('Messages Lost')
plt.grid(True)
plt.savefig('message_loss_plot.png')
plt.show()

# Plot Phase Progression of Nodes Over Time
# plt.figure(figsize=(10, 6))
# for node_data in phase_progression:
#     for node in node_data:
#         if node['Phase'] != 'Crashed':
#             plt.scatter(node['Node'], node['Phase'],
#                         label=f"Node {node['Node']}")
# plt.title('Phase Progression of Nodes Over Time')
# plt.xlabel('Node ID')
# plt.ylabel('Phase')
# plt.grid(True)
# plt.savefig('phase_progression_plot.png')
# plt.show()
