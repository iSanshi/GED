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
import sys
import math

SAMPLE_FILENAME = "ExportScene02.Fbx"
UKnotVector = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0)
VKnotVector = (0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0)

def CreateScene(pSdkManager, pScene):
    lNurbsNode = CreateNurbs(pSdkManager, "Nurbs")

    MapShapesOnNurbs(pScene, lNurbsNode)
    MapMaterial(pSdkManager, lNurbsNode)
    MapTexture(pSdkManager, lNurbsNode)

    # Build the node tree.
    pScene.GetRootNode().AddChild(lNurbsNode)

    AnimateNurbs(lNurbsNode, pScene)
    return True

def MapShapesOnNurbs(pScene, pNurbs):
    lBlendShape = FbxBlendShape.Create(pScene,"MyBlendShape")
    lBlendShapeChannel01 = FbxBlendShapeChannel.Create(pScene,"MyBlendShapeChannel01")
    lBlendShapeChannel02 = FbxBlendShapeChannel.Create(pScene,"MyBlendShapeChannel02")
    
    #Create and add two target shapes on the lBlendShapeChannel.
    MapStretchedShape(pScene, lBlendShapeChannel01)
    MapBoxShape(pScene, lBlendShapeChannel01)	
    
    MapBoxShape(pScene, lBlendShapeChannel02)	
    
    #Set the lBlendShapeChannel on lBlendShape.
    lBlendShape.AddBlendShapeChannel(lBlendShapeChannel01)
    lBlendShape.AddBlendShapeChannel(lBlendShapeChannel02)
    
    #Set the lBlendShape on pNurbs.
    lGeometry = pNurbs.GetGeometry()
    lGeometry.AddDeformer(lBlendShape)

# Create a sphere.
def CreateNurbs(pSdkManager, pName):
    lNurbs = FbxNurbs.Create(lSdkManager, pName)
    lNurbs.SetOrder(4, 4)
    lNurbs.SetStep(2, 2)
    lNurbs.InitControlPoints(8, FbxNurbs.ePeriodic, 7, FbxNurbs.eOpen)
    lNurbs.SetUKnotVector(list(UKnotVector))
    lNurbs.SetVKnotVector(list(VKnotVector))
    
    lScale = 20.0
    lPi = 3.14159
    lYAngle = (90.0, 90.0, 52.0, 0.0, -52.0, -90.0, -90.0)
    lRadius = (0.0, 0.283, 0.872, 1.226, 0.872, 0.283, 0.0) 

    for i in range(7):
        for j in range(8):
            lX = lScale * lRadius[i] * math.cos(lPi/4*j)
            lY = lScale * math.sin(2*lPi/360*lYAngle[i])
            lZ = lScale * lRadius[i] * math.sin(lPi/4*j)
            lNurbs.SetControlPointAt(FbxVector4(lX, lY, lZ, 1.0), 8*i+j)
            
    # Create Layer 0 where material and texture will be applied
    if not lNurbs.GetLayer(0):
        lNurbs.CreateLayer()
    
    lNurbsNode = FbxNode.Create(lSdkManager, pName)
    lNurbsNode.SetNodeAttribute(lNurbs)
    return lNurbsNode

# Map nurbs control points onto a stretched shape.
def MapStretchedShape(pSdkManager, pBlendShapeChannel):
    lShape = FbxShape.Create(pSdkManager,"")

    lExtremeRight = FbxVector4(-250.0, 0.0, 0.0)
    lExtremeLeft = FbxVector4(250.0, 0.0, 0.0)

    lShape.InitControlPoints(8*7)

    for i in range(7):
        for j in range(8):
            if j < 3 or j > 6:
                lShape.SetControlPointAt(lExtremeLeft, 8*i+j)
            else:
                lShape.SetControlPointAt(lExtremeRight, 8*i+j)

    pBlendShapeChannel.AddTargetShape(lShape)

