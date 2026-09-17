"""Informe JSON de la corrida. Datos, no prosa."""

import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=Path(__file__).resolve().parent,
        )
        return out.stdout.strip() or "desconocido"
    except Exception:
        return "desconocido"


def _versiones() -> dict:
    vers = {}
    try:
        from importlib import metadata

        for pkg in ("sherpa-onnx", "huggingface-hub", "numpy", "scikit-learn", "scipy"):
            try:
                vers[pkg] = metadata.version(pkg)
            except Exception:
                vers[pkg] = "no-instalado"
    except Exception:
        pass
    return vers


def armar(gama, resultado: dict, entrada: str | Path, comando: str, chunk_ms: int | None) -> dict:
    modo = resultado.get("modo", "audio")
    return {
        "spike": "issue #29 (hijo de #28). Corrida repetible, no cierra D09.",
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entrada": os.path.basename(str(entrada)),
        "comando": comando,
        "commit": _commit(),
        "gama": gama.nombre,
        "asr": "no-usado (modo texto)" if modo == "texto" else gama.asr,
        "detector": detector_stub(),
        "techo_mb": gama.techo_mb,
        "hilos": {"total": gama.hilos_total, "asr": gama.hilos_asr, "detector": gama.hilos_detector},
        "gpu": gama.gpu,
        "chunk_ms": chunk_ms,
        "hardware": {
            "sistema": platform.platform(),
            "arquitectura": platform.machine(),
            "cpus": os.cpu_count(),
        },
        "limite": "PC x86 con techo, no telefono ARM. El numero dice con esta memoria y estos hilos, entra o no.",
        "versiones": _versiones(),
        **resultado,
    }


def detector_stub() -> str:
    import detector as det

    return f"{det.DESCRIPCION_STUB} (seed {det.SEED})"


def guardar(reporte: dict, salida: str | Path) -> Path:
    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(reporte, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return salida
