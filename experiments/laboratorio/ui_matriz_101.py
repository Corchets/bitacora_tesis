"""Visor de matrices #101 con el análisis y las referencias del informe original."""
from collections import defaultdict
from pathlib import Path
import csv
import io
import sys

SLM = Path(__file__).resolve().parent.parent / 'slm-directo'
if str(SLM) not in sys.path:
    sys.path.insert(0, str(SLM))
import informe_101
import resumen


def cargar(path):
    manifiesto, filas, _ = informe_101.leer_corrida(Path(path))
    analisis = resumen.analizar(manifiesto, filas)
    trazas = defaultdict(list)
    for fila in filas:
        trazas[(fila['config'], fila['case_id'])].append(fila)
    return manifiesto, analisis, trazas


def tablas(analisis, configs):
    resultado = []
    for config in configs:
        m = resumen.metricas(analisis[config])
        cs = analisis[config].values()
        resultado.append({'configuración': config, 'vishing con aviso': m['vishing_con_aviso'],
                          'vishing evaluados': m['vishing'], 'falsas alarmas': m['falsas_alarmas'],
                          'legítimas evaluadas': m['legitimas'], 'sin evaluar': m['sin_evaluar'],
                          'fallos de actualización': m['fallos'], 'actualizaciones': m['actualizaciones'],
                          'Tito ms hasta aviso': round(sum(c['tito_ms_total'] for c in cs)),
                          'SLM ms hasta aviso': round(sum(c['slm_ms_total'] for c in cs)),
                          'tokens hasta aviso': int(sum(c['tokens_hasta_aviso'] for c in cs))})
    return resultado


def csv_tabla(filas):
    salida = io.StringIO(newline='')
    if filas:
        writer = csv.DictWriter(salida, fieldnames=list(filas[0]))
        writer.writeheader()
        writer.writerows(filas)
    return salida.getvalue()


