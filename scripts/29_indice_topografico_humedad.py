# -*- coding: utf-8 -*-
"""Indice topografico de humedad (TWI) para Gipuzkoa, desde el MDT LiDAR.

    TWI = ln( a / tan(beta) )

  a    = area de drenaje acumulada por unidad de anchura de curva de nivel
  beta = pendiente local

Alto  -> mucha ladera drenando aqui y poca pendiente: se encharca (vaguadas)
Bajo  -> loma convexa y empinada: escurre (cordales)

Pasos: relleno de depresiones (priority-flood), direcciones de flujo D8 y
acumulacion procesando las celdas de mayor a menor cota.

Se trabaja a 50 m: a 25 m son 6,3 millones de celdas y el bucle de
acumulacion en Python puro no lo justifica para lo que necesitamos.
"""
import heapq, time
import numpy as np
import tifffile

F = 2                    # 25 m -> 50 m
PX = 25.0 * F


def carga():
    A = tifffile.imread('mdt_lidar_2017_25m_etrs89.tif').astype('float32')
    A[A < -1e30] = np.nan
    r0, r1, c0, c1 = np.load('gip_win.npy')
    mask = np.load('gip_mask.npy')
    # margen: el agua entra desde fuera del limite administrativo
    PAD = 60
    R0, R1 = max(r0 - PAD, 0), min(r1 + PAD, A.shape[0])
    C0, C1 = max(c0 - PAD, 0), min(c1 + PAD, A.shape[1])
    Z = A[R0:R1, C0:C1]
    h2, w2 = Z.shape[0] // F, Z.shape[1] // F
    Z = np.nanmean(Z[:h2 * F, :w2 * F].reshape(h2, F, w2, F), axis=(1, 3))
    off = (r0 - R0, c0 - C0)
    return Z.astype('float32'), off, mask, (r1 - r0, c1 - c0)


def rellena(Z):
    """Priority-flood: elimina depresiones para que todo tenga salida."""
    H, W = Z.shape
    val = np.isfinite(Z)
    out = np.where(val, Z, np.inf).astype('float64')
    visto = np.zeros((H, W), bool)
    pq = []
    # semillas: borde del dominio y celdas junto a nodata
    for i in range(H):
        for j in (0, W - 1):
            if val[i, j]:
                heapq.heappush(pq, (out[i, j], i, j)); visto[i, j] = True
    for j in range(W):
        for i in (0, H - 1):
            if val[i, j] and not visto[i, j]:
                heapq.heappush(pq, (out[i, j], i, j)); visto[i, j] = True
    borde = val & ~np.pad(val, 1, constant_values=False)[:-2, 1:-1] \
        if False else None
    inval = ~val
    vecino_nodata = np.zeros((H, W), bool)
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        vecino_nodata |= np.roll(np.roll(inval, di, 0), dj, 1)
    sem = val & vecino_nodata & ~visto
    for i, j in zip(*np.where(sem)):
        heapq.heappush(pq, (out[i, j], int(i), int(j))); visto[i, j] = True

    D = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    while pq:
        z, i, j = heapq.heappop(pq)
        for di, dj in D:
            a, b = i + di, j + dj
            if a < 0 or a >= H or b < 0 or b >= W or visto[a, b] or not val[a, b]:
                continue
            visto[a, b] = True
            if out[a, b] < z:
                out[a, b] = z            # elevar hasta el nivel de salida
            heapq.heappush(pq, (out[a, b], a, b))
    return np.where(val, out, np.nan).astype('float32')


def acumula(Z):
    """D8: direccion de maxima pendiente y acumulacion de area."""
    H, W = Z.shape
    val = np.isfinite(Z)
    Zf = np.where(val, Z, np.inf)
    D = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
    dist = np.array([np.hypot(di, dj) for di, dj in D]) * PX
    mejor = np.full((H, W), -1, dtype='int8')
    caida = np.zeros((H, W), dtype='float32')
    for k, (di, dj) in enumerate(D):
        vec = np.roll(np.roll(Zf, -di, 0), -dj, 1)
        # los bordes se envuelven: anularlos
        if di == 1:  vec[-1, :] = np.inf
        if di == -1: vec[0, :] = np.inf
        if dj == 1:  vec[:, -1] = np.inf
        if dj == -1: vec[:, 0] = np.inf
        g = (Zf - vec) / dist[k]
        m = (g > caida) & val
        caida[m] = g[m]
        mejor[m] = k
    acc = np.ones((H, W), dtype='float64')
    acc[~val] = 0
    orden = np.argsort(np.where(val, -Z, np.inf).ravel(), kind='stable')
    nval = int(val.sum())
    Dr = np.array([d[0] for d in D]); Dc = np.array([d[1] for d in D])
    mf = mejor.ravel(); af = acc.ravel()
    for p in orden[:nval]:
        k = mf[p]
        if k < 0:
            continue
        i, j = divmod(int(p), W)
        a, b = i + Dr[k], j + Dc[k]
        if 0 <= a < H and 0 <= b < W:
            af[a * W + b] += af[p]
    return acc.reshape(H, W), caida


def main():
    t0 = time.time()
    Z, off, mask, forma = carga()
    print('malla %s a %.0f m  (%.0fs)' % (str(Z.shape), PX, time.time() - t0), flush=True)
    Zr = rellena(Z)
    print('depresiones rellenadas (%.0fs)' % (time.time() - t0), flush=True)
    acc, pend = acumula(Zr)
    print('acumulacion de flujo lista (%.0fs)' % (time.time() - t0), flush=True)
    # TWI. Pendiente minima para no dividir por cero en los llanos.
    beta = np.maximum(pend, 0.001)
    a = acc * PX                      # area por unidad de anchura
    twi = np.log(a / beta)
    np.save('twi_50m.npy', twi.astype('float32'))
    np.save('twi_off.npy', np.array([off[0] // F, off[1] // F, forma[0] // F, forma[1] // F]))
    v = twi[np.isfinite(twi)]
    print()
    print('TWI: min %.1f  p5 %.1f  mediana %.1f  p95 %.1f  max %.1f'
          % (v.min(), np.percentile(v, 5), np.median(v), np.percentile(v, 95), v.max()))
    print('celdas con mucha agua acumulada (TWI>10): %.1f %%' % (100 * (v > 10).mean()))


if __name__ == '__main__':
    main()
