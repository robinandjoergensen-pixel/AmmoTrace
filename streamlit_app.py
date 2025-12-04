import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("AmmoTrace – Stabil G7 Kulebanekalkulator")

# --- G7 dragmodell ---
def g7_drag(v_fps):
    table = [
        (0, 423, 0.2344, 1.30),
        (423, 1700, 0.1716, 1.55),
        (1700, 2400, 0.1278, 1.70),
        (2400, 3300, 0.0906, 1.90),
    ]
    for vmin, vmax, a, b in table:
        if vmin <= v_fps < vmax:
            return a, b
    return table[-1][2], table[-1][3]


# --- Stabil og enkel G7 kulebane ---
def simple_g7_trajectory(mv, bc, max_range=1000, step=1):
    g = 9.81
    distances = np.arange(0, max_range + step, step)
    
    drops = []
    velocities = []
    times = []

    v = float(mv)
    y = 0.0
    t = 0.0

    for x in distances:

        # Drag (fps → m/s)
        v_fps = v / 0.3048
        a, b = g7_drag(v_fps)
        dv = (a * v_fps**b) / bc
        dv = dv * 0.3048  # tilbake til m/s

        # Oppdater hastighet
        if v > 0:
            v = float(v - dv * (step / v))
        else:
            v = 0.0

        # Oppdater tid
        if v > 0:
            t = float(t + step / v)

        # Oppdater høyde (flat-fire)
        if v > 0:
            y = float(y - 0.5 * g * (step / v)**2)

        drops.append(y)
        velocities.append(v)
        times.append(t)

    return distances, np.array(drops), np.array(times), np.array(velocities)


# --- UI ---
st.subheader("Inndata")

mv = st.number_input("Munningshastighet (m/s)", value=800)
bc = st.number_input("Ballistisk koeffisient (G7)", value=0.25)
target_range = st.number_input("Målavstand (meter)", value=300)

if st.button("Beregn kulebane"):
    dist, drop, t, vel = simple_g7_trajectory(mv, bc)

    drop_cm = drop * 100
    idx = np.argmin(abs(dist - target_range))

    st.write(f"**Fall ved {target_range} m:** {drop_cm[idx]:.1f} cm")
    st.write(f"**Tid til mål:** {t[idx]:.3f} s")
    st.write(f"**Resthastighet:** {vel[idx]:.1f} m/s")

    # --- Graf ---
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)
    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Fall (cm)")
    ax.set_title("Kulebane (forenklet G7)")
    ax.grid(True)
    st.pyplot(fig)