def mostrar():
    import plotly.graph_objects as go
    import streamlit as st

    st.subheader('Matriz #101 · comparación operativa')
    archivos = sorted((SLM / 'corridas').glob('*_101_manifiesto.json'), reverse=True)
    archivos += sorted((SLM / 'corridas').glob('*/manifiesto.json'), reverse=True)
    if not archivos:
        st.info('No hay manifiestos de matrices en slm-directo/corridas/.')
        return
    path = st.selectbox('Corrida #101', archivos, format_func=lambda p: str(p.relative_to(SLM / 'corridas')))
    try:
        manifiesto, analisis, trazas = cargar(path)
    except (OSError, ValueError, KeyError) as exc:
        st.error(f'No se puede leer o verificar la corrida: {exc}')
        return
    cobertura = manifiesto.get('cobertura', {})
    st.caption(f"Cobertura registrada: {cobertura.get('completados', '?')}/{cobertura.get('esperados_globales', '?')} recorridos. "
               'Referencias de trabajo; líneas de diálogo, sin tiempos de audio ni prevención en segundos. '
               'Las conversaciones se repiten entre modelos; no son muestras independientes.')
    st.caption('La corrida termina en el primer aviso. Los vacíos son consultas omitidas, fallos o líneas posteriores al aviso; no son riesgo cero. Los puntajes no están calibrados entre modelos.')
    configs = list(analisis)
    modelos = list(dict.fromkeys(c.split('|')[1] for c in configs))
    condiciones = list(dict.fromkeys(c.split('|')[0] for c in configs))
    a, b = st.columns(2)
    with a:
        modelos_e = st.multiselect('Modelos', modelos, default=modelos)
    with b:
        condiciones_e = st.multiselect('Condiciones', condiciones, default=condiciones)
    configs = [c for c in configs if c.split('|')[1] in modelos_e and c.split('|')[0] in condiciones_e]
    if not configs:
        st.info('Seleccioná al menos un modelo y una condición.')
        return
    tabla = tablas(analisis, configs)
    st.markdown('#### Métricas por configuración')
    st.dataframe(tabla, width='stretch', hide_index=True)
    st.download_button('Descargar métricas CSV', csv_tabla(tabla), 'metricas-matriz-101.csv', 'text/csv')
    st.caption('Costos acumulados hasta el aviso o hasta el final; las cargas iniciales se informan por separado en el manifiesto. Los fallos son actualizaciones, no conversaciones.')
    fig = go.Figure()
    for nombre, campo in [('Vishing con aviso', 'vishing con aviso'), ('Falsas alarmas', 'falsas alarmas')]:
        fig.add_bar(name=nombre, x=[t['configuración'] for t in tabla], y=[t[campo] for t in tabla],
                    customdata=[t['vishing evaluados' if campo == 'vishing con aviso' else 'legítimas evaluadas'] for t in tabla],
                    hovertemplate='%{x}<br>%{y}/%{customdata}<extra>%{fullData.name}</extra>')
    fig.update_layout(barmode='group', yaxis_title='Conversaciones', xaxis_title='Configuración', height=420)
    st.plotly_chart(fig, width='stretch')
    casos = sorted({cid for c in configs for cid in analisis[c]})
    if not casos:
        st.info('Las configuraciones seleccionadas no tienen conversaciones registradas.')
        return
    caso = st.selectbox('Conversación', casos)
    fig = go.Figure()
    detalle = []
    for config in configs:
        c = analisis[config].get(caso)
        if not c:
            continue
        fs = sorted(trazas[(config, caso)], key=lambda f: int(f['linea']))
        xs = [int(f['linea']) for f in fs]
        ys = [float(f['riesgo']) if f.get('riesgo') and f.get('valida') == 'true' and f.get('consulta') != 'omitida' else None for f in fs]
        fig.add_scatter(x=xs, y=ys, mode='lines+markers', connectgaps=False, name=config)
        if c['aviso'] is not None:
            aviso = next(f for f in fs if int(f['linea']) == c['aviso'])
            if aviso.get('riesgo'):
                fig.add_scatter(x=[c['aviso']], y=[float(aviso['riesgo'])], mode='markers',
                                marker=dict(symbol='star', size=14), name=f"Aviso · {config}")
        ref = c['ref']
        detalle.append({'configuración': config, 'clase': ref['clase'], 'aviso línea': c['aviso'],
                        'categoría': c['categoria'], 'T_R línea': ref.get('t_r_linea'), 'T_C línea': ref.get('t_c_linea'),
                        'fallos': len(c['fallos']), 'fin': c['fin'], 'ms hasta aviso': round(c['ms_hasta_aviso'])})
    fig.update_layout(title='Riesgo SLM por línea · estrella = aviso registrado', xaxis_title='Línea del diálogo',
                      yaxis_title='Riesgo SLM', yaxis_range=[0, 1], height=420)
    st.plotly_chart(fig, width='stretch')
    st.dataframe(detalle, width='stretch', hide_index=True)
    st.caption('T_R es el pedido de referencia; T_C, el cumplimiento cuando está anotado. El aviso es la decisión registrada, no un cruce de umbral inferido.')
    config = st.selectbox('Traza de configuración', [d['configuración'] for d in detalle])
    fs = sorted(trazas[(config, caso)], key=lambda f: int(f['linea']))
    columnas = ['linea', 'hablante', 'texto', 'consulta', 'valida', 'error', 'riesgo', 'alerta_sugerida', 'aviso', 'motivo', 'evidencia', 'tito_puntaje', 'tito_error', 'tito_ms', 'slm_ms']
    st.dataframe([{k: f.get(k, '') for k in columnas} for f in fs], width='stretch', hide_index=True)
    st.download_button('Descargar traza CSV', csv_tabla([{k: f.get(k, '') for k in columnas} for f in fs]),
                       'traza-matriz-101.csv', 'text/csv')
