# foley.py
import numpy as np

VRP = np.array([0.0, 0.0, 0.0])
VPN = np.array([0.0, 0.0, 1.0])
VUP = np.array([0.0, 1.0, 0.0])

PRP = np.array([8.0, 6.0, 84.0])          # Fig. 6.27 [file:2]
umin, umax = -50.0, 50.0                  # window(VRC) [file:2]
vmin, vmax = -50.0, 50.0
F = 0.0
B = 100.0

def normalize(v):
    return v / np.linalg.norm(v)

def build_V():
    n = normalize(VPN)
    u = normalize(np.cross(VUP, n))
    v = np.cross(n, u)
    return np.array([
        [u[0], u[1], u[2], -np.dot(u, VRP)],
        [v[0], v[1], v[2], -np.dot(v, VRP)],
        [n[0], n[1], n[2], -np.dot(n, VRP)],
        [0.0,  0.0,  0.0,  1.0]
    ])

def build_P():
    # 1) translate PRP to origin
    T_prp = np.array([
        [1, 0, 0, -PRP[0]],
        [0, 1, 0, -PRP[1]],
        [0, 0, 1, -PRP[2]],
        [0, 0, 0, 1]
    ])

    # 2) shear – here window is symmetric so centre is (0,0) -> shear is 0
    u0 = (umin + umax) / 2.0   # = 0
    v0 = (vmin + vmax) / 2.0   # = 0
    shx = -u0 / PRP[2]         # = 0
    shy = -v0 / PRP[2]         # = 0

    SH = np.array([
        [1, 0, shx, 0],
        [0, 1, shy, 0],
        [0, 0,  1,  0],
        [0, 0,  0,  1]
    ])

    # 3) scale window to canonical [-1,1]x[-1,1], depth [0,1]
    du = umax - umin
    dv = vmax - vmin
    Sx = 2.0 / du
    Sy = 2.0 / dv
    Sz = 1.0 / (B - F)

    S = np.array([
        [Sx, 0,  0, -(umin + umax) * Sx / 2.0],
        [0,  Sy, 0, -(vmin + vmax) * Sy / 2.0],
        [0,  0,  Sz, -F * Sz],
        [0,  0,  0,  1]
    ])

    # 4) perspective term (like Foley’s final M)
    M = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 1/PRP[2], 0]
    ])

    return M @ S @ SH @ T_prp

def build_MVP():
    V = build_V()
    P = build_P()
    return P @ V
