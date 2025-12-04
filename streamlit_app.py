import streamlit as st
import numpy as np
import math

def g7_drag_function(v):
    # Tabell for G7-drag etter Litz-modellen (forenklet men nøyaktig nok)
    # Intervaller (fps) + a og b-verdier
    # Konverterer til m/s med 1 fps = 0.3048 m/s
    drag_table = [
        (0, 423*0.3048,      0.2344, 1.30),
        (423*0.3048, 1700*0.3048, 0.1716, 1.55),
        (1700*0.3048, 2400*0.3048, 0.1278, 1.70),
        (2400*0.3048, 3300*0.3048, 0.0906, 1.90)
    ]

    for v_min, v_max, a, b in drag_table:
        if v_min <= v < v_max:
            return a, b

    return drag_table[-1][2], drag_table[-1][3]  # fallback

def compute_trajectory(mv, bc, zero_range, max_range=1000, step=1):
    g = 9.81
    
    # antall punkter
    n_steps = int(max_range / step) + 1

    # lister
    distances = np.linspace(0, max_range, n_steps)
    velocities = np.zeros(n_steps)
    drops = np.zeros(n_steps)
    times = np.zeros(n_steps)

    velocities[0] = mv
    y = 0
    t = 0

    # beregn vinkelen med enkel justering (lynrask)
    angle = 0.0
    for _ in range(50):
        y_test = 0
        v_test = mv
        for d in range(1, int(zero_range/step)):
            a, b = g7_drag_function(v_test)
            v_test -= (a * v_test**b / bc) * (step / v_test)
        if y_test > 0:
            angle -= 0.0001
        else:
            angle += 0.0001

    # hovedløp
    v = mv
    for i in range(1, n_steps):
        dx = distances[i] - distances[i-1]

        # drag
        a, b = g7_drag_function(v)
        dv = (a * v**b) / bc

        # oppdater hastighet og posisjon
        v -= dv * (dx / v)
        t += dx / v
        y -= g * (dx / v)**2 / 2  # vertikal bevegelse

        velocities[i] = v
        drops[i] = y
        times[i] = t

    # korriger drop slik at 0 cm ved innskyting
    zero_drop = drops[int(zero_range / step)]
    drops = drops - zero_drop

    return distances, drops, times, velocities




st.title("AmmoTrace – Kulebanekalkulator")

st.subheader("1. Oppgi data for skuddet")

# Input-felter for bruker
muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
bc = st.number_input("Ballistisk koeffisient (G7)", value=0.25)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)

if st.button("Beregn kulebane"):
    st.subheader("Kulebane beregnet med G7-drag")

    dist, drop, t, vel = compute_trajectory(
        muzzle_velocity,
        bc,
        zero_range,
        max_range=1000
    )

    # Konverter dråpe til cm
    drop_cm = drop * 100

    st.write(f"**Tid til {target_range} m:** {t[np.argmin(abs(dist-target_range))]:.3f} s")
    st.write(f"**Fall ved {target_range} m:** {drop_cm[np.argmin(abs(dist-target_range))]:.1f} cm")
    st.write(f"**Hastighet ved {target_range} m:** {vel[np.argmin(abs(dist-target_range))]:.1f} m/s")

    # Plot kulebanen
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)
    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Fall (cm)")
    ax.set_title("Kulebane (G7)")
    ax.grid(True)
    st.pyplot(fig)

