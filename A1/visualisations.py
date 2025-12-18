import numpy as np
import matplotlib.pyplot as plt
from foley import FoleyCamera  # Importing the class from foley.py

# --- 1. Define Geometry ---
vertices = np.array([
    [0, 0, 54, 1], [16, 0, 54, 1], [16, 10, 54, 1], [8, 16, 54, 1], [0, 10, 54, 1],
    [0, 0, 30, 1], [16, 0, 30, 1], [16, 10, 30, 1], [8, 16, 30, 1], [0, 10, 30, 1]
]).T

edges = [
    (0,1),(1,2),(2,3),(3,4),(4,0),
    (5,6),(6,7),(7,8),(8,9),(9,5),
    (0,5),(1,6),(2,7),(3,8),(4,9)
]

# --- 2. Define Parameters for Fig 6.27 ---
params = {
    "VRP": [0,0,0], 
    "VPN": [0,0,1], 
    "VUP": [0,1,0], 
    "PRP": [8,6,84], 
    "window": [-50,50,-50,50]
}

# --- 3. Initialize Camera & Get MVP ---
camera = FoleyCamera(**params)
MVP = camera.build_MVP()

# --- 4. Transform & Project ---
clip = MVP @ vertices
w = clip[3, :]
w[w == 0] = 1e-9 # Avoid divide by zero
ndc = clip[:3, :] / w 

x_ndc, y_ndc = ndc[0, :], ndc[1, :]

# --- 5. Viewport Mapping ---
# Map NDC [-1, 1] to Viewport [0, 1]
u_min, u_max = 0.0, 1.0
v_min, v_max = 0.0, 1.0

u = (x_ndc + 1) * 0.5 * (u_max - u_min) + u_min
# Use (y_ndc + 1) so -1 maps to 0 (bottom) and +1 maps to 1 (top)
v = (y_ndc + 1) * 0.5 * (v_max - v_min) + v_min 

# --- 6. Plot ---
plt.figure(figsize=(5,5))
for i, j in edges:
    plt.plot([u[i], u[j]], [v[i], v[j]], 'k-')

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.title("Figure 6.27")
plt.gca().set_aspect('equal', 'box')
plt.grid(True, alpha=0.3)
plt.show()