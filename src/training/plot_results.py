import sys
import os
import matplotlib.pyplot as plt
import json

def generate_training_graph(history_file='training_history.json', output_file='training_results.png'):
    if not os.path.exists(history_file):
        print("No history found.")
        return

    with open(history_file, 'r') as f:
        history = json.load(f)

    if not history:
        print("Empty history.")
        return

    # Extract data
    timestamps = [entry['timestamp'] for entry in history]
    accuracies = [entry['overall_accuracy'] for entry in history]

    # Plot Overall Accuracy Trend
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, accuracies, marker='o', linestyle='-', color='b', label='Overall Accuracy')

    plt.title('Training Accuracy Evolution')
    plt.xlabel('Evaluation Run')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 100)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(output_file)
    print(f"History graph saved to {output_file}")

    # Also plot the latest class breakdown
    latest = history[-1]
    class_metrics = latest.get('class_metrics', {})

    if class_metrics:
        plt.figure(figsize=(10, 6))
        classes = list(class_metrics.keys())
        scores = list(class_metrics.values())

        bars = plt.bar(classes, scores, color='green')
        plt.title(f"Latest Class Accuracy ({latest['timestamp']})")
        plt.ylim(0, 100)
        plt.ylabel('Accuracy (%)')

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig('latest_class_accuracy.png')
        print("Latest class accuracy saved to latest_class_accuracy.png")

if __name__ == "__main__":
    generate_training_graph()
