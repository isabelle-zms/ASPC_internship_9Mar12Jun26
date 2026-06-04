import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

FREQUENCY = 868000000
WAVELENGTH = (300000000)/FREQUENCY

def frensel_zone(node1, node2):
    x1, y1 = node1.x, node1.y
    x2, y2 = node2.x, node2.y
    print(x1, y1, x2, y2)
    d = ((x1-x2) ** 2 + (y1-y2) ** 2) ** 0.5
    midpt = ((x1+x2)/2, (y1+y2)/2)
    fresnel_r = 0.5 * (WAVELENGTH * d) ** 0.5
    ellipse_angle = (math.atan((y2-y1)/(x2-x1)))/math.pi * 180
    fresnel_1_patch = patches.Ellipse(midpt, d, fresnel_r * 2, ellipse_angle, edgecolor='r', fc='None', lw=1, alpha=0.4)
    return fresnel_1_patch

class Node():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Graph():
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
    
    def show_frensel_zone_1(self, node1, node2):
        self.ax.add_patch(frensel_zone(node1, node2))
    
    def show_node_marker(self, node):
        circle = plt.Circle(
            (node.x, node.y),
            radius=0.2,
            alpha=0.9
        )
        self.ax.add_patch(circle)

    def show_LOS(self, node1, node2):
        self.ax.plot([node1.x, node2.x], [node1.y, node2.y], ls='--')

    def show(self):
        plt.show()

nodeA = Node(1, 1)
nodeB = Node(4, 2)
graph = Graph()
graph.show_frensel_zone_1(nodeA, nodeB)
graph.show_node_marker(nodeA)
graph.show_node_marker(nodeB)
graph.show_LOS(nodeA, nodeB)
graph.show()

