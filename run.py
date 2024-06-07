import os.path

import numpy as np
import tslabeller as tsl

tslw = tsl.TimeSeriesLabellerWindow()
tslw.set_default_save_path(os.path.join(".", "test.npy"))
ax = tslw.get_ax()

x_for_labelling = np.linspace(0, 16.3, 15) + 7.5
data_for_labelling = np.random.rand(15)

additional_x = np.linspace(0, 30, 30)
additional_data = np.sin(2 * np.pi * additional_x) / 2 + 0.5

ax.plot(additional_x, additional_data, label="sin", color="red", linestyle="--")
ax.plot(x_for_labelling, data_for_labelling, label="rand", color="blue", marker='o')
ax.legend()

tslw.load_target_data(x_for_labelling, data_for_labelling)
tslw.show()

if os.path.exists('test.npy'):
    with open('test.npy', 'rb') as f:
        a = np.load(f)
        print(a.shape)
        print(np.unique(a, return_counts=True))
