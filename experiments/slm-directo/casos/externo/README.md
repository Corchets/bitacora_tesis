# Sets externos de #144 en formato de casos

Conversaciones externas publicadas el 2026-11-18 a pedido de Luciano para que #52 las pueda correr.
Están fuera de `casos/texto/` para no entrar en desarrollo. Procedencia, criterios y límites:
[relevamiento](../../../../docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md#84-inglés-y-portugués).

| Carpeta | Casos | Líneas | Clase en la referencia | Fuente |
|---|---:|---:|---|---|
| `ingles/` | 16 | 467 | 9 estafas, 4 legítimas, 1 dudosa y 2 sin clase | YouTube (BothBosu), derechos sin verificar |
| `coreano/` | 33 | 6238 | 33 estafas: 27 con `T_R` y 16 con `T_C` | KorCCVi v2, KO-01 a KO-33 |

Cada carpeta tiene `texto/EXT-NNN.txt`, `referencia/EXT-NNN.json`, `roles-protegida.json` y
`correspondencia.json`.

- **Inglés:** copia exacta del set local; los textos coinciden con `MANIFIESTO-TEXTO.json`. Solo 2 de
  los 16 son entrantes: el resto queda fuera del alcance de #151 y se informa aparte.
- **Coreano:** es el set congelado completo. Los 68 archivos coinciden con su
  [manifiesto](../../../../docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json).

> **Aviso: 24 de las 33 referencias de coreano no tienen ficha.** KO-10 a KO-33 llevan un pre-marcado
> de IA (`gpt-6.1-sol`), ajustado con los criterios de Luciano y aprobado por él como lista, sin leer
> las conversaciones. Se reconocen por `revision_humana: false` y el campo `marcado_por`. KO-01 a KO-09
> llevan la ficha de Luciano. Los resultados de #52 tienen que poder separarse por ese campo.

> **Aviso: derechos del coreano.** El [`DATA.md`](https://github.com/selfcontrol7/Korean_Voice_Phishing_Detection/blob/93b5b07a9a73b20d2e686f82e5115ba850e21b9c/DATA.md)
> de la fuente pide no redistribuir el original ni sus derivados. Estas traducciones se publican por
> decisión de Luciano del 2026-11-18, sin permiso de la fuente ni del FSS. El set ya no está en
> custodia: cualquiera puede leer conversaciones y referencias antes de la corrida.

## Cómo correrlos

`correr.py` todavía no los acepta: lee solo `casos/texto/`, y sus referencias no tienen los campos
que exige `casos.py` (`semilla`, `par`, `pedido`, `evidencia`, `que_prueba`, `origen`). `casos.cargar_texto`
sí lee los textos si `DIR_TEXTO` apunta a la carpeta. Falta el cargador de #52.
