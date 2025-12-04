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
    dt = 0.001  # tidssteg (gir god nøyaktighet)
    
    # Startbetingelser
    v = mv
    x = 0
    y = 0
    time = 0

    # Juster siktelinje for å treffe på innskytingsavstand
    # Itererer små vinkler til vi treffer
    angle = 0.0
    for _ in range(200):
        test_v = mv
        test_x = 0
        test_y = 0
        test_time = 0
        angle += 0.0001  # radianer
        
        while test_x < zero_range:
            a, b = g7_drag_function(test_v)
            dvdt = -(a * (test_v**b)) / bc
            test_v += dvdt * dt
            test_time += dt
            
            test_x += test_v * dt * np.cos(angle)
            test_y += test_v * dt * np.sin(angle) - 0.5*g*(dt**2)

        if abs(test_y) < 0.01:  # nesten midt i blinken
            break

    # Faktisk løp
    distances = []
    drops = []
    velocities = []
    times = []

    v = mv
    x = 0
    y = 0
    time = 0

    while x <= max_range:
        distances.append(x)
        drops.append(y)
        velocities.append(v)
        times.append(time)

        a, b = g7_drag_function(v)
        dvdt = -(a * (v**b)) / bc
        v += dvdt * dt
        time += dt
        
        x += v * dt * np.cos(angle)
        y += v * dt * np.sin(angle) - 0.5*g*(dt**2)

    return np.array(distances), np.array(drops), np.array(times), np.array(velocities)


st.title("AmmoTrace – Kulebanekalkulator")

st.subheader("1. Oppgi data for skuddet")

# Input-felter for bruker
muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
bc = st.number_input("Ballistisk koeffisient (G1)", value=0.45)
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