# Map nurbs control points onto a box shape.
def MapBoxShape(pSdkManager, pBlendShapeChannel):
    lShape = FbxShape.Create(pSdkManager,"")
    lShape.InitControlPoints(8*7)
    
    lScale = 20.0
    lWeight = 1.0
    lX = (0.9, 1.1, 0.0, -1.1, -0.9, -1.1, 0.0, 1.1)
    lZ = (0.0, 1.1, 0.9, 1.1, 0.0, -1.1, -0.9, -1.1)

    # Top control points.
    for i in range(8):
        lShape.SetControlPointAt(FbxVector4(0.0, lScale, 0.0, lWeight), i)

    # Middle control points.
    for i in range(1, 6):
        lY = 1.0 - 0.5 * (i - 1)
        for j in range(8):
            lShape.SetControlPointAt(FbxVector4(lScale*lX[j], lScale*lY, lScale*lZ[j], lWeight), 8*i + j)

    # Bottom control points.
    for i in range(48, 56):
        lShape.SetControlPointAt(FbxVector4(0.0, -lScale, 0.0, lWeight), i)

    pBlendShapeChannel.AddTargetShape(lShape)

# Map texture over sphere.
def MapTexture(pSdkManager, pNurbs):
    lTexture = FbxFileTexture.Create(pSdkManager,"scene02.jpg")

    # The texture won't be displayed if node shading mode isn't set to FbxNode.eTEXTURE_SHADING.
    pNurbs.SetShadingMode(FbxNode.eTextureShading)

    # Set texture properties.
    lTexture.SetFileName("scene02.jpg") # Resource file is in current directory.
    lTexture.SetTextureUse(FbxTexture.eStandard)
    lTexture.SetMappingType(FbxTexture.eCylindrical)
    lTexture.SetMaterialUse(FbxFileTexture.eModelMaterial)
    lTexture.SetSwapUV(False)
    lTexture.SetTranslation(0.45, -0.05)
    lTexture.SetScale(4.0, 1.0)
    lTexture.SetRotation(0.0, 0.0)

    lMaterial = pNurbs.GetSrcObject(FbxSurfacePhong.ClassId, 0)
    if lMaterial:
        lMaterial.Diffuse.ConnectSrcObject(lTexture)

    #now, we can try to map a texture on the AMBIENT channel of a material.

    #It is important to create a NEW texture and not to simply change the
    #properties of lTexture.

    #Set the Texture properties
    lTexture=FbxFileTexture.Create(pSdkManager, "grandient.jpg")
    lTexture.SetFileName("gradient.jpg")
    lTexture.SetTextureUse(FbxTexture.eStandard)
    lTexture.SetMappingType(FbxTexture.eCylindrical)
    lTexture.SetMaterialUse(FbxFileTexture.eModelMaterial)
    lTexture.SetSwapUV(False)

    if lMaterial:
        lMaterial.Ambient.ConnectSrcObject(lTexture)

# Map material over sphere.
def MapMaterial(pSdkManager, pNurbs):
    lMaterial = FbxSurfacePhong.Create(pSdkManager,"scene02")
    lBlue = FbxDouble3(0.0, 0.0, 1.0)
    lBlack = FbxDouble3(0.0, 0.0, 0.0)

    lMaterial.Emissive.Set(lBlue)
    lMaterial.Ambient.Set(lBlack)
    lMaterial.Specular.Set(lBlack)
    lMaterial.TransparencyFactor.Set(0.0)
    lMaterial.Shininess.Set(0.0)
    lMaterial.ReflectionFactor.Set(0.0)
    
    # Create LayerElementMaterial on Layer 0
    lLayerContainer = pNurbs.GetNurbs()
    lLayerElementMaterial = lLayerContainer.GetLayer(0).GetMaterials()

    if  not lLayerElementMaterial:
        lLayerElementMaterial = FbxLayerElementMaterial.Create(lLayerContainer,"")
        lLayerContainer.GetLayer(0).SetMaterials(lLayerElementMaterial)

    # The material is mapped to the whole Nurbs
    lLayerElementMaterial.SetMappingMode(FbxLayerElement.eAllSame)

    # And the material is avalible in the Direct array
    lLayerElementMaterial.SetReferenceMode(FbxLayerElement.eDirect)
    pNurbs.AddMaterial(lMaterial)

