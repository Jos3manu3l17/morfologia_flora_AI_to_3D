-- ==========================================================
-- SILUETA 3D GENERADA AUTOMATICAMENTE
-- Puntos en el contorno: 68
-- ==========================================================

delete objects

shp = splineShape pos:[0,0,0] name:"mango_3d_2"
addNewSpline shp

addKnot shp 1 #corner #line [27.990, 337.805, 0]
addKnot shp 1 #corner #line [9.530, 327.665, 0]
addKnot shp 1 #corner #line [-28.250, 293.935, 0]
addKnot shp 1 #corner #line [-44.160, 282.285, 0]
addKnot shp 1 #corner #line [-87.350, 244.495, 0]
addKnot shp 1 #corner #line [-94.300, 237.595, 0]
addKnot shp 1 #corner #line [-119.340, 206.835, 0]
addKnot shp 1 #corner #line [-140.520, 173.595, 0]
addKnot shp 1 #corner #line [-152.810, 146.475, 0]
addKnot shp 1 #corner #line [-160.450, 118.985, 0]
addKnot shp 1 #corner #line [-173.040, 82.455, 0]
addKnot shp 1 #corner #line [-179.130, 46.485, 0]
addKnot shp 1 #corner #line [-179.300, -7.275, 0]
addKnot shp 1 #corner #line [-177.870, -16.135, 0]
addKnot shp 1 #corner #line [-177.430, -34.045, 0]
addKnot shp 1 #corner #line [-174.080, -51.645, 0]
addKnot shp 1 #corner #line [-163.050, -95.865, 0]
addKnot shp 1 #corner #line [-126.660, -173.985, 0]
addKnot shp 1 #corner #line [-110.070, -197.845, 0]
addKnot shp 1 #corner #line [-63.940, -245.685, 0]
addKnot shp 1 #corner #line [-49.260, -257.275, 0]
addKnot shp 1 #corner #line [-33.390, -267.605, 0]
addKnot shp 1 #corner #line [-16.170, -276.425, 0]
addKnot shp 1 #corner #line [1.440, -283.965, 0]
addKnot shp 1 #corner #line [38.930, -296.115, 0]
addKnot shp 1 #corner #line [79.860, -302.345, 0]
addKnot shp 1 #corner #line [112.470, -302.005, 0]
addKnot shp 1 #corner #line [124.300, -303.365, 0]
addKnot shp 1 #corner #line [134.450, -307.465, 0]
addKnot shp 1 #corner #line [142.910, -312.585, 0]
addKnot shp 1 #corner #line [174.480, -337.805, 0]
addKnot shp 1 #corner #line [179.300, -332.665, 0]
addKnot shp 1 #corner #line [174.550, -327.545, 0]
addKnot shp 1 #corner #line [167.880, -323.375, 0]
addKnot shp 1 #corner #line [135.180, -308.375, 0]
addKnot shp 1 #corner #line [126.260, -302.695, 0]
addKnot shp 1 #corner #line [113.250, -289.025, 0]
addKnot shp 1 #corner #line [100.040, -266.715, 0]
addKnot shp 1 #corner #line [75.770, -230.255, 0]
addKnot shp 1 #corner #line [65.810, -208.935, 0]
addKnot shp 1 #corner #line [61.260, -195.055, 0]
addKnot shp 1 #corner #line [51.420, -174.705, 0]
addKnot shp 1 #corner #line [28.460, -135.305, 0]
addKnot shp 1 #corner #line [19.380, -109.665, 0]
addKnot shp 1 #corner #line [18.520, -102.955, 0]
addKnot shp 1 #corner #line [15.710, -96.545, 0]
addKnot shp 1 #corner #line [10.470, -76.565, 0]
addKnot shp 1 #corner #line [8.140, -56.155, 0]
addKnot shp 1 #corner #line [3.850, -36.105, 0]
addKnot shp 1 #corner #line [1.070, -1.725, 0]
addKnot shp 1 #corner #line [-1.380, 4.255, 0]
addKnot shp 1 #corner #line [-5.840, 31.335, 0]
addKnot shp 1 #corner #line [-4.860, 79.935, 0]
addKnot shp 1 #corner #line [-3.560, 87.015, 0]
addKnot shp 1 #corner #line [-3.470, 101.145, 0]
addKnot shp 1 #corner #line [-0.470, 108.485, 0]
addKnot shp 1 #corner #line [2.360, 123.265, 0]
addKnot shp 1 #corner #line [0.680, 144.475, 0]
addKnot shp 1 #corner #line [-1.810, 158.575, 0]
addKnot shp 1 #corner #line [0.430, 187.645, 0]
addKnot shp 1 #corner #line [0.570, 210.795, 0]
addKnot shp 1 #corner #line [4.000, 242.305, 0]
addKnot shp 1 #corner #line [2.890, 250.115, 0]
addKnot shp 1 #corner #line [4.210, 288.585, 0]
addKnot shp 1 #corner #line [8.410, 303.665, 0]
addKnot shp 1 #corner #line [14.570, 318.635, 0]
addKnot shp 1 #corner #line [18.750, 325.755, 0]
addKnot shp 1 #corner #line [24.980, 332.295, 0]

close shp 1
updateShape shp

-- Extrusion: le da volumen 3D a la silueta
addModifier shp (Extrude amount:15.0 segments:1 capStart:on capEnd:on)

-- Convertir a Editable Poly para facilitar edicion posterior
convertToPoly shp

max zoomext sel all

print ("Silueta 3D creada: " + shp.name + " (" + 68 as string + " puntos)")