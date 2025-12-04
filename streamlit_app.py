import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("Kulebanekalkulator")

st.subheader("Inndata")

muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)
max_range = 500  # for graf

g = 9.81  # gravitasjon

def simple_drop(mv, zero, max_range=500, step=1):
    distances = np.arange(0, max_range + step, step)
    drops = []

    for x in distances:
        time = x / mv
        drop = 0.5 * g * time**2
        drops.append(drop)

    # korriger slik at drop = 0 på innskyting
    zero_drop = drops[int(zero)]
    drops = np.array(drops) - zero_drop

    return distances, drops


if st.button("Beregn kulebane"):
    dist, drop = simple_drop(muzzle_velocity, zero_range, max_range)

    drop_cm = drop * 100
    idx = np.argmin(abs(dist - target_range))

    st.write(f"**Fall ved {target_range} m:** {drop_cm[idx]:.1f} cm")

    # --- Graf ---
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)
    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Fall (cm)")
    ax.set_title("Kulebane (uten drag)")
    ax.grid(True)
    st.pyplot(fig)
