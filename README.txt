Vel-IO 3D: a tool for 3Dvelocity model construction, optimization and time-depth conversion in 3D geological modeling workflow

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

Note: Sample data provided do not represent any real case

Notes on Sample Data folder:
barriers.shp
Polyline shapefile containing barriers for the interpolation (Script 1, Script 2)

ControlPointL1.shp
Point shapefile with control point markers of Layer 1 (Script 2)

ControlPointL2.shp
Point shapefile with control point markers of Layer 2 (Script 2)

L1.shp
Point shapefile with points of Layer 1 in time domain (Script 1)


L2.shp
Point shapefile with points of Layer 2 in time domain (Script 1)

PointTime.shp
Point shapefile with the point to time depth convert (Script 3)

Velocity_L1.shp
Point with the velocity and gradient values for Layer 1 (Script 1, Script 2)

Velocity_L2.shp
Point with the velocity and gradient values for Layer 2 (Script 1, Script 2)

Velocity_L3.shp
Point with the velocity and gradient values for all the data under the bottom of Layer 2 (Script 1, Script 2)

