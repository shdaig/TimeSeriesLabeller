import numpy as np
import tslabeller.tslabeller as tsl

tslw = tsl.TimeSeriesLabellerWindow()
ax = tslw.get_ax()

x = np.linspace(0, 500, 500)
main_array = np.random.rand(500)
additional_array = np.sin(2 * np.pi * x) / 2 + 0.5
ax.plot(x, main_array, label="rand", color="blue")
ax.plot(x, additional_array, label="sin", color="red")
ax.legend()

tslw.load_axis_data(x, main_array)
tslw.root.mainloop()

with open('test.npy', 'rb') as f:
    a = np.load(f)
    print(a.shape)
    print(np.unique(a, return_counts=True))
