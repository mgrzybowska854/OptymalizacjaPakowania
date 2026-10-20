import itertools
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Optymalizacja pakowania 3D",
    layout="wide"
)

st.title("Optymalizacja pakowania 3D")
st.write("Wszystkie wymiary podawaj w milimetrach.")

st.header("1. Wymiary opakowania")

c1, c2, c3 = st.columns(3)

with c1:
    bx = st.number_input("Szerokość opakowania", min_value=1, value=800)
with c2:
    by = st.number_input("Długość opakowania", min_value=1, value=1200)
with c3:
    bz = st.number_input("Wysokość opakowania", min_value=1, value=670)

st.header("2. Wymiary wyrobu")

c1, c2, c3 = st.columns(3)

with c1:
    h = st.number_input("Wysokość wyrobu", min_value=1, value=100)
with c2:
    w = st.number_input("Szerokość wyrobu", min_value=1, value=100)
with c3:
    t = st.number_input("Grubość wyrobu", min_value=1, value=20)

gap = st.number_input(
    "Minimalny odstęp między sztukami (mm)",
    min_value=0,
    value=0
)

if st.button("OBLICZ NAJLEPSZE UŁOŻENIE", type="primary"):
    box = (bx, by, bz)
    product = (h, w, t)

    # Wszystkie unikalne orientacje wyrobu
    orientations = sorted(set(itertools.permutations(product)))
    results = []

    for a, b, c in orientations:
        nx = (bx + gap) // (a + gap)
        ny = (by + gap) // (b + gap)
        nz = (bz + gap) // (c + gap)

        count = nx * ny * nz

        results.append({
            "Wymiar X": a,
            "Wymiar Y": b,
            "Wymiar Z": c,
            "Sztuk w rzędzie": nx,
            "Rzędów": ny,
            "Warstw": nz,
            "Sztuk w warstwie": nx * ny,
            "Łącznie sztuk": count,
            "Wysokość zajęta (mm)": nz * c + max(0, nz - 1) * gap
        })

    df = pd.DataFrame(results)
    df = df.sort_values(
        by=["Łącznie sztuk", "Wysokość zajęta (mm)"],
        ascending=[False, True]
    ).reset_index(drop=True)

    best = df.iloc[0]

    st.header("3. Najlepszy układ regularny")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Liczba sztuk", int(best["Łącznie sztuk"]))
    c2.metric("Sztuk w warstwie", int(best["Sztuk w warstwie"]))
    c3.metric("Liczba warstw", int(best["Warstw"]))
    c4.metric("Wysokość zajęta", f'{int(best["Wysokość zajęta (mm)"])} mm')

    st.write(
        "Orientacja wyrobu (X × Y × Z): "
        f'{int(best["Wymiar X"])} × '
        f'{int(best["Wymiar Y"])} × '
        f'{int(best["Wymiar Z"])} mm'
    )

    st.info(
        "Wynik dotyczy regularnego ułożenia wszystkich sztuk "
        "w tej samej orientacji. Nie jest gwarancją globalnego "
        "optimum dla układów mieszanych."
    )

    st.header("4. Porównanie wszystkich orientacji")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        "Pobierz wyniki CSV",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name="wyniki_pakowania.csv",
        mime="text/csv"
    )