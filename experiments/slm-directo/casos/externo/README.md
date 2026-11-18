# Sets externos de #144 en formato de casos

Conversaciones externas con ficha de Luciano, publicadas el 2026-11-18 a su pedido para que #52 las
pueda correr. Están fuera de `casos/texto/` para no entrar en desarrollo. Procedencia, criterios y
límites: [relevamiento](../../../../docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#84-inglés-y-portugués).

| Carpeta | Casos | Líneas | Clase en la referencia | Fuente |
|---|---:|---:|---|---|
| `ingles/` | 16 | 467 | 9 estafas, 4 legítimas, 1 dudosa y 2 sin clase | YouTube (BothBosu), derechos sin verificar |
| `coreano/` | 9 | 774 | 9 estafas: 7 con `T_R`, 5 de ellas con `T_C` | KorCCVi v2, KO-01 a KO-09 |

Cada carpeta tiene `texto/EXT-NNN.txt`, `referencia/EXT-NNN.json`, `roles-protegida.json` y
`correspondencia.json`.

- **Inglés:** copia exacta del set local; los textos coinciden con `MANIFIESTO-TEXTO.json`. Solo 2 de
  los 16 son entrantes: el resto queda fuera del alcance de #151 y se informa aparte.
- **Coreano:** `texto/` y `referencia/` coinciden con el
  [manifiesto del set congelado](../../../../docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json).
  `roles-protegida.json` y `correspondencia.json` son recortes a estos 9 casos, así que su hash no es
  el del manifiesto. Los otros 24 casos del set no tienen ficha y siguen fuera de Git.

> **Derechos del coreano.** El [`DATA.md`](https://github.com/selfcontrol7/Korean_Voice_Phishing_Detection/blob/93b5b07a9a73b20d2e686f82e5115ba850e21b9c/DATA.md)
> de la fuente pide no redistribuir el original ni sus derivados. Estas traducciones se publican por
> decisión de Luciano del 2026-11-18, sin permiso de la fuente ni del FSS.

## Cómo correrlos

`correr.py` todavía no los acepta: lee solo `casos/texto/`, y sus referencias no tienen los campos
que exige `casos.py` (`semilla`, `par`, `pedido`, `evidencia`, `que_prueba`, `origen`). `casos.cargar_texto`
sí lee los textos si `DIR_TEXTO` apunta a la carpeta. Falta el cargador de #52.
