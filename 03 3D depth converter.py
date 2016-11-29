# v.1.0 This script uses the prevoiusly built velocity model to depth convert any point within the workspace

#The point data of an horizon or a fault will be
#depth converted using the 3D model

import math
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput=True

#Step 1 import configuration file
import sys, os
path=os.path.dirname(os.path.abspath(sys.argv[0]))
import imp
filename=path+'\\config3.ini'
f=open(filename)
var=imp.load_source('var','',f)
f.close()

#initialize new lists for the depth conversion

pointData=var.pointData #input data in twt
pointZList=[] #list of output data in depth
twtData=var.pointTwtField #field with twt information
indexList=[] #index values
obNameField=var.obNameField #field of the object names

V0RasterList=var.V0RasterList #list of raster interpolation for v0 values
KRasterList=var.KRasterList #list of raster interpolation for k values
TwtRasterList=var.TwtRasterList #list of raster interpolation for twt of key horizons
ZRasterList=var.ZRasterList #list of raster interpolation for z of key horizons
inRasterList=[] #temporary list
inRaster=[] #temporary list
fields=[] #temporary list
logList=[] #list of log


#set the number of key horizons and the workspace folder
l=var.horizons
#set the datum
datum=var.reference

# Step 1 insert input data
#Step 1.1. Insert data of the velocity model 
print "Initializing data"
workspace=var.folder
env.workspace=workspace

log="point to depth convert"+pointData
logList.append(log)

#copy the data in twt to a new file in which calculation will be made
outname="Z_"+pointData
arcpy.Copy_management(pointData,outname)
inputShp=outname
log="data copied in: "+str(outname)
logList.append(log)

#re-initialize temporary lists
del inRasterList[:]  
del inRaster[:]
del fields[:]

#Step 2 Extract all tn-1 values and assign layer position
#create a variable with the index value of TWT to call data in the lists
for element in TwtRasterList:
    inRasterList.append(element)
arcpy.CheckOutExtension("Spatial")
fields.append(twtData) #add to the list the field with the twt data of the points to be converted
arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList) #extract value of twt from the velocity model
newField="tn_1" #add a field to be populated with the correct value of tn-1 for each record
arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
layerField="layer"
arcpy.AddField_management(inputShp, layerField, "SHORT","","","","","NULLABLE")
for element in inRasterList: #populate the list of fields
    fields.append(element)
fields.append(newField) #add to the list the field for assign the tn-1 output values
fields.append(layerField) #add the field with the number of the layer

 
## initialize the cursor loop to calculate the tn-1 value and assign number of layer for the point
with arcpy.da.UpdateCursor(inputShp, fields) as selectT:
    
    for row in selectT:
        if row[0]>row[l]:
            row[l+1]=row[l]
            row[l+2]=l+1 
        elif row[0]<=row[1]:
            row[l+1]=0
            row[l+2]=1
        elif row[0]>row[1] and row[0]<=row[l]:
            a=2
            while a<=l:
                if row[0]>row[a-1] and row[0]<=[a]:
                    row[l+1]=row[a-1]
                    row[l+2]=a
                a+=1
        selectT.updateRow(row)
        
log="tn-1 and layer assigned"
logList.append(log)

#Step 3 Extract the remaining variables
#Step 3.1 extract Zn-1 
#extract all value of Zn-1
#re-initialize the inRasterList and fields list
del inRasterList[:]
del fields[:]
#populate inRasterList with Z raster value
for element in ZRasterList:
    inRasterList.append(element)

arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList) #extract value of Z from the velocity model
#add layer field to fields list (index 0)
fields.append(layerField)
for element in inRasterList: #populate the list of fields
    fields.append(element)
newField="Zn_1" #add a field to be populated with the correct value of Zn-1 for each record
arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
fields.append(newField)

