"""

 Copyright (C) 2001 - 2010 Autodesk, Inc. and/or its licensors.
 All Rights Reserved.

 The coded instructions, statements, computer programs, and/or related material 
 (collectively the "Data") in these files contain unpublished information 
 proprietary to Autodesk, Inc. and/or its licensors, which is protected by 
 Canada and United States of America federal copyright law and by international 
 treaties. 
 
 The Data may not be disclosed or distributed to third parties, in whole or in
 part, without the prior written consent of Autodesk, Inc. ("Autodesk").

 THE DATA IS PROVIDED "AS IS" AND WITHOUT WARRANTY.
 ALL WARRANTIES ARE EXPRESSLY EXCLUDED AND DISCLAIMED. AUTODESK MAKES NO
 WARRANTY OF ANY KIND WITH RESPECT TO THE DATA, EXPRESS, IMPLIED OR ARISING
 BY CUSTOM OR TRADE USAGE, AND DISCLAIMS ANY IMPLIED WARRANTIES OF TITLE, 
 NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE OR USE. 
 WITHOUT LIMITING THE FOREGOING, AUTODESK DOES NOT WARRANT THAT THE OPERATION
 OF THE DATA WILL BE UNINTERRUPTED OR ERROR FREE. 
 
 IN NO EVENT SHALL AUTODESK, ITS AFFILIATES, PARENT COMPANIES, LICENSORS
 OR SUPPLIERS ("AUTODESK GROUP") BE LIABLE FOR ANY LOSSES, DAMAGES OR EXPENSES
 OF ANY KIND (INCLUDING WITHOUT LIMITATION PUNITIVE OR MULTIPLE DAMAGES OR OTHER
 SPECIAL, DIRECT, INDIRECT, EXEMPLARY, INCIDENTAL, LOSS OF PROFITS, REVENUE
 OR DATA, COST OF COVER OR CONSEQUENTIAL LOSSES OR DAMAGES OF ANY KIND),
 HOWEVER CAUSED, AND REGARDLESS OF THE THEORY OF LIABILITY, WHETHER DERIVED
 FROM CONTRACT, TORT (INCLUDING, BUT NOT LIMITED TO, NEGLIGENCE), OR OTHERWISE,
 ARISING OUT OF OR RELATING TO THE DATA OR ITS USE OR ANY OTHER PERFORMANCE,
 WHETHER OR NOT AUTODESK HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH LOSS
 OR DAMAGE. 
 
"""

from DisplayCommon import *
from fbx import FbxGlobalLightSettings
from fbx import FbxGlobalCameraSettings, FbxSystemUnit

def DisplayGlobalLightSettings(pScene):
    lGlobalLightSettings = pScene.GlobalLightSettings()
    DisplayColor("Ambient Color: ", lGlobalLightSettings.GetAmbientColor())
    DisplayBool("Fog Enabled: ", lGlobalLightSettings.GetFogEnable())
    DisplayColor("Fog Color: ", lGlobalLightSettings.GetFogColor())
    
    lFogMode = lGlobalLightSettings.GetFogMode()
    
    if(lFogMode == FbxGlobalLightSettings.eLinear):
        DisplayString("Fog Mode: Linear")
    elif(lFogMode == FbxGlobalLightSettings.eExponential):
        DisplayString("Fog Mode: Exponential")
    elif(lFogMode == FbxGlobalLightSettings.eExponentialSquareRoot):
        DisplayString("Fog Mode: Exponential Square Root")
    else:
        DisplayString("Fog Mode: UNKNOWN")
        
    DisplayDouble("Fog Density: ", lGlobalLightSettings.GetFogDensity())
    DisplayDouble("Fog Start: ", lGlobalLightSettings.GetFogStart())
    DisplayDouble("Fog End: ", lGlobalLightSettings.GetFogEnd())
        
    DisplayBool("Shadow Enabled: ", lGlobalLightSettings.GetShadowEnable())
    DisplayDouble("Fog Density: ", lGlobalLightSettings.GetShadowIntensity())
    DisplayInt("Shadow Planes Count: ", lGlobalLightSettings.GetShadowPlaneCount())
    
    DisplayString("")



def DisplayGlobalCameraSettings(pScene):
    lGlobalSettings = pScene.GetGlobalSettings()
    DisplayString("Default Camera: ", lGlobalSettings.GetDefaultCamera().Buffer())
    DisplayString("")

def DisplaySystemUnit(systemUnit):
    print "      Conversion factor to meter: %f" % (systemUnit.GetConversionFactorTo(FbxSystemUnit.m))
    
def DisplayGlobalTimeSettings(pGlobalSettings, peParserCtx):
    lTimeModes = [ "Default Mode", "Cinema", "PAL", "Frames 30", 
        "NTSC Drop Frame", "Frames 50", "Frames 60",
        "Frames 100", "Frames 120", "NTSC Full Frame", 
        "Frames 30 Drop", "Frames 1000" ] 

    DisplayString("Time Mode: ", lTimeModes[pGlobalSettings.GetTimeMode()])

    lTs = pGlobalSettings.GetTimelineDefaultTimeSpan()
    lStart = lTs.GetStart()
    lEnd   = lTs.GetStop()
    DisplayString("Timeline default timespan: ")
    lTmpStr=""
    DisplayString("     Start: ", lStart.GetTimeString(lTmpStr))
    DisplayString("     Stop : ", lEnd.GetTimeString(lTmpStr))

    DisplayString("     Original Unit System: ")
    DisplaySystemUnit(pGlobalSettings.GetOriginalSystemUnit())
    
    #so far this is the only place where I see a conversion scale value  that will make the meshes stored in FBX file
    #to be converted properly to meters. That is when we export fbx and we say we want meters, it still exports mesh verts as cm
    #but the original sytem unti conversio to 1m is 0.01 so we use that as our conversion factor
    #this could not be 100% correct and maybe will change with future fxb exporters. But for now this is the only place
    #I found 0.01 factor in the file
    convFactor = pGlobalSettings.GetOriginalSystemUnit().GetConversionFactorTo(FbxSystemUnit.m)
    peParserCtx.logger.AddLine("Setting conversion factor to %f" % (convFactor,))
    peParserCtx.conversionFactor = convFactor
    
    DisplayString("     Current Unit System: ")
    DisplaySystemUnit(pGlobalSettings.GetSystemUnit())
    
    #print "SystemUnit dir()"
    #print dir(pGlobalSettings.GetSystemUnit())
    
    DisplayString("")
    
