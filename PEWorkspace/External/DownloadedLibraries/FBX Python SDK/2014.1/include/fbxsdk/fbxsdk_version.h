/****************************************************************************************
 
   Copyright (C) 2013 Autodesk, Inc.
   All rights reserved.
 
   Use of this software is subject to the terms of the Autodesk license agreement
   provided at the time of installation or download, or which otherwise accompanies
   this software in either electronic or hard copy form.
 
****************************************************************************************/

/** \file fbxsdk_version.h
  * FBX SDK version definition.
  *
  * This file defines the version string and numbers for this release of the FBX SDK.
  * \note This file should never be included directly, please include fbxsdk_def.h
  * instead.
  */
#ifndef _FBXSDK_VERSION_H_
#define _FBXSDK_VERSION_H_

//FBX SDK version defines
#define FBXSDK_VERSION_MAJOR	2014		//<! Integer, version major number
#define FBXSDK_VERSION_MINOR	1			//<! Integer, version minor number
#define FBXSDK_VERSION_POINT	0			//<! Integer, version point number
#define FBXSDK_VERSION_NAME		"Release"	//<! String, version name, example: Alpha, Beta, RC, Release

#define FBXSDK_VERSION_YEAR     2013		//<! Integer, release date year
#define FBXSDK_VERSION_MONTH	04			//<! Integer, release date month
#define FBXSDK_VERSION_DAY		02			//<! Integer, release date day

#ifndef FBXSDK_VERSION_REVISION
	#define FBXSDK_VERSION_REVISION	0		//<! Integer, version revision number, set by build environment. Do not edit here!
#endif

//FBX SDK version string macros
#define FBXSDK_DEF_TO_STR(x)	#x
#define FBXSDK_STRINGIFY(x)		FBXSDK_DEF_TO_STR(x)

#if FBXSDK_VERSION_POINT == 0
	#define FBXSDK_VER_TO_STR(a, b, c)	FBXSDK_DEF_TO_STR(a.b)
#else
	#define FBXSDK_VER_TO_STR(a, b, c)	FBXSDK_DEF_TO_STR(a.b.c)
#endif

//FBX SDK version strings
#define FBXSDK_VERSION_STRING		FBXSDK_VER_TO_STR(FBXSDK_VERSION_MAJOR, FBXSDK_VERSION_MINOR, FBXSDK_VERSION_POINT)
#define FBXSDK_VERSION_STRING_FULL	FBXSDK_VERSION_STRING" "FBXSDK_VERSION_NAME" ("FBXSDK_STRINGIFY(FBXSDK_VERSION_REVISION)")"
#define FBXSDK_VERSION_DATE			FBXSDK_STRINGIFY(FBXSDK_VERSION_YEAR)""FBXSDK_STRINGIFY(FBXSDK_VERSION_MONTH)""FBXSDK_STRINGIFY(FBXSDK_VERSION_DAY)

//FBX SDK namespace definition
#ifndef FBXSDK_DEFINE_NAMESPACE
	#define FBXSDK_DEFINE_NAMESPACE 1
#endif

#if FBXSDK_DEFINE_NAMESPACE == 1
	#define FBXSDK_NAMESPACE fbxsdk_2014_1
#else
	#define FBXSDK_NAMESPACE
#endif

#endif /* _FBXSDK_VERSION_H_ */
