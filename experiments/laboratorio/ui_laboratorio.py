"""UI local de texto y resultados (#44). Ejecutar con streamlit run."""

import json
import importlib
import sys
import tempfile
import time
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

import ui_resultados

# Streamlit reejecuta el script, pero puede conservar el módulo auxiliar anterior.
# Recargar solo al cambiar su fuente evita importar funciones que aún no están en memoria.
if getattr(ui_resultados, "FUENTE_MTIME_NS", None) != (AQUI / "ui_resultados.py").stat().st_mtime_ns:
    importlib.reload(ui_resultados)

import math

from ui_resultados import (RESULTADOS, combinar_corridas, color_detector, csv_comparacion,
                           csv_texto, datos_matriz_panorama, fila_texto, guardar_csv,
                           leer_csv, leer_seccion_manual, nombre_detector, numero,
                           obtener_series_columnas, procedencia, puntos, sha256,
                           texto_caso, tipo_entrada, trazo_corrida, validar_semillas)


def nombre_curva(fila, todas_filas=None):
    corrida = fila.get("corrida_visual", fila.get("fecha", "")[:10])
    base = f"{fila['caso']} · {nombre_detector(fila)} [{corrida}]"
    if todas_filas:
        colisiones = [f for f in todas_filas if f.get("caso") == fila.get("caso")
                      and nombre_detector(f) == nombre_detector(fila)
                      and f.get("corrida_visual", "C1") == corrida]
        if len(colisiones) > 1:
            raws = {f.get("detector_goteo", "") for f in colisiones}
            if len(raws) > 1:
                return f"{fila['caso']} · {nombre_detector(fila)} · {fila.get('detector_goteo', '').split('/')[-1]} [{corrida}]"
            return f"{base} #{fila.get('_ocurrencia', 1)}"
    elif fila.get("_ocurrencia", 1) > 1:
        return f"{base} #{fila['_ocurrencia']}"
    return base


