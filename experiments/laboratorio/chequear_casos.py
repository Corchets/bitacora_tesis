#!/usr/bin/env python3
"""Chequeo de los casos del spike + ejemplo, en modo texto.

Oracle post-pivote LLM (2026-09-25): mide **incendio (reglas de capa 2)**.
El goteo depende del LLM local (`LLM_BASE_URL`); sin server no hay opinion
y el goteo queda mudo — por eso las expectativas de goteo estan en None
hasta fijar corridas con el modelo en #29.

Uso: desde experiments/laboratorio, `.venv/bin/python chequear_casos.py`
(con el venv de la raíz del repo) o dentro del contenedor.
"""

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import pipeline  # noqa: E402
import rules  # noqa: E402

CASOS = AQUI / "casos"
TYPO_SEED = 42

# (archivo, clase V/L, etiquetas de incendio, turno de incendio, turno de goteo)
# Goteo = None: no se exige hasta tener baseline LLM en #29.
ESPERADO = [
    ("vishing/banco-codigo.txt", "V", {"REQUEST_AUTH_CODE"}, 5, None),
    ("vishing/whatsapp-codigo.txt", "V", {"REQUEST_AUTH_CODE"}, 3, None),
    ("vishing/acceso-remoto.txt", "V", {"REQUEST_REMOTE_ACCESS"}, 3, None),
    ("vishing/anses-beneficio.txt", "V", {"REQUEST_SECRET", "REQUEST_TRANSFER"}, 3, None),
    (
        "vishing/arca-deuda.txt",
        "V",
        {"REQUEST_SECRET", "REQUEST_TRANSFER", "REQUEST_SECURITY_ACTION"},
        3,
        None,
    ),
    ("vishing/familiar-peligro.txt", "V", {"REQUEST_TRANSFER"}, 4, None),
    ("vishing/banco-codigo-parafrasis.txt", "V", {"REQUEST_AUTH_CODE"}, 5, None),
    ("vishing/banco-numeros-sin-clave.txt", "V", {"REQUEST_AUTH_CODE"}, 5, None),
    ("vishing/acceso-remoto-parafrasis.txt", "V", {"REQUEST_REMOTE_ACCESS"}, 3, None),
    ("vishing/anses-beneficio-parafrasis.txt", "V", {"REQUEST_SECRET", "REQUEST_TRANSFER"}, 3, None),
    ("vishing/arca-deuda-parafrasis.txt", "V", {"REQUEST_TRANSFER"}, 5, None),
    ("vishing/familiar-peligro-parafrasis.txt", "V", {"REQUEST_TRANSFER"}, 6, None),
    ("vishing/whatsapp-codigo-parafrasis.txt", "V", {"REQUEST_AUTH_CODE"}, 3, None),
    ("legitima/banco-revisa-app.txt", "L", set(), None, None),
    ("legitima/mensajeria-no-pases-nada.txt", "L", set(), None, None),
    ("legitima/no-bajes-nada.txt", "L", set(), None, None),
    ("legitima/anses-canal-oficial.txt", "L", set(), None, None),
    ("legitima/arca-canal-oficial.txt", "L", set(), None, None),
    ("legitima/familiar-llama-vos.txt", "L", set(), None, None),
    ("legitima/banco-niega-el-codigo.txt", "L", set(), None, None),
    ("legitima/banco-app-parafrasis.txt", "L", set(), None, None),
]

FALLOS: list[str] = []


def _afirmar(
    rel: str,
    clase: str,
    etiquetas: set[str],
    turno: int | None,
    got_turno: int | None,
    r: dict,
    nota: str = "",
) -> None:
    evs = r["incendio"]["eventos"]
    todas = {e for ev in evs for e in ev["etiquetas"]}
    primero = evs[0]["turno"] if evs else None
    got = r["goteo"]["disparo"]
    beam = ";".join(f"{e['turno']}:{','.join(e['etiquetas'])}" for e in evs) or "-"
    if clase == "V":
        if not etiquetas <= todas:
            FALLOS.append(f"{nota}{rel}: incendio {sorted(todas)} no cubre {sorted(etiquetas)}")
        if turno is None:
            if evs:
                FALLOS.append(f"{nota}{rel}: incendio inesperado {beam} (hueco documentado)")
        elif primero != turno:
            FALLOS.append(f"{nota}{rel}: primer incendio t{primero}, esperado t{turno}")
        if got_turno is None:
            # Sin expectativa de goteo (LLM aun sin baseline).
            pass
        elif not got:
            FALLOS.append(f"{nota}{rel}: vishing sin goteo")
        elif r["goteo"]["turno"] != got_turno:
            FALLOS.append(f"{nota}{rel}: goteo t{r['goteo']['turno']}, esperado t{got_turno}")
    else:
        if evs:
            FALLOS.append(f"{nota}{rel}: legítima con incendio {beam}")
        # Sin LLM, goteo mudo es lo esperado; con LLM se reabrirá la chequeo de FP.


