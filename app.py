from flask import Flask, render_template, jsonify
import math
from operator import itemgetter

app = Flask(__name__)

coord = {
        'Jiloyork': (19.916012,-99.580580),
        'Toluca': (19.289165, -99.655697),
        'Atlacomulco': (19.799520, -99.873844),
        'Guadalajara': (20.677754472859146, -103.346253548771137),
        'Monterrey': (25.69161110, -100.321838480256),
        'QuintanaRoo': (21.163111924844458, -86.80231502121464),
        'Michoacan': (19.701400113725654, -101.20829680213464),
        'Aguascalientes': (21.87641043660486, -102.26438663286967),
        'CDMX': (19.432713075976878, -99.13318344772986),
        'QRO': (20.59719437542255, -100.38667040246602)
    }
    
pedidos = {
        'Jiloyork': 10,
        'Toluca': 15,
        'Atlacomulco': 30,
        'Guadalajara': 20,
        'Monterrey': 40,
        'QuintanaRoo': 50,
        'Michoacan': 25,
        'Aguascalientes': 45,
        'CDMX': 60,
        'QRO': 100
    }
    
almacen = (19.92273824869188, -99.33732649364755)
max_carga = 400

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def en_ruta(rutas, c):
    ruta = None
    for r in rutas:
        if c in r:
            ruta = r
    return ruta

def peso_ruta(ruta):
    total = 0
    for c in ruta:
        total = total + pedidos[c]
    return total

def vrp_voraz():
    # calcular los ahorros
    s = {}
    for c1 in coord:
        for c2 in coord:
            if c1 != c2:
                if not (c2, c1) in s:
                    d_c1_c2 = distancia(coord[c1], coord[c2])
                    d_c1_almacen = distancia(coord[c1], almacen)
                    d_c2_almacen = distancia(coord[c2], almacen)
                    s[c1, c2] = d_c1_almacen + d_c2_almacen - d_c1_c2
    # ordenar ahorros
    s = sorted(s.items(), key=itemgetter(1), reverse=True)

    # Construir rutas
    rutas = []
    for k, v in s:
        rc1 = en_ruta(rutas, k[0])
        rc2 = en_ruta(rutas, k[1])
        if rc1 == None and rc2 == None:
            # No están en ninguna ruta.
            if peso_ruta([k[0], k[1]]) <= max_carga:
                rutas.append([k[0], k[1]])
        elif rc1 != None and rc2 == None:
            # Ciudad 1 ya en una ruta. Agregamos la ciudad 2
            if rc1[0] == k[0]:
                if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                    rutas[rutas.index(rc1)].insert(0, k[1])
            elif rc1[len(rc1)-1] == k[0]:
                if peso_ruta(rc1) + peso_ruta([k[1]]) <= max_carga:
                    rutas[rutas.index(rc1)].append(k[1])
        elif rc1 == None and rc2 != None:
            # ciudad 2 ya en una ruta. Agregamos la ciudad 1
            if rc2[0] == k[1]:
                if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                    rutas[rutas.index(rc2)].insert(0, k[0])
            elif rc2[len(rc2) -1] == k[1]:
                if peso_ruta(rc2) + peso_ruta([k[0]]) <= max_carga:
                    rutas[rutas.index(rc2)].append(k[0])
        elif rc1 != None and rc2 != None and rc1 != rc2:
            # ciudad 1 y 2 ya en una ruta. Tratamos de unirlas
            if rc1[0] == k[0] and rc2[len(rc2)-1] == k[1]:
                if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                    rutas[rutas.index(rc2)].extend(rc1)
                    rutas.remove(rc1)
            elif rc1[len(rc1)-1] == k[0] and rc2[0] == k[1]:
                if peso_ruta(rc1) + peso_ruta(rc2) <= max_carga:
                    rutas[rutas.index(rc1)].extend(rc2)
                    rutas.remove(rc2)
    return rutas

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/mostrar-rutas', methods= ['GET', 'POST'])
def vrpvoraz():
    rutas = vrp_voraz()
    for rutas in rutas:
        return jsonify({
            'rutas': rutas
        })

if __name__ == "__main__":
    app.run(debug = False, host = '0.0.0.0')