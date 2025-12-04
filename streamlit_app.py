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
    step = float(step)

    # konverter m/s → fps (nødvendig for G7)
    mv_fps = mv / 0.3048

    def g7_drag(v_fps):
        drag_table = [
            (0, 423, 0.2344, 1.30),
            (423, 1700, 0.1716, 1.55),
            (1700, 2400, 0.1278, 1.70),
            (2400, 3300, 0.0906, 1.90),
        ]
        for vmin, vmax, a, b in drag_table:
            if vmin <= v_fps < vmax:
                return a, b
        return drag_table[-1][2], drag_table[-1][3]

    # juster elevasjonsvinkel grovt (ikke binary search)
    angle = 0.0  
    drop_at_zero = 9999

    for correction in [0.001, 0.0005, 0.00025, 0.0001]:
        while abs(drop_at_zero) > 0.01:
            # test trajectory to zero target
            v = mv
            y = 0
            x = 0
            while x < zero_range:
                v_fps = v / 0.3048
                a, b = g7_drag(v_fps)

                dv = (a * v_fps**b) / bc
                dv = dv * 0.3048  # back to m/s

                v -= dv * (step / v)
                x += step
                y += math.tan(angle) * step - g * (step / v)**2 / 2

            drop_at_zero = y

            if drop_at_zero > 0:
                angle -= correction
            else:
                angle += correction

    # full trajectory
    distances = np.arange(0, max_range + step, step)
    drops = []
    times = []
    velocities = []

    v = mv
    y = 0
    t = 0

    for x in distances:
        v_fps = v / 0.3048
        a, b = g7_drag(v_fps)
        dv = (a * v_fps**b) / bc
        dv = dv * 0.3048

        v -= dv * (step / v)
        t += step / v
        y += math.tan(angle) * step - g * (step / v)**2 / 2

        drops.append(y)
        times.append(t)
        velocities.append(v)

    # juster drop slik at 0 på innskyting
    zero_index = int(zero_range / step)
    drops = np.array(drops) - drops[zero_index]

    return np.array(distances), drops, np.array(times), np.array(velocities)

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

