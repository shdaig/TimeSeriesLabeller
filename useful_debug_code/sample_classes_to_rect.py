import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Маски для каждого из каналов на 4 класса. Размерность каждого: (500,)
class_mask_cxf = np.array([2 for i in range(100)] + [-1 for i in range(50)] + [1 for i in range(250)] + [0 for i in range(100)])
class_mask_cxl = np.array([2 for i in range(50)] + [-1 for i in range(150)] + [1 for i in range(200)] + [0 for i in range(100)])
class_mask_htl = np.array([2 for i in range(200)] + [-1 for i in range(50)] + [1 for i in range(250)])
class_mask_hcm = np.array([2 for i in range(150)] + [1 for i in range(200)] + [0 for i in range(150)])

# Цвета для классов
colors = {-1: 'gray', 0: 'red', 1: 'blue', 2: 'green'}

# Соберем все маски в единый массив. Размерность: (4, 500)
channel_masks = np.vstack((class_mask_cxf, class_mask_cxl, class_mask_htl, class_mask_hcm))
print(f"channel_masks shape: {channel_masks.shape}")


def get_coords_for_classes(channel_masks: np.ndarray) -> tuple[list, list]:
    channel_coords = []
    channel_classes = []
    for channel in channel_masks:
        coords = []
        classes = []
        coords.append(0)
        classes.append(channel[0])
        i = 1
        while i < len(channel):
            if channel[i] != classes[-1]:
                coords.append(i)
                classes.append(channel[i])
            i += 1
        coords.append(i-1)
        classes.append(channel[i-1])
        channel_coords.append(coords)
        channel_classes.append(classes)
    return channel_coords, channel_classes


channel_coords, channel_classes = get_coords_for_classes(channel_masks)
print(f"channel_coords: {channel_coords}")
print(f"channel_classes: {channel_classes}")

fig, ax = plt.subplots(figsize=(10, 7))
for i in range(len(channel_coords)): # 4
    for j in range(len(channel_coords[i]) - 1):
        rectangle = Rectangle(xy=(channel_coords[i][j], 0.6 + i),
                              width=channel_coords[i][j + 1] - channel_coords[i][j],
                              height=0.8,
                              facecolor=colors[channel_classes[i][j]],
                              alpha=0.5)
        ax.add_patch(rectangle)
ax.set_xlim([0, 500])
ax.set_ylim([0, 5])
plt.show()
