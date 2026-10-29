// @ts-check
/** @typedef {{suma: number, peso: number}} EstadoRemuestreo */

/**
 * Promedia el área de las muestras en cada intervalo de salida (16 kHz).
 * Conservá el estado entre bloques: a 44,1 kHz las fronteras no son enteras.
 * shortcut: filtro de caja para voz, usar un FIR si se requiere mayor rechazo de alias.
 * @param {Float32Array} muestras Mono, normalmente bloques de 128 muestras.
 * @param {number} hz Frecuencia real del AudioContext.
 * @param {EstadoRemuestreo} estado
 * @returns {{pcm: Int16Array, estado: EstadoRemuestreo}}
 */
export function remuestrearPCM16(muestras, hz, estado = {suma: 0, peso: 0}) {
  if (!Number.isFinite(hz) || hz < 16000) throw new Error('La entrada debe ser de al menos 16 kHz.');
  let {suma, peso} = estado;
  const salida = [];
  for (const muestra of muestras) {
    let restante = 16000 / hz;
    while (restante > 1e-10) {
      const parte = Math.min(restante, 1 - peso);
      suma += muestra * parte;
      peso += parte;
      restante -= parte;
      if (peso >= 1 - 1e-10) {
        // Misma escala y truncamiento que cliente.py; PCM16 little-endian en el envío.
        salida.push(Math.trunc(Math.max(-1, Math.min(1, suma)) * 32767));
        suma = 0;
        peso = 0;
      }
    }
  }
  return {pcm: Int16Array.from(salida), estado: {suma, peso}};
}
