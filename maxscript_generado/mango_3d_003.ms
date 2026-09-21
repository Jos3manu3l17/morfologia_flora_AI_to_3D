-- ==========================================================
-- SILUETA 3D GENERADA AUTOMATICAMENTE
-- Puntos en el contorno: 51
-- ==========================================================

delete objects

shp = splineShape pos:[0,0,0] name:"mango_3d_3"
addNewSpline shp

addKnot shp 1 #corner #line [-30.230, 342.530, 0]
addKnot shp 1 #corner #line [-39.220, 332.130, 0]
addKnot shp 1 #corner #line [-55.670, 299.190, 0]
addKnot shp 1 #corner #line [-78.450, 260.660, 0]
addKnot shp 1 #corner #line [-87.640, 240.110, 0]
addKnot shp 1 #corner #line [-101.860, 202.510, 0]
addKnot shp 1 #corner #line [-106.050, 187.080, 0]
addKnot shp 1 #corner #line [-110.790, 155.030, 0]
addKnot shp 1 #corner #line [-111.400, 130.900, 0]
addKnot shp 1 #corner #line [-115.540, 98.140, 0]
addKnot shp 1 #corner #line [-116.170, 73.690, 0]
addKnot shp 1 #corner #line [-108.760, -7.610, 0]
addKnot shp 1 #corner #line [-95.790, -64.400, 0]
addKnot shp 1 #corner #line [-75.410, -121.850, 0]
addKnot shp 1 #corner #line [-57.750, -159.630, 0]
addKnot shp 1 #corner #line [-41.740, -188.010, 0]
addKnot shp 1 #corner #line [-19.000, -220.440, 0]
addKnot shp 1 #corner #line [2.380, -243.230, 0]
addKnot shp 1 #corner #line [38.610, -273.140, 0]
addKnot shp 1 #corner #line [87.910, -305.380, 0]
addKnot shp 1 #corner #line [98.470, -323.760, 0]
addKnot shp 1 #corner #line [100.760, -331.380, 0]
addKnot shp 1 #corner #line [105.280, -337.920, 0]
addKnot shp 1 #corner #line [111.800, -342.530, 0]
addKnot shp 1 #corner #line [116.170, -336.550, 0]
addKnot shp 1 #corner #line [102.890, -306.320, 0]
addKnot shp 1 #corner #line [100.300, -295.220, 0]
addKnot shp 1 #corner #line [100.130, -269.180, 0]
addKnot shp 1 #corner #line [101.180, -262.450, 0]
addKnot shp 1 #corner #line [95.520, -212.800, 0]
addKnot shp 1 #corner #line [95.490, -198.250, 0]
addKnot shp 1 #corner #line [96.780, -191.070, 0]
addKnot shp 1 #corner #line [95.050, -168.900, 0]
addKnot shp 1 #corner #line [84.270, -124.050, 0]
addKnot shp 1 #corner #line [82.480, -86.450, 0]
addKnot shp 1 #corner #line [80.740, -71.390, 0]
addKnot shp 1 #corner #line [77.290, -56.480, 0]
addKnot shp 1 #corner #line [70.740, 10.620, 0]
addKnot shp 1 #corner #line [66.730, 25.420, 0]
addKnot shp 1 #corner #line [62.930, 31.800, 0]
addKnot shp 1 #corner #line [53.820, 60.250, 0]
addKnot shp 1 #corner #line [46.710, 118.310, 0]
addKnot shp 1 #corner #line [42.710, 132.630, 0]
addKnot shp 1 #corner #line [37.260, 161.240, 0]
addKnot shp 1 #corner #line [25.900, 189.620, 0]
addKnot shp 1 #corner #line [17.370, 217.360, 0]
addKnot shp 1 #corner #line [-3.780, 264.050, 0]
addKnot shp 1 #corner #line [-7.940, 270.230, 0]
addKnot shp 1 #corner #line [-22.810, 301.280, 0]
addKnot shp 1 #corner #line [-29.370, 326.320, 0]
addKnot shp 1 #corner #line [-28.850, 337.840, 0]

close shp 1
updateShape shp

-- Extrusion: le da volumen 3D a la silueta
addModifier shp (Extrude amount:15.0 segments:1 capStart:on capEnd:on)

-- Convertir a Editable Poly para facilitar edicion posterior
convertToPoly shp

max zoomext sel all

print ("Silueta 3D creada: " + shp.name + " (" + 51 as string + " puntos)")