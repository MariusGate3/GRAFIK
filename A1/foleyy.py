import numpy as np
import matplotlib.pyplot as plt

# 1. Define House Geometry (Homogeneous Coordinates)
vertices = np.array([
    [0, 0, 54, 1],   [16, 0, 54, 1],  [16, 10, 54, 1], [8, 16, 54, 1], [0, 10, 54, 1], 
    [0, 0, 30, 1],   [16, 0, 30, 1],  [16, 10, 30, 1], [8, 16, 30, 1], [0, 10, 30, 1]
]).T 

edges = [
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 0), 
    (5, 6), (6, 7), (7, 8), (8, 9), (9, 5), 
    (0, 5), (1, 6), (2, 7), (3, 8), (4, 9) 
]

def normalize(v):
    norm = np.linalg.norm(v)
    return v if norm == 0 else v / norm

def compute_MVP(VRP, VPN, VUP, PRP, window):

    n = normalize(VPN)
    u = normalize(np.cross(VUP, n))
    v = np.cross(n, u)
    
    R = np.eye(4)
    R[0, :3], R[1, :3], R[2, :3] = u, v, n
    
    T_vrp = np.eye(4)
    T_vrp[:3, 3] = -VRP
    
    V = R @ T_vrp


    T_prp = np.eye(4)
    T_prp[:3, 3] = -PRP
    

    umin, umax, vmin, vmax = window
    cw_u = (umin + umax) / 2.0
    cw_v = (vmin + vmax) / 2.0
    
    dop_x = cw_u - PRP[0]
    dop_y = cw_v - PRP[1]
    dop_z = -PRP[2]
    
    SH = np.eye(4)
    SH[0, 2] = -dop_x / dop_z
    SH[1, 2] = -dop_y / dop_z


    S = np.eye(4)
    S[0, 0] = 2.0 / (umax - umin)
    S[1, 1] = 2.0 / (vmax - vmin)
    S[2, 2] = 1.0 
    
    M = np.eye(4)
    M[3, 2] = -1.0 / PRP[2] 
    M[3, 3] = 0

    P = M @ S @ SH @ T_prp
    return P @ V

params = {
    "6.27": { "VRP": [0,0,0], "VPN": [0,0,1], "VUP": [0,1,0], "PRP": [8,6,84], "window": [-50,50,-50,50] },
    "6.28": { "VRP": [0,0,54], "VPN": [0,0,1], "VUP": [0,1,0], "PRP": [8,6,30], "window": [-1,17,-1,17] },
    "6.31": { "VRP": [16,0,54], "VPN": [0,0,1], "VUP": [0,1,0], "PRP": [20,25,20], "window": [-20,20,5,35] },
    "6.34": { "VRP": [16,0,54], "VPN": [1,0,1], "VUP": [-0.17, 0.98, 0], "PRP": [0,25,28.28], "window": [-20,20,5,35] }
}

fig, axes = plt.subplots(2, 2, figsize=(10, 10))
keys = list(params.keys())

for idx, key in enumerate(keys):
    ax = axes[idx//2, idx%2]
    p = params[key]
    
    MVP = compute_MVP(np.array(p['VRP']), np.array(p['VPN']), np.array(p['VUP']), np.array(p['PRP']), p['window'])
    clip = MVP @ vertices
    
    w = clip[3, :]

    x = clip[0, :] / w
    y = clip[1, :] / w
    
    for e in edges:
        ax.plot([x[e[0]], x[e[1]]], [y[e[0]], y[e[1]]], 'k-')
        
    ax.set_title(f"Figure {key}")
    ax.set_aspect('equal')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()