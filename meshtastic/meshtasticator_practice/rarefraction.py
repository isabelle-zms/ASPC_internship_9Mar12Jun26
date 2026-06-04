import numpy as np
import matplotlib.pyplot as plt

# Refractive indices
n1 = 1.0   # air
n2 = 1.5   # glass

# Plot
plt.figure(figsize=(8,5))

# Geometry
x1 = 0
x2 = 4
x3 = 7
block_bottom = 0
block_top = 8

def rarefraction(theta1, n1, n2, x0, y0):
    # Snell's Law
    theta2 = np.arcsin(n1/n2 * np.sin(theta1))

    # Incident point
    y1 = (x1 - x0) * np.tan(theta1) + y0

    # Exit point
    y2 = (x2 - x1) * np.tan(theta2) + y1

    # Future point
    y3 = (x3 - x2) * np.tan(theta1) + y2

    # Rays
    plt.plot([x0,  x1, x1, x2, x2, x3], [y0, y1, y1, y2, y2, y3], 'r', lw=0.5)

    if theta1 == np.radians(-15) or theta1 == np.radians(30):
        plt.fill([x0, x1, x2, x3, x3], [y0, y1, y2, y3, y0], alpha=0.3, color='red')

# Normals
# plt.axvline(entry_x, linestyle='--', color='gray')
# plt.axvline(exit_x, linestyle='--', color='gray')

# Draw block
plt.fill([x1, x2, x2, x1],
        [block_bottom, block_bottom, block_top, block_top],
        color='lightblue', alpha=0.3, label='Glass block')
for t1 in range(-15, 31):
    rarefraction(np.radians(t1), 1.0, 1.5, -3, 2)

plt.xlim(-3, 7)
plt.ylim(-1, 10)
plt.gca().set_aspect('equal', adjustable='box')
plt.legend()
plt.title("Refraction Through a Rectangular Glass Block")

plt.show()