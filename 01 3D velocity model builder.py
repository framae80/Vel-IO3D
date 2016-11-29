# v.1.1 This script creates a multi-layer velocity model from point data

import math
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput=True

#Step 1 import configuration file
import sys, os
path=os.path.dirname(os.path.abspath(sys.argv[0]))
import imp
filename=path+'\\config1.ini'
f=open(filename)
var=imp.load_source('var','',f)
f.close()


#initialize the lists of variables
inShpV0KList=var.inShpV0KList
inShpZList=[] #list of the depth converted files
inFieldV0List=var.inFieldV0List
inFieldKList=var.inFieldKList
inShpTwtList=var.inShpTwtList
inFieldTwtList=var.inFieldTwtList
inShpBarriersList=var.inShpBarriersList
inFieldZList=[] #list of the field name with Z information
inFieldTwtPrevList=[] #list of the field with the twt data of the previous horizon
inFieldZPrevList=[] #list of the field with the Z data of the previous horizon
V0RasterList=[] #list of raster interpolation for v0 values
KRasterList=[] #list of raster interpolation for k values
TwtRasterList=[] #list of raster interpolation for twt of key horizons
ZRasterList=[] #listo of raster interpolation for z of key horizons
inRasterList=[] #temporary list
inRaster=[] #temporary list
fields=[] #temporary list
logList=[] #list of the log messages
confList=[] #list of config file

#Step 1. Insert the input data	
print "Initializing data"	
#Read input data from config file
l=var.horizons #read number of horizons
datum=var.reference #read reference datum
workspace=var.folder #read workspace folder
env.workspace=workspace

#write input data in config file for script 2
conf="#set the number of steps for the optimization"
confList.append(conf)
conf="steps="
confList.append(conf)
conf="#set the tolerance of the optimization in meters. \n #(e.g. the supposed vertical resolution of the seismic dataset can be used as value of tolerance)"
confList.append(conf)
conf="tolerance="
confList.append(conf)
conf="#Set the list of files with control points \n #The list must contain a file for each horizon \n #The files must be entered from the shallower to the deeper"
confList.append(conf)
conf="CPList=[]"
confList.append(conf)
conf="#Set the fields with depth values"
confList.append(conf)
conf="depthFieldList=[]"
confList.append(conf)
conf="#parameters from script 1"
confList.append(conf)
conf="horizons="+str(l)
confList.append(conf)
conf="reference="+str(datum)
confList.append(conf)
conf="folder=r'"+str(workspace)+"'"
confList.append(conf)
conf="inShpV0KList="+str(inShpV0KList)
confList.append(conf)
conf="inFieldV0List="+str(inFieldV0List)
confList.append(conf)
conf="inFieldKList="+str(inFieldKList)
confList.append(conf)
conf="inShpTwtList="+str(inShpTwtList)
confList.append(conf)
conf="inFieldTwtList="+str(inFieldTwtList)
confList.append(conf)
conf="inShpBarriersList="+str(inShpBarriersList)
confList.append(conf)



#Step 2. this part of the code uses Spatial analyst to interpolate and extract values

