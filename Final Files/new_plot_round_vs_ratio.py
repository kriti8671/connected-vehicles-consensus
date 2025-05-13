import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os


def fetch_data_from_json(json_file, algorithm_name):
    with open(json_file, 'r') as f:
        data = json.load(f)

    ratio = [entry['initial_ratio'] * 100 for entry in data]
    rounds = [entry['rounds'] for entry in data]

    return pd.DataFrame({
        'Initial Ratio': ratio,
        'Rounds to Convergence': rounds,
        'Algorithm': algorithm_name
    })


def plot_combined_rounds_vs_loss_rate(json_files):
    combined_data = pd.DataFrame()

    for json_file, algorithm_name in json_files:
        combined_data = pd.concat(
            [combined_data, fetch_data_from_json(json_file, algorithm_name)],
            ignore_index=True
        )

    sns.set(style="whitegrid")

    custom_colors = ['#1f77b4', '#2ca02c', '#d62728']
    algorithm_order = combined_data['Algorithm'].unique()
    ratio_order = sorted(combined_data['Initial Ratio'].unique())

    # Ensure consistent order
    combined_data['Initial Ratio'] = pd.Categorical(combined_data['Initial Ratio'], categories=ratio_order, ordered=True)

    plt.figure(figsize=(10, 6))
    ax = sns.boxplot(
        x='Initial Ratio',
        y='Rounds to Convergence',
        hue='Algorithm',
        data=combined_data,
        palette=custom_colors,
        linewidth=1.5
    )

    # Calculate and plot mean line for each algorithm
    grouped_means = (
        combined_data
        .groupby(['Algorithm', 'Initial Ratio'])['Rounds to Convergence']
        .mean()
        .reset_index()
    )

    # Get the x-tick positions from the boxplot
    positions = {val: idx for idx, val in enumerate(ratio_order)}

    for algo, color in zip(algorithm_order, custom_colors):
        algo_means = grouped_means[grouped_means['Algorithm'] == algo]
        x = [positions[val] for val in algo_means['Initial Ratio']]
        y = algo_means['Rounds to Convergence']
        ax.plot(x, y, color=color, marker='o', linewidth=2, label=f"{algo} (mean)")

    plt.ylim(0, 21)
    plt.yticks(range(0, 21, 3))
    plt.xlabel('Initial Ratio (%)')
    plt.ylabel('Rounds to Convergence')

    # Handle legend (avoid duplication)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper left', fontsize=9)

    plt.tight_layout()

    output_dir = os.path.join(os.path.dirname(__file__), '..', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'Rounds_vs_Ratio_10%Messageloss_10runs_box_line.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved at: {output_path}")
    plt.show()


if __name__ == "__main__":
    json_files = [
        ('DAC_Algorithm_Results.json', 'DAC'),
        ('Early-DAC_AlgoResults.json', 'Early-DAC'),
        ('Tunable_Early-DAC(5)_AlgoResults.json', 'Tunable Early-DAC(5)')
    ]

    plot_combined_rounds_vs_loss_rate(json_files)
