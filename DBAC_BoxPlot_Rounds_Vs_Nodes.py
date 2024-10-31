import json
import matplotlib.pyplot as plt
import seaborn as sns

# Function to generate Rounds vs. Number of Nodes box plot


def plot_rounds_vs_nodes(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extracting data for the plot
    nodes = [entry['num_nodes'] for entry in data]
    rounds = [entry['rounds'] for entry in data]

    # Plotting the box plot
    sns.boxplot(x=nodes, y=rounds)
    plt.xlabel('Number of Nodes')
    plt.ylabel('Rounds to Convergence')
    plt.title('Rounds to Convergence vs Number of Nodes (DBAC)')
    plt.show()


# Call these functions as needed to generate the plots
if __name__ == "__main__":
    plot_rounds_vs_nodes('dbac_results.json')