def revisar(rel: str, clase: str, etiquetas: set[str], turno: int | None, got_turno: int | None) -> None:
    r = pipeline.correr_texto(CASOS / rel, umbral_goteo=0.5)
    evs = r["incendio"]["eventos"]
    got = r["goteo"]["disparo"]
    beam = ";".join(f"{e['turno']}:{','.join(e['etiquetas'])}" for e in evs) or "-"
    ps = ",".join(f"t{t['n']}={t['puntaje']}" for t in r["turnos"] if t["puntaje"] is not None) or "-"
    print(f"{rel:38s} {clase:3s} {beam:44s} {'SI' if got else 'no':5s} {ps}")
    _afirmar(rel, clase, etiquetas, turno, got_turno, r)


def revisar_ejemplo() -> None:
    r = pipeline.correr_texto(AQUI / "ejemplo.txt", umbral_goteo=0.5)
    turnos = [e["turno"] for e in r["incendio"]["eventos"]]
    print(f"ejemplo.txt: incendio {turnos} goteo {r['goteo']['disparo']} lat {r['latencia_decision_turno']}")
    if turnos != [5, 6]:
        FALLOS.append(f"ejemplo.txt: incendio {turnos}, esperado [5, 6]")


def con_typo(textos: list[str]) -> list[str]:
    """Un swap de letras por turno (una palabra len>4), determinista."""
    import random

    rng = random.Random(TYPO_SEED)
    sal = []
    for linea in textos:
        toks = linea.split()
        idx = [i for i, w in enumerate(toks) if len(w) > 4]
        if idx:
            i = rng.choice(idx)
            w = toks[i]
            j = rng.randrange(len(w) - 1)
            toks[i] = w[:j] + w[j + 1] + w[j] + w[j + 2 :]
        sal.append(" ".join(toks))
    return sal


def revisar_typos() -> None:
    """El incendio debe sobrevivir a un typo por turno: misma cobertura, sin falsos."""
    n_ok = 0
    for rel, clase, etiquetas, turno, _ in ESPERADO:
        textos = [
            l.strip()
            for l in (CASOS / rel).read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
        todas = {e for t in con_typo(textos) for e in rules.incendio_en(t)}
        if clase == "V" and turno is not None:
            if etiquetas <= todas:
                n_ok += 1
            else:
                FALLOS.append(f"typo {rel}: {sorted(todas)} no cubre {sorted(etiquetas)}")
        else:
            if not todas:
                n_ok += 1
            else:
                FALLOS.append(f"typo {rel}: falso incendio {sorted(todas)}")
    print(f"typos (seed {TYPO_SEED}): {n_ok}/{len(ESPERADO)} conservan incendio")


_TILDES = {
    "codigo": "código", "verificacion": "verificación", "telefono": "teléfono",
    "digitos": "dígitos", "pagina": "página", "mas": "más", "esta": "está", "que": "qué",
}


def _perturbar(textos: list[str], modo: str) -> list[str]:
    if modo == "upper":
        return [t.upper() for t in textos]
    if modo == "tildes":
        for a, b in _TILDES.items():
            textos = [t.replace(a, b) for t in textos]
        return textos
    return [f"eh, mirá, {t} ..." for t in textos]


def revisar_robusto() -> None:
    """Mayúsculas, tildes y muletillas no cambian el incendio (reglas)."""
    import tempfile

    for modo in ("upper", "tildes", "muletilla"):
        n0 = len(FALLOS)
        for rel, clase, etiquetas, turno, got_turno in ESPERADO:
            textos = [
                l.strip()
                for l in (CASOS / rel).read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.strip().startswith("#")
            ]
            with tempfile.NamedTemporaryFile(
                "w", suffix=".txt", encoding="utf-8"
            ) as f:
                f.write("\n".join(_perturbar(textos, modo)) + "\n")
                f.flush()
                r = pipeline.correr_texto(f.name, umbral_goteo=0.5)
            _afirmar(rel, clase, etiquetas, turno, got_turno, r, nota=f"{modo} ")
        print(f"robusto/{modo}: {len(ESPERADO) - (len(FALLOS) - n0)}/{len(ESPERADO)} iguales")


def main() -> None:
    for rel, clase, etiquetas, turno, got_turno in ESPERADO:
        revisar(rel, clase, etiquetas, turno, got_turno)
    revisar_ejemplo()
    revisar_typos()
    revisar_robusto()
    if FALLOS:
        print(f"\nFALLA ({len(FALLOS)}):")
        for f in FALLOS:
            print(f"  - {f}")
        raise SystemExit(1)
    print(f"\nOK: {len(ESPERADO)}/{len(ESPERADO)} casos + ejemplo (incendio; goteo LLM pendiente #29)")


if __name__ == "__main__":
    main()
