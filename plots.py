import matplotlib.pyplot as plt
import numpy as np


def grouped_bar_plot(x_labels, values, y_label):

    x = np.arange(len(x_labels))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize = (12,7))

    for attribute, measurement in values.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(y_label)
    ax.set_xlabel('System Configuration')
    ax.set_title('System Performance')
    ax.set_xticks(x + width, x_labels)
    ax.legend(loc='upper left', ncol=3)
    ax.set_ylim(0, 20)

    plt.show()


x_labels = ("Capacity = 1\nDifficulty = 4", "Capacity = 1\nDifficulty = 5",
           "Capacity = 5\nDifficulty = 4", "Capacity = 5\nDifficulty = 5",
           "Capacity = 10\nDifficulty = 4", "Capacity = 10\nDifficulty = 5")

throughput_values = {
    'Five Nodes': [4.6612, 10.8255, 11.7791, 5.2462, 8.1247, 9.6092],
    'Ten Nodes': [5.4537, 9.5058, 8.9738, 5.1375, 7.8731, 9.1134]

}
y_label = "Throughput"
grouped_bar_plot(x_labels, throughput_values, y_label)

block_time_values = {
    'Five Nodes': [0.3662, 1.1069, 2.9747, 3.7575, 10.0786, 12.6148],
    'Ten Nodes': [0.2987, 1.1442, 2.2790, 1.9135, 7.6191, 11.5736]

}
y_label = "Block Time"
grouped_bar_plot(x_labels, block_time_values, y_label)



