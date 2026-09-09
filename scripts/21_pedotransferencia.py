"""Capacidad de agua disponible del suelo a partir de la textura.

Funciones de pedotransferencia de Saxton & Rawls (2006), Soil Sci. Soc. Am. J. 70:1569-1578.
Estiman capacidad de campo (33 kPa) y punto de marchitez (1500 kPa) a partir de los
porcentajes de arena y arcilla y del contenido en materia organica.
La diferencia entre ambos es el agua disponible para las plantas y, por extension,
para el micelio.
"""
import numpy as np

def saxton_rawls(arena, arcilla, mo=2.5):
    """arena, arcilla: % en peso. mo: materia organica en %. Devuelve (CC, PMP) en fraccion volumetrica."""
    S=arena/100.0; C=arcilla/100.0; OM=mo
    # punto de marchitez (1500 kPa)
    t1500t = -0.024*S + 0.487*C + 0.006*OM + 0.005*(S*OM) - 0.013*(C*OM) + 0.068*(S*C) + 0.031
    t1500  = t1500t + (0.14*t1500t - 0.02)
    # capacidad de campo (33 kPa)
    t33t = -0.251*S + 0.195*C + 0.011*OM + 0.006*(S*OM) - 0.027*(C*OM) + 0.452*(S*C) + 0.299
    t33  = t33t + (1.283*t33t**2 - 0.374*t33t - 0.015)
    return t33, t1500

def agua_disponible_mm(arena, arcilla, prof_cm=50.0, mo=2.5, pedregosidad=0.0):
    """Agua disponible en mm para un espesor de suelo dado."""
    cc, pmp = saxton_rawls(arena, arcilla, mo)
    awc = np.clip(cc - pmp, 0.02, 0.35)          # fraccion volumetrica
    return awc * prof_cm * 10.0 * (1.0 - pedregosidad)

if __name__=='__main__':
    print('Comprobacion con texturas de referencia (prof. 50 cm, MO 2,5 %):')
    print('%-22s %6s %6s %8s %8s %8s'%('textura','arena','arcilla','CC','PMP','mm'))
    for nom,a,c in [('arenosa',85,5),('franco-arenosa',65,10),('franca',40,20),
                    ('franco-limosa',20,15),('franco-arcillosa',35,30),('arcillosa',20,50)]:
        cc,pmp=saxton_rawls(a,c)
        print('%-22s %6d %6d %8.3f %8.3f %8.0f'%(nom,a,c,cc,pmp,agua_disponible_mm(a,c)))
