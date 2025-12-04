import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("Kulebanekalkulator")

st.subheader("Inndata")

muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)

# NYTT: hvor langt grafen skal vise
graph_range = st.number_input("Vis graf opp til (meter)", value=500, min_value=50, max_value=2000)

# ------------------------------
# ENKEL MODELL MED ELEVASJONSVINKEL (ingen drag)
# ------------------------------
def simple_drop_with_angle(mv, zero, max_range=500, step=1):
    g = 9.81
    distances = np.arange(0, max_range + step, step)
    drops = []

    # 1. Naturlig fall ved innskyting
    t_zero = zero / mv
    natural_drop_zero = 0.5 * g * t_zero**2

    # 2. Vinkel justert slik at kula treffer 0 på innskytingsavstand
    angle = natural_drop_zero / zero   # liten vinkel → tan(angle) ≈ angle

    for x in distances:
        t = x / mv
        natural_drop = 0.5 * g * t**2
        height_relative = x * angle - natural_drop
        drops.append(height_relative)

    return distances, np.array(drops)


# ------------------------------
# STREAMLIT UI-KODE
# ------------------------------
if st.button("Beregn kulebane"):

    dist, drop = simple_drop_with_angle(muzzle_velocity, zero_range, graph_range)

    # konverter til cm
    drop_cm = drop * 100

    # fall ved målavstand
    idx = np.argmin(abs(dist - target_range))
    fall_target = drop_cm[idx]

    st.write(f"**Fall ved {target_range} m:** {fall_target:.1f} cm")

    # --------------------------
    # GRAF
    # --------------------------
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)

    # vis siktelinje og innskyting også innenfor valgt område
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)
    if zero_range <= graph_range:
        ax.axvline(zero_range, color="red", linestyle="--", linewidth=1)

    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Høyde relativt siktelinje (cm)")
    ax.set_title(f"Kulebane med innskyting (0–{graph_range} m)")
    ax.grid(True)

    st.pyplot(fig)