#reset iterators
i=1
#initalize the Spatial Analyst extension to be used in the second loop
arcpy.CheckOutExtension("Spatial") 
try:
    while i<=l+1:
        #create a variable (a) containing the index value to call data in the lists
        #value a is always = i-1
        a=i-1
        #create rasters with Inverse Distance Weighted for V0 and k and append raster to the relative lists lists
        inputShp=inShpV0KList[a]
        inputField=inFieldV0List[a]
        inputBarriers=inShpBarriersList[a]
        outname="v0_l"+str(i)
        V0_IDW=arcpy.gp.Idw_sa(inputShp, inputField,outname,"","","",inputBarriers) #create IDW of V0 value
        V0RasterList.append(outname)
        log="V0 data interpolated with IDW for layer "+str(i)
        logList.append(log)
        
        inputShp=inShpV0KList[a]
        inputField=inFieldKList[a]
        inputBarriers=inShpBarriersList[a]
        outname="k_l"+str(i)
        K_IDW=arcpy.gp.Idw_sa(inputShp, inputField,outname,"","","",inputBarriers) #create IDW of K value
        KRasterList.append(outname)
        log="K data interpolated with IDW for layer "+str(i)
        logList.append(log)
        i+=1

    #write velocity rasters in the config file for Script 2
    conf="V0RasterList="+str(V0RasterList)
    confList.append(conf)
    conf="KRasterList="+str(KRasterList)
    confList.append(conf)

    #reset the iterator
    i=1

    #Step 3. this loop extract the values of Tn-1 and Zn-1 for each layer in the velocity model and then calculate the value of Zn
    while i<=l:
        a=i-1
        # Create raster with Topo to Raster for twt data
        inputShp=inShpTwtList[a]
        inputField=inFieldTwtList[a]
        inParameterTTR=inputShp+" "+inputField+" PointElevation"
        outname="twt_ttr"+str(i)
        arcpy.gp.TopoToRaster_sa(inParameterTTR, outname, "", "", "", "", "", "NO_ENFORCE", "SPOT") #create Topo to Raster of Twt value
        TwtRasterList.append(outname)
        log="L"+str(i)+" rasters saved"
        logList.append(log)

        #Step 3.1 Extract the values of Zn-1 and Twtn-1 (the values of Z and T of the upper layer)
            #if the loop is in the first run, create a field with datum that will be use as Z0
        #else create Zn-1 TTR to be used in the successive math for Zn calculation
        if i==1:
            inputShp=inShpTwtList[a]
            outShape="Z_"+inputShp #Create a new file name for depth converted feature class
            inShpZList.append(outShape) #Append the new name to list of depth converted feature classes
            arcpy.Copy_management(inputShp,outShape) #save a file with the input data with the depth converted data file name
            inputShp=outShape #set the copied file as new input for the calculation
            newField="twt0"
            inFieldTwtPrevList.append(newField) #append the Twt0 field to the twt  prev field list, field index is 0
            arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE") #add the Twt0 field to inShpTwt table
            with arcpy.da.UpdateCursor(inputShp,(newField),) as cursor: #the cursor add the value of datum to the Z0 records
                for row in cursor:
                    row[0]=0
            log="T0 data assigned"
            logList.append(log)
            newField="Z0"
            inFieldZPrevList.append(newField) #append the Z0 field to the Z field list, field index is 0
            arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE") #add the Z0 field to inShpTwt table
            with arcpy.da.UpdateCursor(inputShp,(newField),) as cursor: #the cursor add the value of datum to the Z0 records
                for row in cursor:
                    row[0]=datum
            log="Z0 data assigned"
            logList.append(log)
            
        else:
            inputShp=inShpZList[a-1] #from previous layer...
            inputField=inFieldZList[a-1] #...take Zn-1 values...
            inParameterTTR=inputShp+" "+inputField+" PointElevation"
            outname="Z_ttr"+str(i-1) #... set the name of raster output...
            inFieldZPrevList.append(outname) #add field Zn-1 to Z Field list
            arcpy.gp.TopoToRaster_sa(inParameterTTR, outname, "", "", "", "", "", "NO_ENFORCE", "SPOT") #... and interpolate Topo to raster
            ZRasterList.append(outname) #add the raster to Z Raster List
            log="Zn-1 raster for layer "+str(i)+" created with name "+outname
            logList.append(log)
            inputShp=inShpTwtList[a] #set the shape in which Zn will be calculaterd
            outShape="Z_"+inputShp #Create a new file name for depth converted feature class
            inShpZList.append(outShape) #Append the new name to list of depth converted feature classes
            arcpy.Copy_management(inputShp,outShape) #save a file with the input data with the depth converted data file name
            log="Z file for layer "+str(i)+" created with name "+outShape
            logList.append(log)
            inputShp=outShape #set the copied file as new input for the calculation
            inRaster.append(ZRasterList[a-1]) #populate the temporary list...
            inRaster.append(TwtRasterList[a-1]) #... with the raster with Zn-1 and TwTn-1 value
            outnameTwtPrev="twt_ttr"+str(i-1)
            inFieldTwtPrevList.append(outnameTwtPrev)    
            arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRaster) #extract Zn-1 value to shp in which will be calculated the Zn value
            log="Zn-1 and Twtn-1 for layer "+str(i)+ "assigned"
            logList.append(log)
        
            #Step 3.2 This part of the loop calculates the value of Zn (the value of Z of the current layer)
            #extract raster value to points
        inputShp=inShpZList[a]
        inRasterList.append(V0RasterList[a])
        inRasterList.append(KRasterList[a])
        log=inRasterList
        logList.append(log)
        arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList)
        log="v0 and k values for layer "+str(i)+"extracted"
        #add z1 field to be populated with depth values
        newField="Z"+str(i)
        arcpy.AddField_management(inputShp, newField, "FLOAT","","","","","NULLABLE")
        log=newField+ " field added to shp "+ inputShp
        logList.append(log)
        inFieldZList.append(newField)
        #the cursor calculate value in depth
        fields.append(inFieldZPrevList[a]) #Z of the upper layer (Zn-1), index 0
        fields.append(inFieldTwtPrevList[a]) # Twt of the upper layer (Tn-1), index 1
        fields.append(inFieldTwtList[a]) # Twt of the current layer (Tn), index 2
        fields.append(V0RasterList[a]) # V0 of the current layer, index 3 
        fields.append(KRasterList[a]) #K of the current layer, index 4
        fields.append(newField) #Z of the current layer, index 5
        log= fields
        logList.append(log)
        with arcpy.da.UpdateCursor(inputShp, fields) as cursor:
            for row in cursor:
                try:
                    if row[4]==0: #if gradient is 0 the script uses v0 as average velocity
                        Dt=(row[2]-row[1])/2000
                        row[5]=row[0]+row[3]*Dt
                        cursor.updateRow(row)
                        
                    else: #else the script uses the instantanueous velocity equation to depth converte each point
                        Dt=(row[2]-row[1])/2000
                        row[5]=row[0]+row[3]*(math.exp(row[4]*Dt)-1)/row[4]
                        cursor.updateRow(row)
                        
                except:
                    print arcpy.GetMessages()
                    cursor.deleteRow(row)
                    continue
        log="Z values calculated for layer" +str(i)
        logList.append(log)
        #increase the iterator
        #re-initialize temporary lists
        del inRasterList[:]  
        del inRaster[:]
        del fields[:]
        i+=1
        #end of the while loop for interpolation and extraction

    #Step 4. Create the raster layer for the current value of Z (Zn)	
    #create the Z raster of the last layer
    inputShp=inShpZList[l-1] 
    inputField=inFieldZList[l-1] 
    inParameterTTR=inputShp+" "+inputField+" PointElevation"
    outname="Z_ttr"+str(l) #... set the name of raster output...
    inFieldZPrevList.append(outname) #add field Zn-1 to Z Field list
    arcpy.gp.TopoToRaster_sa(inParameterTTR, outname, "", "", "", "", "", "NO_ENFORCE", "SPOT") #... and interpolate Topo to raster
    log="Raster of Z "+str(l)+" created with name "+outname
    ZRasterList.append(outname) #add the raster to Z Raster List
    log=ZRasterList
    logList.append(log)
    log=TwtRasterList
    logList.append(log)
    conf="ZRasterList="+str(ZRasterList)
    confList.append(conf)
    conf="TwtRasterList="+str(TwtRasterList)
    confList.append(conf)
    conf="inShpZList="+str(inShpZList)
    confList.append(conf)
    conf="inFieldZList="+str(inFieldZList)
    confList.append(conf)
    print "velocity model completed completed"
    print "Before running Script 2 please check config2.ini file and add the missing data"
    arcpy.CheckInExtension("Spatial")

except:
    arcpy.CheckInExtension("Spatial") 
    log="something went wrong"
    logList.append(log)
    log=arcpy.GetMessages()
    logList.append(log)

#print the log file and the configuration file for script 2
filename=path+"\\log1.txt"
out_file = open(filename,"w")
for element in logList:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()
filename=path+'\\config2.ini'
out_file=open(filename, "w")
for element in confList:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()

    

