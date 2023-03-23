import matplotlib.pyplot as plt
import numpy as np

x_labels = ("Capacity = 1\nDifficulty = 4", "Capacity = 1\nDifficulty = 5",
           "Capacity = 5\nDifficulty = 4", "Capacity = 5\nDifficulty = 5",
           "Capacity = 10\nDifficulty = 4", "Capacity = 10\nDifficulty = 5")
values = {
    'Five Nodes': [12.35, 12.35, 12.35, 12.35, 12.35,12.35],
    'Ten Nodes': [8.79, 8.79, 8.79, 8.79, 8.79, 8.79]

}

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
ax.set_ylabel('Throughput')
ax.set_xlabel('System Configuration')
ax.set_title('System Performance')
ax.set_xticks(x + width, x_labels)
ax.legend(loc='upper left', ncol=3)
ax.set_ylim(0, 20)

plt.show()