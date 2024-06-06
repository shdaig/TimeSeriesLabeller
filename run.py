import numpy as np
import tslabeller.tslabeller as tsl

tslw = tsl.TimeSeriesLabellerWindow()
ax = tslw.get_ax()

main_array = np.random.rand(500)
additional_array = np.sin(2 * np.pi * np.linspace(0, 500, 500)) / 2 + 0.5
ax.plot(main_array, label="rand", color="blue")
ax.plot(additional_array, label="sin", color="red")
ax.legend()

tslw.load_data(main_array)
tslw.root.mainloop()

with open('test.npy', 'rb') as f:
    a = np.load(f)
    print(a.shape)
    print(np.unique(a, return_counts=True))
