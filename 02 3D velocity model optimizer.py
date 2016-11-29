#v.1.1 this script optimize an existing velocity model

import math
import itertools
import arcpy
from arcpy import env
from arcpy.sa import *
arcpy.env.overwriteOutput=True

#Step 1 import configuration file
import sys, os
path=os.path.dirname(os.path.abspath(sys.argv[0]))
import imp
filename=path+'\\config2.ini'
f=open(filename)
var=imp.load_source('var','',f)
f.close()

#set the lists that will be used
#initialize the lists of variables
tolerance=var.tolerance #set the value of tolerance for the optimization
warnings=0 #set the number of warnings
inShpV0KList=var.inShpV0KList #list of the files with the V0 and k information
inShpTwtList=var.inShpTwtList #list of the files with the twt data for each key horizon
inShpZList=var.inShpZList #list of the depth converted files
inShpBarriersList=var.inShpBarriersList #list of the files with the barriers features
CPList=var.CPList #list of control point
CPListXY=[] #control points with XY coordinates
horizonFieldList=[] #field with name horizon of control point
depthFieldList=var.depthFieldList #field with depth value of control point
horizonNameList=[] #name of the horizons
HnameList=[] #temporary list for horizon name
outShpList=[] #list of the putput shapefiles
stdevV0List=[] #list of standard deviation value of v0 for each layer
stdevKList=[] #list of standard deviation value of k for each layer
v_values=[]#store the value of v0 within the standard deviation interval
k_values=[]#store the value of k within the standard deviation interval
vtemp_values=[] #list of all the values of v
ktemp_values=[] # list of all the values of k
z_values=[] # temporary store the values of z
delta_values=[] #temporary store the residual delta values
logList=[] #list of log for output results
confList=[] #list of configuration for script 3
outIter=[]

inFieldV0List=var.inFieldV0List #list of the field name with V0 information
inFieldKList=var.inFieldKList #list of the field name with k information
inFieldTwtList=var.inFieldTwtList #list of the field name with twt information for each key horizon
inFieldZList=var.inFieldZList #list of the field name with Z information
inFieldTwtPrevList=[] #list of the field with the twt data of the previous horizon
inFieldZPrevList=[] #list of the field with the Z data of the previous horizon

V0RasterList=var.V0RasterList #list of raster interpolation for v0 values
KRasterList=var.KRasterList #list of raster interpolation for k values
TwtRasterList=var.TwtRasterList #list of raster interpolation for twt of key horizons
ZRasterList=var.ZRasterList #list of raster interpolation for z of key horizons
inRasterList=[] #temporary list
inRaster=[] #temporary list
fields=[] #temporary list
insertFields=[] #temporary list
V0RasterOptList=[] #list of v0 raster optimized
KRasterOptList=[] #list of k raster optimized
ZRasterOptList=[] #list of Z raster optimized

#define functions
#define the function to calculate standard deviation
def stdev (intable,infield,stdevList):
    sum1=0
    sum2=0
    nrow=0
    with arcpy.da.SearchCursor(intable, infield) as cursor:
        for row in cursor:
            sum1+=row[0]
            sum2+=row[0]*row[0]
            nrow+=1
    argument=nrow*sum2-(sum1*sum1)
    std=math.sqrt(argument)/nrow
    stdevList.append(std)
    return stdevList

#Step 1 Insert the Input data
#Step 1.1. Insert the input data of the velocity model built with Script 1 
#set the number of key horizons and the workspace folder
print "Initializing data"
l=var.horizons
#set the datum
datum=var.reference
#set the steps for optimization
steps=var.steps
#set the workspace
workspace=var.folder
env.workspace=workspace

#write input data in config file for script 3
conf="#Insert the file with points to depth convert"
confList.append(conf)
conf="pointData="
confList.append(conf)
conf="#Set the field with travel time data values"
confList.append(conf)
conf="pointTwtField="
confList.append(conf)
conf="#Set the field with object names"
confList.append(conf)
conf="obNameField="
confList.append(conf)
conf="#parameters from script 2"
confList.append(conf)
conf="horizons="+str(l)
confList.append(conf)
conf="reference="+str(datum)
confList.append(conf)
conf="folder=r'"+str(workspace)+"'"
confList.append(conf)

