import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots()
fresnel_1_patch = patches.Ellipse((2, 1), 2, 1, 20)

ax.add_patch(fresnel_1_patch)

# Ensure the ellipse is visible by setting limits and aspect ratio
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_aspect('equal')
plt.show()