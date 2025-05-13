import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os


def fetch_data_from_json(json_file, algorithm_name):
    """
    Fetch data from a JSON file and structure it for plotting.
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract relevant data: loss rates and rounds
    loss_rates = [entry['message_loss_rate'] *
                  100 for entry in data]  # Convert to percentage
    rounds = [entry['rounds'] for entry in data]

    # Combine data with algorithm name
    structured_data = pd.DataFrame({
        'Message Loss Rate': loss_rates,
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
    # 2ca02c, #1f77b4	,ff7f0e, d62728
    # custom_colors = ['#4C72B0', '#55A868', '#C44E52']  # Blue, Green, Red
    custom_colors = ['#1f77b4', '#2ca02c', '#d62728']


    # Plot using Seaborn
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Message Loss Rate', y='Rounds to Convergence',
                hue='Algorithm', data=combined_data, palette=custom_colors)
    # y_min = combined_data['Rounds to Convergence'].min() + \
    #     2  # Decrease lower limit
    # y_max = combined_data['Rounds to Convergence'].max() + \
    #     2  # Increase upper limit
    # plt.ylim(y_min, y_max)
    plt.ylim(0, 70)
    plt.yticks(range(0, 70, 10))
    # Add titles and labels
    # Updated x-axis label to indicate percentage
    plt.xlabel('Message Loss Rate (%)')
    plt.ylabel('Rounds to Convergence')

    # Show the legend
    plt.legend(loc='upper left')

    # Display the plot
    # plt.show()


    # Define the output path
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn't exist

    # Save the figure
    output_path = os.path.join(output_dir, 'Rounds_vs_MesageLoss.png')
    plt.savefig(output_path, dpi=300)

    print(f"Plot saved at: {output_path}")


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
