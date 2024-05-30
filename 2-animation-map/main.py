import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.animation import FuncAnimation


coordinates = {
    "New York City": (-74.0060, 40.7128),
    "Los Angeles": (-118.2437, 34.0522)
}


fig, ax = plt.subplots()
plt.gcf().canvas.manager.set_window_title('New York to Los Angeles Flight Path Animation')

map = Basemap(projection='merc', llcrnrlat=25, urcrnrlat=50, llcrnrlon=-130, urcrnrlon=-65, resolution='i')
map.drawcoastlines(color='gray')
map.drawcountries(color='gray')
map.drawstates(color='gray')


x_start, y_start = map(*coordinates["New York City"])
x_end, y_end = map(*coordinates["Los Angeles"])


map.plot([x_start, x_end], [y_start, y_end], linestyle='--', linewidth=2, color='red')
plt.text(x_start, y_start, 'New York City', fontsize=12, ha='right', va='bottom', color='black')
plt.text(x_end, y_end, 'Los Angeles', fontsize=12, ha='right', va='bottom', color='black')


plane, = map.plot([], [], marker='.', markersize=10, color='blue')


def init():
    plane.set_data([], [])
    return plane,


def update(frame):
    if frame == 60:
        ani.event_source.stop()
    x_new = x_start + (x_end - x_start) * frame / 60
    y_new = y_start + (y_end - y_start) * frame / 60
    plane.set_data(x_new, y_new)
    return plane,


ani = FuncAnimation(fig, update, frames=np.linspace(0, 60, 61), init_func=init, blit=True)


plt.show()
