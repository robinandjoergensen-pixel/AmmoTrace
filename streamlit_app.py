import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("AmmoTrace – Enkel G7 Kulebanekalkulator")

# --- G7 drag modell (fps-basert, konvertert) ---
def g7_drag(v):
    drag_table = [
        (0, 423, 0.2344, 1.30),
        (423, 1700, 0.1716, 1.55),
        (1700, 2400, 0.1278, 1.70),
        (2400, 3300, 0.0906, 1.90),
    ]
    for vmin, vmax, a, b in drag_table:
        if vmin <= v < vmax:
            return a, b
    return drag_table[-1][2], drag_table[-1][3]

# --- Enkel G7-beregning uten vinkel-søk ---
def simple_g7_trajectory(mv, bc, max_range=1000, step=1):
    g = 9.81
    distances = np.arange(0, max_range + step, step)
    drops = []
    velocities = []
    times = []

    v = mv
    y = 0
    t = 0

    for x in distances:
        # drag i fps (konverter m/s → fps)
        v_fps = v / 0.3048
        a, b = g7_drag(v_fps)
        dv = (a * v_fps**b) / bc
        dv = dv * 0.3048  # tilbake til m/s

        # fall-modell (flat-fire)
        t += step / v
        y -= 0.5 * g * (step / v)**2

        v -= dv * (step / v)

        drops.append(y)
        velocities.append(max(v, 0))
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

