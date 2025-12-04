import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.title("Kulebanekalkulator")

st.subheader("Inndata")

muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)

# NYTT: siktehøyde (løp → sikte)
sight_height = st.number_input("Siktehøyde (cm)", value=4.5, min_value=0.0, max_value=20.0)

# NYTT: hvor langt grafen skal vises
graph_range = st.number_input("Vis graf opp til (meter)", value=500, min_value=50, max_value=2000)


# ------------------------------------------------------
# MODELL MED SIKTEHØYDE OG ELEVASJON (ingen drag)
# ------------------------------------------------------
def simple_drop_with_sight(mv, zero, sight_height_cm, max_range=500, step=1):
    g = 9.81
    sight_h = sight_height_cm / 100  # cm → meter
    distances = np.arange(0, max_range + step, step)
    drops = []

    # 1. Naturlig fall ved zero avstand
    t_zero = zero / mv
    natural_drop_zero = 0.5 * g * t_zero**2

    # 2. Elevasjonsvinkel som gjør at kula treffer siktehøyden ved zero-range
    angle = (natural_drop_zero + sight_h) / zero

    # 3. Beregn høyde relativt siktelinje for alle avstander
    for x in distances:
        t = x / mv
        natural_drop = 0.5 * g * t**2

        # Høyde relativt siktelinjen (siktelinje = 0)
        height_relative = x * angle - natural_drop - sight_h

        drops.append(height_relative)

    return distances, np.array(drops)


# ------------------------------------------------------
# STREAMLIT FUNKSJONALITET
# ------------------------------------------------------
if st.button("Beregn kulebane"):

    dist, drop = simple_drop_with_sight(muzzle_velocity, zero_range, sight_height, graph_range)

    drop_cm = drop * 100

    # Fall ved målavstand
    idx = np.argmin(abs(dist - target_range))
    fall_target = drop_cm[idx]

    st.write(f"**Fall ved {target_range} m:** {fall_target:.1f} cm")

    # ------------------------------------------------------
    # FINN FØRSTE GANG KULA KRYSSES SIKTELINJEN (før zero)
    # ------------------------------------------------------
    zero_cross = None
    for i in range(1, len(dist)):
        if drop[i - 1] < 0 and drop[i] >= 0:
            zero_cross = dist[i]
            break

    if zero_cross:
        st.write(f"**Første kryss av siktelinjen:** {zero_cross:.1f} m")


    # ------------------------------------------------------
    # TREFFPUNKT-TABELL (hver 10 meter)
    # ------------------------------------------------------
    st.subheader("Treffpunkt-tabell (hver 10 m)")

    table_dist = np.arange(0, graph_range + 1, 10)
    table_drop = np.interp(table_dist, dist, drop_cm)

    table_data = { "Avstand (m)": table_dist, "Fall (cm)": np.round(table_drop, 1) }

    st.table(table_data)


    # ------------------------------------------------------
    # GRAF
    # ------------------------------------------------------
    fig, ax = plt.subplots()
    ax.plot(dist, drop_cm)

    # siktelinje
    ax.axhline(0, color="gray", linestyle="--", linewidth=1)

    # innskyting
    if zero_range <= graph_range:
        ax.axvline(zero_range, color="red", linestyle="--", linewidth=1)

    ax.set_xlabel("Avstand (m)")
    ax.set_ylabel("Høyde relativt siktelinje (cm)")
    ax.set_title(f"Kulebane med siktehøyde (0–{graph_range} m)")
    ax.grid(True)

    st.pyplot(fig)