# Morph sphere into box shape.
def AnimateNurbs(pNurbs, pScene):
    lTime = FbxTime()
    lKeyIndex = 0

    # First animation stack.
    lAnimStackName = "Morph sphere into box"
    lAnimStack = FbxAnimStack.Create(pScene, lAnimStackName)

    # The animation nodes can only exist on AnimLayers therefore it is mandatory to
    # add at least one AnimLayer to the AnimStack. And for the purpose of this example,
    # one layer is all we need.
    lAnimLayer = FbxAnimLayer.Create(pScene, "Base Layer")
    lAnimStack.AddMember(lAnimLayer)

    lNurbsAttribute = pNurbs.GetNodeAttribute()

    # The stretched shape is at index 0 because it was added first to the nurbs.
    lCurve = lNurbsAttribute.GetShapeChannel(0, 0, lAnimLayer, True)
    if lCurve:
        lTime.SetSecondDouble(0.0)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeyModifyBegin()
        lCurve.KeySetValue(lKeyIndex, 0.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)

        lTime.SetSecondDouble(1.0)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeySetValue(lKeyIndex, 75.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)

        lTime.SetSecondDouble(1.25)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeySetValue(lKeyIndex, 0.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
        lCurve.KeyModifyEnd()

    # The box shape is at index 1 because it was added second to the nurbs.
    lCurve = lNurbsAttribute.GetShapeChannel(0, 1, lAnimLayer, True)
    if lCurve:
        lTime.SetSecondDouble(1.0)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeyModifyBegin()
        lCurve.KeySetValue(lKeyIndex, 0.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)

        lTime.SetSecondDouble(1.25)
        lKeyIndex = lCurve.KeyAdd(lTime)[0]
        lCurve.KeySetValue(lKeyIndex, 100.0)
        lCurve.KeySetInterpolation(lKeyIndex, FbxAnimCurveDef.eInterpolationCubic)
        lCurve.KeyModifyEnd()

if __name__ == "__main__":
    try:
        import FbxCommon
        from fbx import *
    except ImportError:
        import platform
        msg = 'You need to copy the content in compatible subfolder under /lib/python<version> into your python install folder such as '
        if platform.system() == 'Windows' or platform.system() == 'Microsoft':
            msg += '"Python26/Lib/site-packages"'
        elif platform.system() == 'Linux':
            msg += '"/usr/local/lib/python2.6/site-packages"'
        elif platform.system() == 'Darwin':
            msg += '"/Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages"'        
        msg += ' folder.'
        print(msg) 
        sys.exit(1)

    # Prepare the FBX SDK.
    (lSdkManager, lScene) = FbxCommon.InitializeSdkObjects()

    # Create the scene.
    lResult = CreateScene(lSdkManager, lScene)

    if lResult == False:
        print("\n\nAn error occurred while creating the scene...\n")
        lSdkManager.Destroy()
        sys.exit(1)

    # Save the scene.
    # The example can take an output file name as an argument.
    if len(sys.argv) > 1:
        lResult = FbxCommon.SaveScene(lSdkManager, lScene, sys.argv[1])
    # A default output file name is given otherwise.
    else:
        lResult = FbxCommon.SaveScene(lSdkManager, lScene, SAMPLE_FILENAME)

    if lResult == False:
        print("\n\nAn error occurred while saving the scene...\n")
        lSdkManager.Destroy()
        sys.exit(1)

    # Destroy all objects created by the FBX SDK.
    lSdkManager.Destroy()
   
    sys.exit(0)
