# Vel-IO3D
Vel-IO 3D: A tool for 3D velocity model construction, optimization and time-depth conversion in 3D geological modeling workflow

F.E. Maesano (a, b) and C. D'Ambrogi (b)
Computer and Geosciences http://dx.doi.org/10.1016/j.cageo.2016.11.013

(a) INGV - Istituto Nazionale di Geofisica e Vulcanologia, Rome, Italy
(b) ISPRA - Geological Survey of Italy, Rome, Italy

Corresponding author:
Francesco E. Maesano
francesco.maesano@ingv.it

Vel-IO 3D, version 1.1
Requisites:
ESRI ArcGIS 10.3+
Python 2.7.11
Important Legal Notice: Albeit Authors believe the information to be reliable, mechanical or human errors remain possible. The Authors, thus, do not guarantee the accuracy or completeness of the information provided with Vel-IO 3D tool.

Neither the Authors nor any of the sources of information shall be liable for errors or omissions, or for the use of this information, including any liability or expense incurred, claimed to have resulted from the use of the Vel-IO 3D tool.

The Vel-IO 3D tool is subject to the usual uncertainties of research, subject to change without notice and shall not be relied on as the basis for doing or failing to do something.


#################

Input data must be in shapefile format (.shp): point for all the files except the barriers (polylines)


Before running the Script 1 fill the config1.ini file with the name of shapefiles and the fields
Note: config1.ini is precompiled for the sample data provided with the supplementary materials

Before running Script2 edit the config2.ini file and insert the file name of control points, the requested fields, the number of steps of optimization and the threshold

Before running Script 3 edit the config3.ini file and insert the file name of the points to depth convert and the requested fields.

For any information please read the documentation attached to supplementary materials
