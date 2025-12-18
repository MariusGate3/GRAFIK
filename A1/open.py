import numpy as np
import matplotlib.pyplot as plt

# 1. Define House Geometry
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

def lookAt(eye, center, up):
    F = center - eye
    f = normalize(F)
    UP = normalize(up)
    s = normalize(np.cross(f, UP))
    u = np.cross(s, f)
    
    M = np.eye(4)
    M[0, :3] = s
    M[1, :3] = u
    M[2, :3] = -f
    
    T = np.eye(4)
    T[:3, 3] = -eye
    return M @ T

def frustum(l, r, b, t, n, f):
    M = np.zeros((4, 4))
    M[0, 0] = 2 * n / (r - l)
    M[0, 2] = (r + l) / (r - l)
    M[1, 1] = 2 * n / (t - b)
    M[1, 2] = (t + b) / (t - b)
    M[2, 2] = -(f + n) / (f - n)
    M[2, 3] = -2 * f * n / (f - n)
    M[3, 2] = -1
    return M

def compute_opengl_matrices(VRP, VPN, VUP, PRP, window):
    n_vec = normalize(VPN)
    u_vec = normalize(np.cross(VUP, n_vec))
    v_vec = np.cross(n_vec, u_vec)
    
    prp_world = VRP + (u_vec * PRP[0]) + (v_vec * PRP[1]) + (n_vec * PRP[2])
    
    eye = prp_world
    

    center = eye - n_vec
    

    up = VUP
    
    V = lookAt(eye, center, up)

    near = PRP[2]
    far = near + 200.0
    
    umin, umax, vmin, vmax = window
    
    l = umin - PRP[0]
    r = umax - PRP[0]
    b_val = vmin - PRP[1]
    t_val = vmax - PRP[1]
    
    P = frustum(l, r, b_val, t_val, near, far)
    
    return P @ V

# --- Plotting ---
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
    
    MVP = compute_opengl_matrices(np.array(p['VRP']), np.array(p['VPN']), np.array(p['VUP']), np.array(p['PRP']), p['window'])
    
    clip = MVP @ vertices
    
    # Perspective Divide
    w = clip[3, :]
    w[np.abs(w) < 1e-9] = 1e-9
    x = clip[0, :] / w
    y = clip[1, :] / w
    
    for e in edges:
        ax.plot([x[e[0]], x[e[1]]], [y[e[0]], y[e[1]]], 'k-')
        
    ax.set_title(f"Figure {key} (OpenGL)")
    ax.set_aspect('equal')
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()