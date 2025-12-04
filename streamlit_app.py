import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("Kulebanekalkulator")

st.subheader("Inndata")

muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)
max_range = 500  # hvor langt grafen skal vises


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

    # 2. Vinkel for å løfte løpet slik at kula treffer null på innskytingsavstand
    angle = natural_drop_zero / zero   # liten vinkel → tan(angle) ≈ angle

    for x in distances:
        # tid til avstand x
        t = x / mv

        # naturlig fall pga gravitasjon
        natural_drop = 0.5 * g * t**2

        # høyde relativt siktelinjen
        height_relative = x * angle - natural_drop

        drops.append(height_relative)

    return distances, np.array(drops)


# ------------------------------
# STREAMLIT UI-KODE
# ------------------------------
if st.button("Beregn kulebane"):

    dist, drop = simple_drop_with_angle(muzzle_velocity, zero_range, max_range)

    # konverter til cm
    drop_cm = drop * 100

    # finn fall ved mål
    idx = np.argmin(abs(dist - target_range))
    fall_target = drop_cm[idx]

    st.write(f"**Fall ved {target_range} m:** {fall_target:.1f} cm")

    # --------------------------
    # GRAF
    # --------------------------
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)

    ax.axhline(0, color="gray", linestyle="--", linewidth=1)  # siktelinje
    ax.axvline(zero_range, color="red", linestyle="--", linewidth=1)  # innskyting

    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Høyde relativt siktelinje (cm)")
    ax.set_title("Kulebane med innskyting (uten drag)")
    ax.grid(True)

    st.pyplot(fig)