with arcpy.da.UpdateCursor(inputShp,fields) as selectZ:
    for row in selectZ:
        if row[0]==1:
            row[l+1]=0
        else:
            a=2
            while a<=l+1:
                if row[0]==a:
                    row[l+1]=row[a-1]
                a+=1
        selectZ.updateRow(row)
        
log="Zn-1 values assigned"
logList.append(log)

#Step 3.2 extract all value of V
#re-initialize the inRasterList and fields list
del inRasterList[:]
del fields[:]
#populate inRasterList with v0 raster value
for element in V0RasterList:
    inRasterList.append(element)

arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList) #extract value of V0 from the velocity model
#add layer field to fields list (index 0)
fields.append(layerField)
for element in inRasterList: #populate the list of fields
    fields.append(element)
newField="V0" #add a field to be populated with the correct value of V0 for each record
arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
fields.append(newField)

with arcpy.da.UpdateCursor(inputShp,fields) as selectV0:
    for row in selectV0:
        a=1
        while a<=l+1:
            if row[0]==a:
                row[l+2]=row[a]
            a+=1
        selectV0.updateRow(row)
        log=str(row[0]) + " velocity: " + str(row[l+2])
        logList.append(log)

log="V0 data assigned"
logList.append(log)

#Step 3.3 extract value of k         
# extract all value of k
#re-initialize the inRasterList and fields list
del inRasterList[:]
del fields[:]
#populate inRasterList with k raster value
for element in KRasterList:
    inRasterList.append(element)

arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList) #extract value of K from the velocity model
#add layer field to fields list (index 0)
fields.append(layerField)
for element in inRasterList: #populate the list of fields
    fields.append(element)
newField="k" #add a field to be populated with the correct value of k for each record
arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
fields.append(newField)

with arcpy.da.UpdateCursor(inputShp,fields) as selectK:
    for row in selectK:
        a=1
        while a<=l+1:
            if row[0]==a:
                row[l+2]=row[a]
            a+=1
        selectK.updateRow(row)
        log=str(row[0]) + " gradient: " + str(row[l+2])
        logList.append(log)
log="K data assigned"
logList.append(log)

arcpy.CheckInExtension("Spatial")

#Step 4 calculate the Z value
#re initialize fields list
del fields[:]
fields.append(twtData) #index 0
fields.append('tn_1') #index 1 
fields.append('Zn_1') #index 2 
fields.append('V0') #index 3 
fields.append('k') #index 4
newField="Z" #add field Z in which calculate final values, index 5
arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
fields.append(newField)
with arcpy.da.UpdateCursor(inputShp,fields) as calcZ:
    for row in calcZ:
        try:
            if row[4]==0: #if gradient is 0 the script uses v0 as average velocity
                Dt=(row[0]-row[1])/2000
                row[5]=row[2]+row[3]*Dt
                calcZ.updateRow(row)
                
            else: #else the script uses the instantanueous velocity equation to depth converte each point
                Dt=(row[0]-row[1])/2000
                row[5]=row[2]+row[3]*(math.exp(row[4]*Dt)-1)/row[4]
                calcZ.updateRow(row)
                
        except:
            print arcpy.GetMessages()

            continue
log="Z value calculated"
logList.append(log)

#Step 5 create output file 
deleteField=[]
outShape="outPointZ.shp"
del fields[:]
arcpy.Copy_management(inputShp,outShape) #copy the value in a new output file
fields=arcpy.ListFields(outShape)
for field in fields:
    
    deleteField.append(field.name)
#eliminate the required field from the list of DeleteField. This will save these information for the out file
deleteField.remove("FID")
deleteField.remove("Id")
deleteField.remove("Shape")
deleteField.remove(obNameField)
deleteField.remove("Z")
arcpy.DeleteField_management(outShape,deleteField)
arcpy.AddXY_management(outShape)
log="Result saved in "+outShape
del fields[:]
print "points depth converted successfully"
filename=path+"\\log3.txt"
out_file = open(filename,"w")
for element in logList:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()
