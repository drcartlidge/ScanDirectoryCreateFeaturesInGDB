#!/usr/bin/env python3  Line 1
# -*- coding: utf-8 -*- Line 2
#----------------------------------------------------------------------------
# Created By  : Matthew Cartlidge, PhD, GISP
# Created Date: 10-14-21
# version ='1.0'
# ---------------------------------------------------------------------------
""" Purpose: Script scans a directory in which reports are generated routinely, then creates GIS feature classes
in a geodatabase using arcpy for only features not previously created. An accompanying batch file
allows this script to run at scheduled times routinely.""" 

# Usefill links to gain contextual information related to scrip's functionality
# (1) https://desktop.arcgis.com/en/arcmap/10.6/tools/samples-toolbox/create-features-from-text-file.htm
# (2) https://community.esri.com/t5/python-questions/python-create-polylines-with-attributes/td-p/586581

import arcpy
import os

# Set workspace. 
arcpy.env.workspace = "C:/Users/Matthew Cartlidge/Google Drive/SNHU/IT_338_Geospatial_Programming/" \
                      "Assignments/Final_Project/Final_Project_ArcGIS_Workspace/Final_Project_ArcGIS_Workspace.gdb"
workspace = "C:/Users/Matthew Cartlidge/Google Drive/SNHU/IT_338_Geospatial_Programming/" \
                      "Assignments/Final_Project/Final_Project_ArcGIS_Workspace/Final_Project_ArcGIS_Workspace.gdb"

# Turn on overwriting of outputs
arcpy.env.overwriteOutput = True

# Create empty feature class in which polylines from .txt file will be stored
# Leverage the 'if exists' condition below to skip over 'CreateFeatureclass' method and 'AddField', if feature class already created
if arcpy.Exists("Gas_Lines"):
    pass
else:
    arcpy.management.CreateFeatureclass(workspace, "Gas_Lines", "POLYLINE", spatial_reference =
    "C:/Users/Matthew Cartlidge/Google Drive/SNHU/IT_338_Geospatial_Programming/Assignments/" \ 
    "Final_Project/data/final_project_data/final_project_data/Gas_Lines.prj")
    # Add field to table
    arcpy.management.AddField("Gas_Lines", "Name", "TEXT")
    arcpy.management.AddField("Gas_Lines", "Date", "TEXT")
    arcpy.management.AddField("Gas_Lines", "PSI", "TEXT")
    arcpy.management.AddField("Gas_Lines", "Material", "TEXT")

# List feature classes in workspace
print(arcpy.ListFeatureClasses())

# Define object for feature class
fc = "Gas_Lines"

unique_values = []
# Employ search cursor to identify unique set of values in the 'Date' field, as they will mean
# that the corresponding text will have already be used to create features
with arcpy.da.SearchCursor(fc, ["Date"]) as cursor:
    values = [row[0] for row in cursor]
    unique_values = set(values)
    print(unique_values)

# add .txt to dates in the feature class's 'Date' field
completed_list = []
for i in unique_values:
    completed_list.append(i + ".txt")
print(completed_list)
print("line 58 completed")

available_reports = []
directory = r'C:\Users\Matthew Cartlidge\Google Drive\SNHU\IT_338_Geospatial_Programming\Assignments\Final_Project\data\final_project_data\final_project_data\Cartlidge_Corrected_Data'
for entry in os.scandir(directory):
    if (entry.path.endswith(".txt")
            or entry.path.endswith(".txt")) and entry.is_file():
        available_reports.append(entry.name)
        print(available_reports)
        print("line 67 completed")

# create a list of keys and a lookup list
update_data = []  # list in which file paths for data to be run in model
for key in available_reports:
    for i in completed_list:
        if key == i:
            print("Data from " + str(key) + " is already updated in geodatabase.")
            break
    else:
        print("Data from " + str(key) + " needs to be updated in geodatabase.")
        update_data.append(r'C:\Users\Matthew Cartlidge\Google Drive\SNHU\IT_338_Geospatial_Programming\Assignments\Final_Project\data\final_project_data\final_project_data\Cartlidge_Corrected_Data' + '\\' + key)

print("Following are directory paths and file names of reports to be updated in GDB when rest of script runs")
print(update_data)

# Loop through file paths of reports for which features have not already been created in the geodatabase.
for report in update_data:
# The text file contains lines with data as Name, X, Y with one entry per row.
    infile = open(report, mode = 'r')

    # Extract file name of text file containing coordinates and data for later inclusion in the processed data text file
    from pathlib import Path
    dataset = Path(str(infile))

    # add coordinate data from text file into a nested list
    coords_list = [line.split() for line in infile]
    print(coords_list)

    spatial_reference = arcpy.Describe("Gas_Lines_Provided").spatialReference

    # Employ insert cursor to insert coordinates in feature class.
    cursor = arcpy.da.InsertCursor(fc, ["SHAPE@", "Name", "Date", "PSI", "Material"])
    print(cursor.fields)  # fields to which cursor has been given access
    array = arcpy.Array()  # This creates a place to store all the coordinates for a line before we create  it.

    # Below inspired by example at https://pro.arcgis.com/en/pro-app/latest/arcpy/get-started/writing-geometries.htm.

    ID = -1
    for coords in coords_list:
        if ID == -1:
            ID = coords[0]

        # Store attribute data in Python object for record being read by cursor so that it can be added to
        # the feature created when ID counter used for iteration doesn't match
        # the ID in column 0, thus signifying the end of a feature and simultaneously
        # triggering the creation of the feature using cursor.insertRow.
        if ID == coords[0]:
            Name = coords[1] # coords[1] references the attribute data location to be inserted when the row is created.
            Date = coords[5]
            PSI = coords[6]
            Material = coords[7]
        # Add the point to the feature's array of points
        # If the ID has changed, create a new feature
        if ID != coords[0]:
            cursor.insertRow([arcpy.Polyline(array), Name, Date, PSI, Material])
            array.removeAll()
        array.add(arcpy.Point(coords[2], coords[3], ID=coords[0]))
        ID = coords[0]

    # Add the last feature
    polyline = arcpy.Polyline(array, spatial_reference)
    cursor.insertRow([polyline, Name, Date, PSI, Material])
    del cursor