def figura_comparacion(filas, relativo=False):
    """Superposición enfocada; cada curva conserva su identidad sin promediar ni rellenar vacíos."""
    fig = go.Figure()
    for fila in filas:
        datos = puntos(fila)
        det = nombre_detector(fila)
        corrida = fila.get("corrida_visual", "C1")
        fig.add_trace(go.Scatter(
            x=[p["turno"] * 100 / len(datos) if relativo else p["turno"] for p in datos],
            y=[p["puntaje"] for p in datos], mode="lines+markers", connectgaps=False,
            name=nombre_curva(fila, filas),
            line=dict(color=color_detector(det), dash=trazo_corrida(corrida), width=2),
            marker=dict(size=4),
            customdata=[[p["turno"], fila["caso"], det,
                         fila.get("archivo_resultado", ""), fila.get("commit", ""), corrida,
                         fila.get("detector_goteo", "")] for p in datos],
            hovertemplate="Caso: %{customdata[1]}<br>Turno: %{customdata[0]}<br>Puntaje: %{y:.3f}"
                          "<br>Detector: %{customdata[2]}<br>Identidad cruda: %{customdata[6]}"
                          "<br>Corrida: %{customdata[5]}<br>CSV: %{customdata[3]}<br>Commit: %{customdata[4]}<extra></extra>"))
    umbrales = sorted({numero(f["umbral_goteo"]) for f in filas if numero(f.get("umbral_goteo")) is not None})
    for umbral in umbrales:
        fig.add_hline(y=umbral, line_dash="dash", line_color="#9ca3af",
                      annotation_text=f"Umbral registrado {umbral}")
    n = max((int(f["n_turnos"]) for f in filas), default=1)
    fig.update_layout(xaxis_title="Avance por cantidad de turnos (%)" if relativo else "Turno (sin segundos)",
                      yaxis_title="Puntaje del turno", yaxis_range=[0, 1],
                      xaxis_range=[0, 100] if relativo else [0.5, n + 0.5],
                      xaxis_dtick=10 if relativo else max(1, n // 12), height=420,
                      legend=dict(orientation="h", y=-0.22, font=dict(size=9)),
                      margin=dict(t=35, b=60), hovermode="closest")
    return fig


def figura_panorama(filas, casos):
    """Panorama matricial (ejemplos vs series); celdas sin datos explícitas."""
    matriz = datos_matriz_panorama(filas, casos)
    fig = go.Figure(data=go.Heatmap(
        z=matriz["z"],
        x=[s["codigo"] for s in matriz["series"]],
        y=matriz["casos"],
        text=matriz["text"],
        texttemplate="%{text}",
        textfont=dict(size=11),
        colorscale="Blues",
        zmin=0.0,
        zmax=1.0,
        colorbar=dict(title=dict(text="Puntaje máx", side="right"), len=0.85, thickness=16),
        hoverongaps=True,
        customdata=matriz["customdata"],
        hovertemplate="%{customdata}<extra></extra>"
    ))
    for ann in matriz["annotations"]:
        fig.add_annotation(ann)
    altura = max(240, min(800, len(casos) * 26 + 90))
    fig.update_layout(
        title=dict(text="<b>Panorama · puntajes máx</b>", font=dict(size=12)),
        height=altura,
        margin=dict(l=70, r=40, t=45, b=35),
        xaxis=dict(side="top", tickfont=dict(size=11), tickangle=0),
        yaxis=dict(autorange="reversed", tickfont=dict(size=11))
    )
    return fig, matriz


def figura_panel_ejemplo(filas_caso, caso, relativo=False):
    """Panel individual compacto para un ejemplo con escala 0-1 compartida y alertas agrupadas."""
    fig = go.Figure()
    n = max((int(f["n_turnos"]) for f in filas_caso), default=1)

    conteo_traza = {}
    for f in filas_caso:
        k = (nombre_detector(f), f.get("corrida_visual", "C1"))
        conteo_traza[k] = conteo_traza.get(k, 0) + 1

    for fila in filas_caso:
        datos = puntos(fila)
        det = nombre_detector(fila)
        corrida = fila.get("corrida_visual", "C1")
        color = color_detector(det)
        dash = trazo_corrida(corrida)

        k = (det, corrida)
        if conteo_traza.get(k, 0) > 1:
            raws = {f.get("detector_goteo", "") for f in filas_caso if (nombre_detector(f), f.get("corrida_visual", "C1")) == k}
            if len(raws) > 1:
                raw_sufijo = fila.get("detector_goteo", "").split("/")[-1]
                nombre_traza = f"{det} · {raw_sufijo} [{corrida}]"
            else:
                oc = fila.get("_ocurrencia", 1)
                nombre_traza = f"{det} [{corrida}] #{oc}"
        else:
            nombre_traza = f"{det} [{corrida}]"

        fig.add_trace(go.Scatter(
            x=[p["turno"] * 100 / len(datos) if relativo else p["turno"] for p in datos],
            y=[p["puntaje"] for p in datos],
            mode="lines+markers",
            connectgaps=False,
            name=nombre_traza,
            line=dict(color=color, dash=dash, width=2),
            marker=dict(size=4),
            customdata=[[p["turno"], caso, det,
                         fila.get("archivo_resultado", ""), fila.get("commit", ""), corrida,
                         fila.get("detector_goteo", "")] for p in datos],
            hovertemplate="Turno: %{customdata[0]}<br>Puntaje: %{y:.3f}<br>Detector: %{customdata[2]}<br>"
                          "Identidad cruda: %{customdata[6]}<br>Corrida: %{customdata[5]}<extra></extra>"
        ))

    # Agrupar anotaciones verticales por posición en x para no superponer leyendas idénticas
    reglas_por_x = {}
    goteo_por_x = {}
    for fila in filas_caso:
        datos = puntos(fila)
        corrida = fila.get("corrida_visual", "C1")
        tr = numero(fila.get("T_R_turno"))
        if tr is not None:
            pos_x = tr * 100 / len(datos) if relativo else tr
            reglas_por_x.setdefault(pos_x, []).append(corrida)
        ta = numero(fila.get("T_A_turno"))
        if ta is not None:
            pos_x = ta * 100 / len(datos) if relativo else ta
            goteo_por_x.setdefault(pos_x, []).append(corrida)

    for pos_x, corridas in reglas_por_x.items():
        corridas_unicas = list(dict.fromkeys(corridas))
        if len(corridas_unicas) == 1:
            texto = f"Reglas [{corridas_unicas[0]}]"
        elif len(corridas_unicas) <= 3:
            texto = f"Reglas [{', '.join(corridas_unicas)}]"
        else:
            texto = f"Reglas [{len(corridas_unicas)} corridas]"
        fig.add_vline(x=pos_x, line_color="#dc2626", line_dash="dot", line_width=1.5,
                      annotation_text=texto, annotation_position="bottom left",
                      annotation_font_size=8)

    for pos_x, corridas in goteo_por_x.items():
        corridas_unicas = list(dict.fromkeys(corridas))
        if len(corridas_unicas) == 1:
            texto = f"Goteo [{corridas_unicas[0]}]"
        elif len(corridas_unicas) <= 3:
            texto = f"Goteo [{', '.join(corridas_unicas)}]"
        else:
            texto = f"Goteo [{len(corridas_unicas)} corridas]"
        fig.add_vline(x=pos_x, line_color="#7c3aed", line_dash="dot", line_width=1.5,
                      annotation_text=texto, annotation_position="top right",
                      annotation_font_size=8)

    umbrales = sorted({numero(f["umbral_goteo"]) for f in filas_caso if numero(f.get("umbral_goteo")) is not None})
    for umbral in umbrales:
        fig.add_hline(y=umbral, line_dash="dash", line_color="#9ca3af", line_width=1,
                      annotation_text=f"Umbral {umbral}", annotation_position="top left",
                      annotation_font_size=8)

    fig.update_layout(
        title=dict(text=f"<b>{caso}</b>", font=dict(size=12)),
        xaxis_title="Avance (%)" if relativo else "Turno",
        yaxis_title="Puntaje",
        yaxis_range=[0, 1],
        xaxis_range=[0, 100] if relativo else [0.5, n + 0.5],
        xaxis_dtick=20 if relativo else max(1, n // 8),
        height=320,
        margin=dict(l=45, r=15, t=35, b=35),
        legend=dict(orientation="h", y=-0.32, font=dict(size=9)),
        hovermode="closest"
    )
    return fig


def comparar():
    archivos = sorted(RESULTADOS.rglob("*.csv"), reverse=True)
    if not archivos:
        st.info("Todavía no hay CSV en resultados/.")
        return

    with st.expander("Filtros y configuración de vista", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            elegidos = st.multiselect("Corridas a comparar", archivos, default=archivos,
                                      format_func=lambda p: str(p.relative_to(RESULTADOS)),
                                      help="Archivos CSV de resultados a comparar.")
            if not elegidos:
                st.info("Seleccioná al menos una corrida.")
                return
            try:
                filas, resumenes = combinar_corridas(elegidos)
            except (OSError, UnicodeError, ValueError) as e:
                st.error(str(e))
                return
            tipos = sorted({tipo_entrada(f) for f in filas})
            tipos_elegidos = st.multiselect("Origen de los ejemplos", tipos,
                                            default=["Grabaciones transcritas"] if "Grabaciones transcritas" in tipos else tipos,
                                            help="Tipo de entrada: grabaciones transcritas, guiones o pruebas de UI.")
            filas = [f for f in filas if tipo_entrada(f) in tipos_elegidos]
            clases = sorted({f["clase"] for f in filas})
            clases_elegidas = st.multiselect("Clases a comparar", clases, default=clases,
                                             help="Clase del ejemplo: V (Vishing), L (Legítima), etc.")
            filas = [f for f in filas if f["clase"] in clases_elegidas]

        with col2:
            detectores = sorted({f.get("detector_goteo", "") for f in filas})
            conteo_det = {}
            for d in detectores:
                nom = nombre_detector(d)
                conteo_det[nom] = conteo_det.get(nom, 0) + 1

            def formato_detector(det_crudo):
                nom = nombre_detector(det_crudo)
                if conteo_det.get(nom, 0) > 1:
                    return f"{nom} ({det_crudo})"
                return nom

            modelos = st.multiselect("Detectores a comparar", detectores, default=detectores,
                                     format_func=formato_detector,
                                     help="Detectores de goteo a incluir en la comparación.")
            filas = [f for f in filas if f.get("detector_goteo", "") in modelos]
            casos = sorted({f["caso"] for f in filas})
            ejemplos = st.multiselect("Ejemplos a comparar", casos, default=casos,
                                      help="Subconjunto de ejemplos para filtrar la vista.")
            filas = [f for f in filas if f["caso"] in ejemplos]
            eje = st.radio("Eje horizontal", ["Turno", "Avance por cantidad de turnos (%)"], horizontal=True,
                           help="Turno cronológico (sin segundos) o avance porcentual relativo.")

        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            tamano_pagina_sel = st.selectbox("Paneles por página", [4, 6, 8, 12, "Todos"], index=0,
                                             help="Cantidad de paneles de curvas a mostrar por página.")
        with col_opt2:
            limite_curvas_sel = st.selectbox("Límite de curvas por panel", [4, 6, 8, 12, "Todas"], index=1,
                                             help="Límite visible para evitar saturar paneles con muchas corridas del mismo caso.")

    if not filas:
        st.info("No hay ejemplos con esta selección.")
        return

    validas = []
    for fila in filas:
        try:
            puntos(fila)
            numero(fila.get("umbral_goteo"))
            validas.append(fila)
        except (TypeError, ValueError) as e:
            st.error(f"{fila['caso']} · {fila['archivo_resultado']}: {e}")

    if not validas:
        st.info("No hay ejemplos válidos para graficar.")
        return

    casos_validos = list(dict.fromkeys(f["caso"] for f in validas))
    total_ejemplos = len(casos_validos)
    total_series = len(validas)
    total_csvs = len({f["archivo_resultado"] for f in validas})

    # --- 1. PANORAMA MATRICIAL ---
    st.subheader("Panorama general")
    m1, m2, m3 = st.columns(3)
    m1.metric("Ejemplos", total_ejemplos)
    m2.metric("Series", total_series)
    m3.metric("Archivos CSV", total_csvs)

    st.caption("Puntajes máximos (0–1). Sin calibrar entre modelos ni establecer ganador (D07/D08/D09 abiertas). Celdas vacías = sin corrida o sin opinión.")
    if eje != "Turno":
        st.caption("Avance relativo normalizado por cantidad de turnos (no son segundos de llamada).")

    fig_pan, matriz = figura_panorama(validas, casos_validos)
    mapeo_series = " · ".join(f"**{s['codigo']}**: {s['etiqueta']}" for s in matriz["series"])
    st.caption(f"**Series en columnas:** {mapeo_series}")
    st.plotly_chart(fig_pan, width="stretch")
    with st.expander("Mapeo de series del panorama (S1, S2, …)", expanded=False):
        st.dataframe([{
            "Serie": s["codigo"],
            "Etiqueta": s["etiqueta"],
            "Corrida visual": s["corrida"],
            "Detector": s["detector"],
            "Identidad completa": s["detector_crudo"],
            "Archivo CSV": s["archivo"]
        } for s in matriz["series"]], width="stretch", hide_index=True)
    if matriz["sin_opinion"] > 0:
        st.info(f"{matriz['sin_opinion']} serie(s) no tienen opiniones registradas (marcadas como 'Sin opinión'); no se convierten en cero.")

    with st.expander("Metodología y cautelas de la comparación", expanded=False):
        st.markdown(
            "- **Selección:** Los CSV pueden usar entrenamientos distintos y sus puntajes no están calibrados entre sí.\n"
            "- **Alertas:** `T_R_turno` en estas salidas históricas representa el primer disparo de reglas (no la anotación humana del pedido crítico `T_C`); `T_A_turno` corresponde a goteo.\n"
            "- **Decisiones abiertas:** D07 (taxonomía), D08 (política temporal y umbrales) y D09 (modelos definitivos) continúan en curso.\n"
            "- Para detalles completos, consultar la pestaña **Ayuda** en la barra lateral."
        )

    # --- 2. PANELES PEQUEÑOS DE CURVAS ---
    st.subheader("Curvas por ejemplo")
    tamano_pag = total_ejemplos if tamano_pagina_sel == "Todos" else int(tamano_pagina_sel)
    total_paginas = max(1, math.ceil(total_ejemplos / tamano_pag))

    if total_paginas > 1:
        col_pag1, col_pag2 = st.columns([2, 5])
        num_pag = col_pag1.number_input(f"Página de paneles (1–{total_paginas})", min_value=1, max_value=total_paginas, value=1, step=1)
        idx_ini = (num_pag - 1) * tamano_pag
        idx_fin = min(num_pag * tamano_pag, total_ejemplos)
        col_pag2.caption(
            f"Mostrando ejemplos {idx_ini + 1} a {idx_fin} de {total_ejemplos} seleccionados (Página {num_pag} de {total_paginas}). "
            "El panorama matricial superior, la tabla de alertas y la descarga incluyen los datos completos."
        )
        casos_visibles = casos_validos[idx_ini:idx_fin]
    else:
        st.caption(f"Mostrando todos los {total_ejemplos} ejemplos seleccionados en paneles individuales compactos.")
        casos_visibles = casos_validos

    limite_curvas = None if limite_curvas_sel == "Todas" else int(limite_curvas_sel)

    for i in range(0, len(casos_visibles), 2):
        fila_cols = st.columns(2)
        for col_idx, offset in enumerate((0, 1)):
            if i + offset < len(casos_visibles):
                c_nombre = casos_visibles[i + offset]
                with fila_cols[col_idx]:
                    filas_c = [f for f in validas if f["caso"] == c_nombre]
                    if limite_curvas is not None and len(filas_c) > limite_curvas:
                        st.caption(
                            f"**{c_nombre}**: mostrando {limite_curvas} de {len(filas_c)} curvas registradas "
                            f"(límite por panel: {limite_curvas}). Podés ampliar el límite en los controles."
                        )
                        filas_panel = filas_c[:limite_curvas]
                    else:
                        filas_panel = filas_c
                    st.plotly_chart(figura_panel_ejemplo(filas_panel, c_nombre, relativo=eje != "Turno"), width="stretch")

    # --- 3. SUPERPOSICIÓN ENFOCADA (OPCIONAL) ---
    with st.expander("Superposición enfocada (opcional — comparar curvas superpuestas)", expanded=False):
        st.caption(
            "Permite inspeccionar directamente curvas superpuestas en un único gráfico para una selección acotada. "
            "No recomendada para conjuntos grandes."
        )
        activar_foco = st.checkbox("Activar superposición enfocada", value=False)
        if activar_foco:
            ejemplos_foco = st.multiselect("Ejemplos a superponer", casos_validos,
                                           default=casos_validos[:2] if len(casos_validos) <= 2 else casos_validos[:1],
                                           max_selections=6, help="Seleccioná hasta 6 ejemplos para habilitar la superposición.")
            if ejemplos_foco:
                filas_disponibles = [f for f in validas if f["caso"] in ejemplos_foco]
                total_disp = len(filas_disponibles)

                def label_serie_foco(idx):
                    f = filas_disponibles[idx]
                    return nombre_curva(f, filas_disponibles)

                opciones_indices = list(range(total_disp))
                defecto_indices = opciones_indices[:min(10, total_disp)]

                seleccion_indices = st.multiselect(
                    "Series a superponer (máximo 10)",
                    options=opciones_indices,
                    default=defecto_indices,
                    format_func=label_serie_foco,
                    max_selections=10,
                    help="Elegí explícitamente hasta 10 series para comparar en el gráfico."
                )

                st.caption(
                    f"Seleccionadas: {len(seleccion_indices)} de {total_disp} series disponibles "
                    f"para los {len(ejemplos_foco)} ejemplo(s) elegido(s) (límite máximo: 10)."
                )

                if seleccion_indices:
                    filas_foco = [filas_disponibles[i] for i in seleccion_indices]
                    st.plotly_chart(figura_comparacion(filas_foco, relativo=eje != "Turno"), width="stretch")
                else:
                    st.info("Seleccioná al menos una serie en el selector para visualizar el gráfico.")
            else:
                st.info("Seleccioná al menos un ejemplo para visualizar la superposición.")

    # --- 4. PROCEDENCIA Y ALERTAS ---
    st.subheader("Procedencia de las corridas")
    st.caption("Detalle de las corridas visuales identificadas en la selección, vinculadas a su CSV de origen y commit.")
    corridas_info = []
    series_cols = matriz["series"] if "matriz" in locals() and "series" in matriz else obtener_series_columnas(filas)
    for s in series_cols:
        filas_s = [f for f in filas if f.get("archivo_resultado") == s["archivo"]
                   and f.get("detector_goteo") == s["detector_crudo"]
                   and f.get("_ocurrencia", 1) == s.get("ocurrencia", 1)]
        commit = filas_s[0].get("commit", "") if filas_s else ""
        fecha = filas_s[0].get("fecha", "") if filas_s else ""
        corridas_info.append({
            "Serie": s["codigo"],
            "Etiqueta": s["etiqueta"],
            "Corrida visual": s["corrida"],
            "Detector": s["detector"],
            "Identidad completa (detector_goteo)": s["detector_crudo"],
            "Archivo CSV": s["archivo"],
            "Ejemplos con datos": len(filas_s),
            "Commit": commit,
            "Fecha": fecha[:19] if fecha else ""
        })
    st.dataframe(corridas_info, width="stretch", hide_index=True)

    st.subheader("Alertas de todos los ejemplos seleccionados")
    st.caption("T_R del CSV = primer disparo de reglas (no anotación humana del pedido); T_A = goteo. Vacío significa sin marca registrada. "
               "No hay T_C ni tiempos de audio. Los resúmenes _suite quedan fuera de esta comparación. "
               "La tabla conserva la selección completa independientemente de la paginación de paneles.")
    columnas = ("caso", "detector_goteo", "corrida_visual", "archivo_resultado", "n_turnos", "puntaje_max",
                "umbral_goteo", "T_R_turno", "T_A_turno", "falsa_alarma", "clase")
    st.dataframe([{k: f.get(k) or None for k in columnas} for f in filas], width="stretch", hide_index=True)

    with st.expander("Filas originales y procedencia completa (para auditoría)"):
        st.dataframe(filas, width="stretch", hide_index=True)

    if resumenes:
        with st.expander("Resúmenes originales _suite (no se recalculan con los filtros)"):
            st.dataframe(resumenes, width="stretch", hide_index=True)

    st.download_button("Descargar filas de la comparación (selección completa)", csv_comparacion(filas),
                       file_name="comparacion-laboratorio.csv", mime="text/csv")


def grafico(fila):
    datos = puntos(fila)
    color = color_detector(fila)
    fig = go.Figure(go.Scatter(x=[p["turno"] for p in datos], y=[p["puntaje"] for p in datos],
                              mode="lines+markers", connectgaps=False, name="Puntaje del turno",
                              line=dict(color=color, width=2)))
    umbral = numero(fila.get("umbral_goteo"))
    if umbral is not None:
        fig.add_hline(y=umbral, line_dash="dash", annotation_text=f"Umbral registrado: {umbral}")
    for columna, nombre, color, posicion in (("T_A_turno", "Goteo", "#7c3aed", "top right"),
                                             ("T_R_turno", "Reglas (T_R del CSV)", "#dc2626", "bottom left")):
        n = numero(fila.get(columna))
        if n is not None:
            fig.add_vline(x=n, line_color=color, annotation_text=nombre, annotation_position=posicion)
    fig.update_layout(xaxis_title="Turno (sin segundos)", yaxis_title="Puntaje",
                      yaxis_range=[0, 1], xaxis_range=[0.5, len(datos) + 0.5],
                      xaxis_dtick=max(1, len(datos) // 12), height=370, margin=dict(t=45, b=35))
    st.plotly_chart(fig, width="stretch")
    if all(p["puntaje"] is None for p in datos):
        st.info("Sin opinión del detector de goteo. Esto no equivale a riesgo cero.")


def alertas(fila):
    c1, c2, c3 = st.columns(3)
    c1.metric("Primer disparo de reglas", fila.get("T_R_turno") or "Sin disparo")
    c2.metric("Primera alerta de goteo", fila.get("T_A_turno") or "Sin alerta")
    c3.metric("T_C anotado", fila.get("T_C_turno") or "Sin dato")
    st.caption("T_R_turno en estas salidas registra reglas; no es una anotación humana del pedido. "
               "La histéresis del spike usa el máximo de una ventana de 3 opiniones; "
               "un pico y una opinión baja pueden disparar. D08 sigue abierta.")


def explorar_detalle():
    archivos = sorted(RESULTADOS.rglob("*.csv"), reverse=True)
    if not archivos:
        st.info("Todavía no hay CSV en resultados/.")
        return
    path = st.selectbox("Corrida", archivos, format_func=lambda p: str(p.relative_to(RESULTADOS)))
    try:
        filas, resumen = leer_csv(path)
    except (OSError, UnicodeError, ValueError) as e:
        st.error(str(e))
        return
    clases = st.multiselect("Clases", sorted({f["clase"] for f in filas}),
                            default=sorted({f["clase"] for f in filas}))
    seleccion = [f for f in filas if f["clase"] in clases]
    st.caption(f"{len(seleccion)} casos visibles · resumen _suite separado · datos leídos del CSV original")
    if seleccion:
        i = st.selectbox("Caso", range(len(seleccion)), format_func=lambda n: seleccion[n]["caso"])
        fila = seleccion[i]
        st.caption(f"Detector: {fila.get('detector_goteo', 'sin dato')} · commit: {fila.get('commit', 'sin dato')}")
        alertas(fila)
        try:
            grafico(fila)
        except ValueError as e:
            st.error(f"No se puede graficar esta fila: {e}")
        st.write("Etiquetas de reglas:", fila.get("etiquetas_incendio") or "Ninguna")
        if fila.get("nota"):
            st.info(fila["nota"])
        texto = texto_caso(fila["caso"])
        with st.expander("Guion disponible en el repositorio"):
            if texto is None:
                st.caption("Texto no disponible en este checkout; el CSV conserva los puntajes.")
            else:
                st.code(texto, language=None)
        with st.expander("Fila original"):
            st.json(fila)
    with st.expander("Tabla de casos"):
        st.dataframe(seleccion, width="stretch")
    if resumen:
        with st.expander("Resumen original de la suite (no se recalcula con los filtros)"):
            st.dataframe(resumen, width="stretch")
    st.download_button("Descargar CSV original", path.read_bytes(), file_name=path.name, mime="text/csv")


def explorar():
    vista = st.radio("Vista de resultados", ["Comparar ejemplos", "Detalle de un ejemplo"], horizontal=True)
    if vista == "Comparar ejemplos":
        comparar()
    else:
        explorar_detalle()


def entrenar():
    st.write("Entrenamiento de laboratorio: encoder congelado + regresión logística del spike (seed 42).")
    st.caption("No calibra umbrales ni evalúa generalización. Datos de entrada separados de los CSV de resultados.")
    archivo = st.file_uploader("Datos externos: JSON con listas estafa y legitima", type=["json"])
    model_id = st.text_input("Encoder (id de Hugging Face o carpeta local)",
                             value="pysentimiento/robertuito-base-uncased")
    hilos = st.number_input("Hilos CPU", min_value=1, max_value=16, value=2)
    datos = None
    raw = None
    if archivo is not None:
        raw = archivo.getvalue()
        try:
            datos = validar_semillas(raw)
            st.write({"estafa": len(datos["estafa"]), "legitima": len(datos["legitima"]),
                      "sha256": sha256(raw)})
        except (ValueError, UnicodeError) as e:
            st.error(str(e))
    if st.button("Entrenar cabeza LR", disabled=datos is None or not model_id.strip()):
        try:
            from detector_encoder import DetectorEncoder
            t0 = time.perf_counter()
            with st.spinner("Cargando encoder y entrenando cabeza LR…"), tempfile.TemporaryDirectory() as carpeta:
                semillas = Path(carpeta) / "semillas.json"
                semillas.write_bytes(raw)
                det = DetectorEncoder(model_id.strip(), semillas, hilos=int(hilos))
            origen = {**procedencia(), "model_id": model_id.strip(), "seed": 42,
                      "hilos": int(hilos), "datos_sha256": sha256(raw),
                      "n_estafa": len(datos["estafa"]), "n_legitima": len(datos["legitima"]),
                      "duracion_entrenamiento_s": round(time.perf_counter() - t0, 3),
                      "metodo": "encoder congelado, pooling media, max_length=128, LR max_iter=1000",
                      "split": "entrada de entrenamiento de laboratorio; sin evaluación ni test",
                      "limite": "D07/D08/D09 abiertas; no mide rendimiento móvil ni generalización"}
            st.session_state["encoder"] = det
            st.session_state["entrenamiento"] = origen
            st.success("Cabeza entrenada y disponible en Probar texto durante esta sesión.")
        except Exception as e:
            st.error(f"No se completó el entrenamiento: {e}")
            st.caption("Instalá torch, transformers y scikit-learn en el mismo entorno. "
                       "El modelo se carga desde su carpeta o se descarga al caché de Hugging Face.")
    if "entrenamiento" in st.session_state:
        st.json(st.session_state["entrenamiento"])
        st.download_button("Descargar registro de entrenamiento", json.dumps(
            st.session_state["entrenamiento"], ensure_ascii=False, indent=2),
            file_name="entrenamiento-lab.json", mime="application/json")
        st.caption("El encoder disponible corresponde a este registro, aunque cambies los campos del formulario. "
                   "Para reemplazarlo, volvé a entrenar. Los pesos de la cabeza viven en esta sesión.")


def probar():
    st.caption("Una línea = un turno. Líneas vacías y comentarios # se ignoran. Usá texto ficticio.")
    opciones = ["Escribir texto"] + [str(p.relative_to(AQUI)) for p in sorted((AQUI / "casos").rglob("*.txt"))]
    caso = st.selectbox("Entrada", opciones)
    defecto = "Hola, soy del banco.\nTenemos que resolver esto ahora.\nDecime el código que recibiste."
    if caso != "Escribir texto":
        defecto = (AQUI / caso).read_text(encoding="utf-8")
    texto = st.text_area("Texto de prueba", value=defecto, height=190, key=f"texto:{caso}")
    modo = st.selectbox("Detector", ["Reglas solas", "Encoder entrenado", "Cascada con encoder entrenado"])
    umbral = st.number_input("Umbral de goteo (exploración del spike)", min_value=0.0,
                             max_value=1.0, value=0.5, step=0.05, disabled=modo == "Reglas solas")
    clase = st.selectbox("Clase declarada para esta prueba", ["Sin etiquetar", "Legítima", "Vishing"])
    url = ""
    slm = ""
    if modo.startswith("Cascada"):
        url = st.text_input("Servidor SLM local (API compatible)", value="http://localhost:11434/v1")
        slm = st.text_input("Modelo SLM", value="llama3.2:1b-instruct-q4_K_M")
        st.caption("Zona gris 0,35–0,75 del spike, sin calibrar. Si el SLM no responde, conserva el encoder.")
    if st.button("Procesar texto"):
        try:
            import detector
            from pipeline import correr_texto
            det = detector.DetectorLlm(base_url="")
            registro = None
            if modo != "Reglas solas":
                if "encoder" not in st.session_state:
                    raise ValueError("Entrená una cabeza LR en Entrenar antes de usar este detector.")
                det = st.session_state["encoder"]
                registro = st.session_state["entrenamiento"]
                if modo.startswith("Cascada"):
                    from detector_cascada import DetectorCascada
                    if not url.strip() or not slm.strip():
                        raise ValueError("Completá el servidor y el modelo SLM.")
                    from urllib.parse import urlparse
                    destino = urlparse(url.strip())
                    if destino.scheme not in ("http", "https") or destino.hostname not in ("localhost", "127.0.0.1", "::1"):
                        raise ValueError("La prueba de texto requiere un SLM local: localhost, 127.0.0.1 o ::1.")
                    det = DetectorCascada(det, detector.DetectorLlm(modelo=slm.strip(), modo="base", base_url=url.strip()))
            t0 = time.perf_counter()
            with st.spinner("Procesando turnos…"), tempfile.TemporaryDirectory() as carpeta:
                entrada = Path(carpeta) / "entrada.txt"
                entrada.write_text(texto, encoding="utf-8")
                r = correr_texto(entrada, float(umbral), det=det)
            origen = {**procedencia(), "texto_sha256": sha256(texto.encode("utf-8")),
                      "duracion_computo_s": round(time.perf_counter() - t0, 3),
                      "entrenamiento": registro, "modelo_slm": slm or None, "servidor_slm": url or None,
                      "histéresis": "máximo de 3 opiniones, alto dos actualizaciones; spike, D08 abierta"}
            fila = fila_texto(r, modo + (":" + registro["model_id"] if registro else ""),
                              origen, {"Sin etiquetar": "sin_etiquetar", "Legítima": "L", "Vishing": "V"}[clase])
            st.session_state["prueba"] = {"resultado": r, "fila": fila, "origen": origen}
            st.session_state.pop("prueba_guardada", None)
        except Exception as e:
            st.error(f"No se completó la prueba: {e}")
    prueba = st.session_state.get("prueba")
    if prueba:
        st.caption("Última prueba procesada; cambiar el formulario requiere volver a procesar.")
        fila = prueba["fila"]
        alertas(fila)
        grafico(fila)
        st.dataframe(prueba["resultado"]["turnos"], width="stretch")
        st.json(prueba["resultado"]["incendio"])
        st.download_button("Descargar puntajes CSV (sin texto)", csv_texto(fila),
                           file_name="prueba-texto.csv", mime="text/csv")
        st.download_button("Descargar detalle JSON (incluye texto)", json.dumps(prueba, ensure_ascii=False, indent=2),
                           file_name="prueba-texto.json", mime="application/json")
        if st.button("Guardar puntajes en resultados/", disabled="prueba_guardada" in st.session_state):
            try:
                path = guardar_csv(fila)
                st.session_state["prueba_guardada"] = path.name
            except OSError as e:
                st.error(str(e))
        if "prueba_guardada" in st.session_state:
            st.success(f"Guardado: {st.session_state['prueba_guardada']}. Disponible en Resultados.")


def ayuda():
    st.subheader("Manual de usuario y guía de laboratorio")
    st.caption("Fuente única: docs/investigacion/GUIA-CORRIDA-LABORATORIO.md (sección UI). No mantiene copias paralelas.")
    texto_manual = leer_seccion_manual()
    st.markdown(texto_manual)


def main():
    st.set_page_config(page_title="Detector · laboratorio", page_icon="📞", layout="wide")
    st.markdown("""
    <style>
    div[data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        max-width: 1240px;
        padding-top: 3.5rem;
        padding-bottom: 2rem;
        container-type: inline-size;
    }
    h1 {
        font-size: 1.75rem !important;
        margin-bottom: 0.2rem !important;
        padding-top: 0 !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) {
        flex-wrap: nowrap !important;
        gap: 0.5rem !important;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stMetric"]) > div[data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0% !important;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(0, 0, 0, 0.02);
        padding: 0.3rem 0.5rem;
        border-radius: 6px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
    }
    @container (max-width: 640px) {
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) {
            flex-wrap: wrap !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    @media (max-width: 900px) {
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) {
            flex-wrap: wrap !important;
        }
        div[data-testid="stHorizontalBlock"]:has(div[data-testid="stPlotlyChart"]) > div[data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    st.title("Laboratorio de vishing")
    st.caption("Detector incremental · texto primero · evidencia del spike · D07/D08/D09 abiertas")
    st.sidebar.header("Laboratorio local")
    pagina = st.sidebar.radio("Recorrido", ["Resultados", "Probar texto", "Entrenar", "Ayuda"])
    st.sidebar.caption("Los resultados de texto usan turnos. No hay tiempos de audio ni métricas preventivas en segundos.")
    {"Resultados": explorar, "Probar texto": probar, "Entrenar": entrenar, "Ayuda": ayuda}[pagina]()


if __name__ == "__main__":
    main()
