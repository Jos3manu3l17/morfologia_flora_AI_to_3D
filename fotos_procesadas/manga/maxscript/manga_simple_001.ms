-- ==========================================================
-- SILUETA 3D GENERADA AUTOMATICAMENTE
-- Puntos en el contorno: 2
-- ==========================================================

delete objects

shp = splineShape pos:[0,0,0] name:"manga_simple_1"
addNewSpline shp

addKnot shp 1 #corner #line [nan, nan, 0]
addKnot shp 1 #corner #line [nan, nan, 0]

close shp 1
updateShape shp

-- Extrusion: le da volumen 3D a la silueta
addModifier shp (Extrude amount:15.0 segments:1 capStart:on capEnd:on)

-- Convertir a Editable Poly para facilitar edicion posterior
convertToPoly shp

max zoomext sel all

print ("Silueta 3D creada: " + shp.name + " (" + 2 as string + " puntos)")