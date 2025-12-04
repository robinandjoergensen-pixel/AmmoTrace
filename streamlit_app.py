import streamlit as st

st.title("AmmoTrace – Kulebanekalkulator")

st.subheader("1. Oppgi data for skuddet")

# Input-felter for bruker
muzzle_velocity = st.number_input("Munningshastighet (m/s)", value=800)
bc = st.number_input("Ballistisk koeffisient (G1)", value=0.45)
zero_range = st.number_input("Innskytingsavstand (meter)", value=100)
target_range = st.number_input("Målavstand (meter)", value=300)

import math

if st.button("Beregn kulebane"):
    st.subheader("Resultater")

    g = 9.81  # gravitasjon m/s²
    time = target_range / muzzle_velocity
    drop = 0.5 * g * time**2

    st.write(f"**Tid til mål:** {time:.3f} s")
    st.write(f"**Kulefall ved {target_range} m:** {drop:.2f} cm")
