import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def fetch_data_from_json(json_file, algorithm_name):
    """
    Fetch data from a JSON file and structure it for plotting.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract relevant data: loss rates and rounds
    num_nodes = [entry['num_nodes'] for entry in data]
    rounds = [entry['rounds'] for entry in data]

    # Combine data with algorithm name
    structured_data = pd.DataFrame({
        'Number of Nodes': num_nodes,
        'Rounds to Convergence': rounds,
        'Algorithm': algorithm_name
    })

    return structured_data


def plot_combined_rounds_vs_loss_rate(json_files):
    """
    Plot rounds to convergence vs message loss rate for multiple algorithms.
    """
    # Prepare the combined data for all algorithms
    combined_data = pd.DataFrame()

    for json_file, algorithm_name in json_files:
        # Fetch data for each algorithm
        algorithm_data = fetch_data_from_json(json_file, algorithm_name)
        # Append to the combined DataFrame
        combined_data = pd.concat(
            [combined_data, algorithm_data], ignore_index=True)

    # Set the Seaborn style
    sns.set(style="whitegrid")

    # Define custom colors for the algorithms
    custom_colors = ['#4C72B0', '#55A868', '#C44E52']  # Blue, Green, Red

    # Plot using Seaborn
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Number of Nodes', y='Rounds to Convergence',
                hue='Algorithm', data=combined_data, palette=custom_colors)

    y_min = combined_data['Rounds to Convergence'].min() - \
        2  # Decrease lower limit
    y_max = combined_data['Rounds to Convergence'].max() + \
        5  # Increase upper limit
    plt.ylim(y_min, y_max)
    # Add titles and labels
    plt.xlabel('Number of Nodes')
    plt.ylabel('Rounds to Convergence')
    # plt.title(
    #     'Rounds to Convergence vs Number of Nodes (Comparison of Algorithms)')

    # Show the legend
    plt.legend(loc='upper left')

    # Display the plot
    plt.show()


# Call these functions to generate the plot
if __name__ == "__main__":
    # List of JSON files and corresponding algorithm names
    json_files = [
        ('DAC_Algorithm_Results.json', 'DAC'),
        ('Early-DAC_AlgoResults.json', 'Early-DAC'),
        ('Tunable_Early-DAC(5)_AlgoResults.json',
         'Tunable Early-DAC(5)')
    ]

    # Generate the combined plot
    plot_combined_rounds_vs_loss_rate(json_files)
