-- ==========================================================
-- SILUETA 3D GENERADA AUTOMATICAMENTE
-- Puntos en el contorno: 57
-- ==========================================================

delete objects

shp = splineShape pos:[0,0,0] name:"mango_3d_1"
addNewSpline shp

addKnot shp 1 #corner #line [-10.655, 344.905, 0]
addKnot shp 1 #corner #line [-20.835, 334.175, 0]
addKnot shp 1 #corner #line [-29.355, 315.245, 0]
addKnot shp 1 #corner #line [-39.825, 301.105, 0]
addKnot shp 1 #corner #line [-68.365, 267.345, 0]
addKnot shp 1 #corner #line [-88.065, 239.395, 0]
addKnot shp 1 #corner #line [-109.175, 200.545, 0]
addKnot shp 1 #corner #line [-118.955, 176.105, 0]
addKnot shp 1 #corner #line [-125.195, 150.735, 0]
addKnot shp 1 #corner #line [-128.305, 125.095, 0]
addKnot shp 1 #corner #line [-136.845, 90.165, 0]
addKnot shp 1 #corner #line [-142.635, 46.325, 0]
addKnot shp 1 #corner #line [-141.355, -22.715, 0]
addKnot shp 1 #corner #line [-138.845, -39.445, 0]
addKnot shp 1 #corner #line [-129.525, -72.335, 0]
addKnot shp 1 #corner #line [-118.465, -96.125, 0]
addKnot shp 1 #corner #line [-95.215, -153.215, 0]
addKnot shp 1 #corner #line [-84.635, -167.755, 0]
addKnot shp 1 #corner #line [-81.075, -175.935, 0]
addKnot shp 1 #corner #line [-66.555, -197.155, 0]
addKnot shp 1 #corner #line [-46.495, -224.795, 0]
addKnot shp 1 #corner #line [-35.265, -237.265, 0]
addKnot shp 1 #corner #line [-11.015, -259.755, 0]
addKnot shp 1 #corner #line [-4.265, -264.825, 0]
addKnot shp 1 #corner #line [10.935, -273.185, 0]
addKnot shp 1 #corner #line [17.125, -278.205, 0]
addKnot shp 1 #corner #line [33.265, -285.925, 0]
addKnot shp 1 #corner #line [50.695, -292.255, 0]
addKnot shp 1 #corner #line [87.775, -301.105, 0]
addKnot shp 1 #corner #line [105.445, -307.345, 0]
addKnot shp 1 #corner #line [117.685, -318.535, 0]
addKnot shp 1 #corner #line [127.685, -331.815, 0]
addKnot shp 1 #corner #line [130.675, -338.885, 0]
addKnot shp 1 #corner #line [136.915, -344.905, 0]
addKnot shp 1 #corner #line [142.635, -340.435, 0]
addKnot shp 1 #corner #line [140.645, -334.675, 0]
addKnot shp 1 #corner #line [112.665, -304.845, 0]
addKnot shp 1 #corner #line [106.685, -290.665, 0]
addKnot shp 1 #corner #line [100.245, -261.545, 0]
addKnot shp 1 #corner #line [90.805, -233.095, 0]
addKnot shp 1 #corner #line [83.415, -196.935, 0]
addKnot shp 1 #corner #line [76.835, -174.915, 0]
addKnot shp 1 #corner #line [60.225, -130.375, 0]
addKnot shp 1 #corner #line [37.755, -39.295, 0]
addKnot shp 1 #corner #line [34.845, -18.215, 0]
addKnot shp 1 #corner #line [34.395, -3.775, 0]
addKnot shp 1 #corner #line [21.375, 43.805, 0]
addKnot shp 1 #corner #line [20.595, 73.185, 0]
addKnot shp 1 #corner #line [16.315, 108.675, 0]
addKnot shp 1 #corner #line [17.555, 146.155, 0]
addKnot shp 1 #corner #line [6.275, 181.305, 0]
addKnot shp 1 #corner #line [-5.255, 253.395, 0]
addKnot shp 1 #corner #line [-12.845, 281.675, 0]
addKnot shp 1 #corner #line [-15.135, 296.855, 0]
addKnot shp 1 #corner #line [-14.675, 319.725, 0]
addKnot shp 1 #corner #line [-11.995, 335.085, 0]
addKnot shp 1 #corner #line [-9.255, 341.715, 0]

close shp 1
updateShape shp

-- Extrusion: le da volumen 3D a la silueta
addModifier shp (Extrude amount:15.0 segments:1 capStart:on capEnd:on)

-- Convertir a Editable Poly para facilitar edicion posterior
convertToPoly shp

max zoomext sel all

print ("Silueta 3D creada: " + shp.name + " (" + 57 as string + " puntos)")