#Step 2 Calulate the standard deviation of V and k
#calculate the standard deviation for v and k
i=1
while i<=l:
    a=i-1
    SD_V=stdev(inShpV0KList[a],inFieldV0List[a],stdevV0List)
    SD_K=stdev(inShpV0KList[a],inFieldKList[a],stdevKList)
    log="stardard deviation of v0 for layer "+str(i)+ " is: "+str(stdevV0List[a])
    logList.append(log)
    log="stardard deviation of k for layer "+str(i)+ " is: "+str(stdevKList[a])
    logList.append(log)
    i+=1
#finished standard deviation calculation

#Step 3 run the optimization 

i=1

arcpy.CheckOutExtension("Spatial")
while i<=l:
    #Step 3.1 Copy the data in a new file and assign the field with the Depth value with index 0
    a=i-1
    outshp="Copy"+CPList[a]
    arcpy.Copy_management(CPList[a],outshp)
    arcpy.AddXY_management(outshp)
    inputShp=outshp
    log="Layer "+str(i)+" log"
    logList.append(log)
    log="file "+ outshp+ " created"
    fields.append(depthFieldList[a]) #this field contain the depth information of control point and will have index 0
    
    #Step 3.2 Assign Tn-1 and Zn-1 value
    #start an if/else to assign the twt n-1 and Z n-1 value
    if i==1:
        #assign 0 to z-1 and twtn-1

        FieldT0="twt_ttr0"
        #add to the field list
        #this will have index 1
        fields.append(FieldT0)
        arcpy.AddField_management(inputShp, FieldT0, "FLOAT","","","","","NULLABLE") #add the Twt0 field to table
        with arcpy.da.UpdateCursor(inputShp,(FieldT0),) as cursor: #the cursor add the value of datum to the Z0 records
            for row in cursor:
                row[0]=0
                cursor.updateRow(row)
        FieldZ0="Z_ttr0"
        #add to the field list
        #this will have index 2
        fields.append(FieldZ0)
        arcpy.AddField_management(inputShp, FieldZ0, "FLOAT","","","","","NULLABLE") #add the Z0 field to table
        with arcpy.da.UpdateCursor(inputShp,(FieldZ0),) as cursor: #the cursor add the value of datum to the Z0 records
            for row in cursor:
                row[0]=0
                cursor.updateRow(row)
        
    elif i!=1:
        #extract multi value to point

        inRaster.append(TwtRasterList[a-1])
        inRaster.append(ZRasterList[a-1])
        #this for loop will add tn-1 and zn-1 to the fields list with index respectively 1 and 2
        for field in inRaster:
            fields.append(field)
        #the tn-1 and zn-1 value are extracted to the control point shape   
        arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRaster) #extract Tn_1 Zn-1 value to shp in which will be calculated the Zn value

    #Step 3.3 extract the data of V, k, T and Z from the velocity model 
    inRasterList=[V0RasterList[a],KRasterList[a],TwtRasterList[a],ZRasterList[a]]
    arcpy.sa.ExtractMultiValuesToPoints(inputShp,inRasterList)
    newField="Delta"
    arcpy.AddField_management(inputShp, newField,"FLOAT","","","","","NULLABLE")
    for element in inRasterList: #populate the list of fields with v0, k, twtn, zn fields with index respectively 3, 4, 5, 6
        fields.append(element)
    #add fields for Delta calculation with index 7
    fields.append(newField)
    print fields
    with arcpy.da.UpdateCursor(inputShp, fields) as cursor:
        for row in cursor:
            row[7]=row[0]-row[6]
            cursor.updateRow(row)
            #Step 3.4 Calculate all possible values of v and k using the standard deviation and the steps assigned for the analysis
    #populate the lists with all possible value of v and k
    incremV=stdevV0List[a]/steps
    incremK=stdevKList[a]/steps
    Vbest="V_best" #index 8
    arcpy.AddField_management(inputShp, Vbest,"FLOAT","","","","","NULLABLE")
    fields.append(Vbest)
    Kbest="k_best" #index 9
    arcpy.AddField_management(inputShp, Kbest,"FLOAT","","","","","NULLABLE")
    fields.append(Kbest)
    Zbest="Z_best" #index 10
    arcpy.AddField_management(inputShp, Zbest,"FLOAT","","","","","NULLABLE")
    fields.append(Zbest)
    resD="res_D" #index 11
    arcpy.AddField_management(inputShp, resD,"FLOAT","","","","","NULLABLE")
    fields.append(resD)
    fields.append("POINT_X") #index 12
    fields.append("POINT_Y") #index 13
    Check="Check"
    arcpy.AddField_management(inputShp, Check,"TEXT","","","2","","NON_NULLABLE")
    fields.append(Check) #index 14
    #copy VK shapfile in a new outfile
    outShpVK="optVK_"+str(i)+".shp"
    arcpy.Copy_management(inShpV0KList[a],outShpVK)
    #copy the out z file in a new output file
    outShpZ="optZ_"+str(i)+".shp"
    arcpy.Copy_management(inShpZList[a],outShpZ)
    log="the file with optimized Z values of Layer "+str(i)+ " is: "+outShpZ
    logList.append(log)
    # the cursor calculate all the values of v and k within the standard deviation based on the steps of iterations
    # add append the values to lists
    rowcount=1
    with arcpy.da.UpdateCursor(inputShp,fields) as cursor:
        for row in cursor:
            iterator=1
            while iterator<=steps:
                v=row[3]+incremV*iterator
                v_values.append(v)
                v=row[3]-incremV*iterator
                v_values.append(v)
                k=row[4]+incremK*iterator
                k_values.append(k)
                k=row[4]-incremK*iterator
                k_values.append(k)
                iterator+=1

            #Step 3.5 Iterate all possible combination of v and k to calculate the Z value with the minimum deviation from control point
            combList=itertools.product(v_values,k_values) #iterate through all the v and k values
            for v,k in combList:
                vtemp_values.append(v)
                ktemp_values.append(k)
                Dt=(row[5]-row[1])/2000
                z=row[2]+v*(math.exp(k*Dt)-1)/k #calculate the z values for all the possible combination of v and k
                resdelta=math.fabs(z-row[0])
                iterout=str(i)+","+str(v)+","+str(k)+","+str(z)+","+str(resdelta)
                outIter.append(iterout)
                z_values.append(z) #append all possible z value to a list
                delta_values.append(math.fabs(z-row[0])) #calculate the residual delta with the marker of control point
            log= "Z values from all combination of v and k for row "+str(rowcount)+" in Layer "+str(i)+" created"
            logList.append(log)
            minimum=min(delta_values) #find the minimum of residual delta
            log="minimum value of residual difference between calculated and measure Z in row "+str(rowcount)+ " is "+str(minimum)
            logList.append(log)
            if minimum<tolerance:
                row[14]="OK"
            else:
                row[14]="NO"
                warnings+=1
                        
            minIndex=delta_values.index(min(delta_values)) #find the index of the minumum residual delta
            log="the minimum value in row "+str(rowcount)+" was found for iteration with index: " + str(minIndex)
            logList.append(log)
            row[10]=z_values[minIndex] #find the z value with minimum delta and add to out table
            log="best z value found from optimization of row "+str(rowcount)+ " is: "+str(z_values[minIndex])
            logList.append(log)
            inZ=outShpZ
            insertFields.append(inFieldZList[a])
            X=row[12]
            Y=row[13]
            insertFields.append("SHAPE@XY")
            with arcpy.da.InsertCursor(inZ,insertFields) as inCursor: #insert a new record in the  z shapefile
                inCursor.insertRow((z_values[minIndex],(float(X),float(Y))))
            log="new point added to "+inZ+" shapefile"
            logList.append(log)
            #resert insertFields list to be used in next steps
            del insertFields[:]

            row[11]=minimum #add the minimum delta to the out table
            log="the residual difference for row "+str(rowcount)+ " is: "+str(row[11]) 
            logList.append(log)
            row[8]=vtemp_values[minIndex] #add the v0 value used to obtain the minimum delta to out table
            log="best v0 value for row "+str(rowcount)+" is: "+str(vtemp_values[minIndex])
            logList.append(log)
            inVK=outShpVK
            insertFields.append(inFieldV0List[a])
            row[9]=ktemp_values[minIndex] #add the k value used to obtaion the minimum delta to out table
            log="best k value for row "+str(rowcount)+" is: "+str(ktemp_values[minIndex])
            logList.append(log)
            insertFields.append(inFieldKList[a])
            X=row[12]
            Y=row[13]
            insertFields.append("SHAPE@XY")
            
            #Step 3.6 add the control point values of v and k as new data in the velocity shapefile 
            #add point features with v and k values to vk optimized shapefile
            with arcpy.da.InsertCursor(inVK,insertFields) as inCursor: #insert a new record in the  v and k shapefile
                inCursor.insertRow((vtemp_values[minIndex],ktemp_values[minIndex],(float(X),float(Y))))
            log="new point added to "+inVK+" shapefile"
            logList.append(log)

            cursor.updateRow(row)
            #reset lists used in each row
            del v_values[:]
            del k_values[:]
            del z_values[:]
            del delta_values[:]
            del vtemp_values[:]
            del ktemp_values[:]
            del insertFields[:]
            rowcount+=1
    
    #Step 4 interpolate the new rasters for the velocity model after optimization 
    inputShp=outShpVK
    inputField=inFieldV0List[a]
    inputBarriers=inShpBarriersList[a]
    outname="optv0l"+str(i)
    V0_IDW=arcpy.gp.Idw_sa(inputShp, inputField,outname,"","","",inputBarriers) #create IDW of V0 optimized values
    V0RasterOptList.append(outname)
    log="output raster for v0 is "+outname
    logList.append(log)
    inputShp=outShpVK
    inputField=inFieldKList[a]
    inputBarriers=inShpBarriersList[a]
    outname="optkl"+str(i)
    K_IDW=arcpy.gp.Idw_sa(inputShp, inputField,outname,"","","",inputBarriers) #create IDW of V0 optimized values
    KRasterOptList.append(outname)
    log="output raster for k is "+outname
    logList.append(log)
    inputShp=outShpZ 
    inputField=inFieldZList[a] 
    inParameterTTR=inputShp+" "+inputField+" PointElevation"
    outname="optZ_"+str(i) #... set the name of raster output...
    arcpy.gp.TopoToRaster_sa(inParameterTTR, outname, "", "", "", "", "", "NO_ENFORCE", "SPOT") #... and interpolate Topo to raster
    ZRasterOptList.append(outname)
    log="output raster for Z is "+outname
    logList.append(log)
    #reset lists used in each loop
    del fields[:]
    del inRaster[:]
    del inRasterList[:]
    #increase the loop iterator
    i+=1

deepVraster=V0RasterList[l]
V0RasterOptList.append(deepVraster)
deepKraster=KRasterList[l]
KRasterOptList.append(deepKraster)
arcpy.CheckInExtension("Spatial")
conf="V0RasterList="+str(V0RasterOptList)
confList.append(conf)
conf="KRasterList="+str(KRasterOptList)
confList.append(conf)
conf="ZRasterList="+str(ZRasterOptList)
confList.append(conf)
conf="TwtRasterList="+str(TwtRasterList)
confList.append(conf)

print "optimization completed"
print "Warnings detected: "+str(warnings)
print "Before running Script 3 please check config3.ini file and add the missing data"
filename=path+"\\log2.txt"
out_file = open(filename,"w")
for element in logList:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()
filename=path+'\\config3.ini'
out_file=open(filename, "w")
for element in confList:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()
filename=path+'\\vkiter.txt'
out_file=open(filename, "w")
for element in outIter:
    text=str(element)
    out_file.write(text)
    out_file.write("\n")
out_file.close()


