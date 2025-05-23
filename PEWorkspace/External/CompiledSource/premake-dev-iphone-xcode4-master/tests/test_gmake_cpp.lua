--
-- tests/test_gmake_cpp.lua
-- Automated test suite for GNU Make C/C++ project generation.
-- Copyright (c) 2009 Jason Perkins and the Premake project
--

	T.gmake_cpp = { }

--
-- Configure a solution for testing
--

	local sln, prj
	function T.gmake_cpp.setup()
		_ACTION = "gmake"
		_OPTIONS.os = "linux"

		sln = solution "MySolution"
		configurations { "Debug", "Release" }
		platforms { "Native" }
		
		prj = project "MyProject"
		language "C++"
		kind "ConsoleApp"
		
		solution("MySolution")
	end

	local function prepare()
		premake.bake.buildconfigs()
	end
	


--
-- Test the header
--

	function T.gmake_cpp.BasicHeader()
		prepare()
		premake.gmake_cpp_header(prj, premake.gcc, sln.platforms)
		test.capture [[
# GNU Make project makefile autogenerated by Premake
ifndef config
  config=debug
endif

ifndef verbose
  SILENT = @
endif

ifndef CC
  CC = gcc
endif

ifndef CXX
  CXX = g++
endif

ifndef AR
  AR = ar
endif

ifndef RESCOMP
  ifdef WINDRES
    RESCOMP = $(WINDRES)
  else
    RESCOMP = windres
  endif
endif
		]]
	end
	
	
	
--
-- Test configuration blocks
--

	function T.gmake_cpp.BasicCfgBlock()
		prepare()
		local cfg = premake.getconfig(prj, "Debug")
		premake.gmake_cpp_config(cfg, premake.gcc)
		test.capture [[
ifeq ($(config),debug)
  OBJDIR     = obj/Debug
  TARGETDIR  = .
  TARGET     = $(TARGETDIR)/MyProject
  DEFINES   += 
  INCLUDES  += 
  CPPFLAGS  += -MMD -MP $(DEFINES) $(INCLUDES)
  CFLAGS    += $(CPPFLAGS) $(ARCH) 
  CXXFLAGS  += $(CFLAGS) 
  LDFLAGS   += -s
  RESFLAGS  += $(DEFINES) $(INCLUDES) 
  LIBS      += 
  LDDEPS    += 
  LINKCMD    = $(CXX) -o $(TARGET) $(OBJECTS) $(RESOURCES) $(ARCH) $(LIBS) $(LDFLAGS)
  define PREBUILDCMDS
  endef
  define PRELINKCMDS
  endef
  define POSTBUILDCMDS
  endef
endif
		]]
	end
	

	function T.gmake_cpp.BasicCfgBlockWithPlatformCc()
		platforms { "PS3" }
		prepare()
		local cfg = premake.getconfig(prj, "Debug", "PS3")
		premake.gmake_cpp_config(cfg, premake.gcc)
		test.capture [[
ifeq ($(config),debugps3)
  CC         = ppu-lv2-g++
  CXX        = ppu-lv2-g++
  AR         = ppu-lv2-ar
  OBJDIR     = obj/PS3/Debug
  TARGETDIR  = .
  TARGET     = $(TARGETDIR)/MyProject.elf
  DEFINES   += 
  INCLUDES  += 
  CPPFLAGS  += -MMD -MP $(DEFINES) $(INCLUDES)
  CFLAGS    += $(CPPFLAGS) $(ARCH) 
  CXXFLAGS  += $(CFLAGS) 
  LDFLAGS   += -s
  RESFLAGS  += $(DEFINES) $(INCLUDES) 
  LIBS      += 
  LDDEPS    += 
  LINKCMD    = $(CXX) -o $(TARGET) $(OBJECTS) $(RESOURCES) $(ARCH) $(LIBS) $(LDFLAGS)
  define PREBUILDCMDS
  endef
  define PRELINKCMDS
  endef
  define POSTBUILDCMDS
  endef
endif
		]]
	end


	function T.gmake_cpp.PlatformSpecificBlock()
		platforms { "x64" }
		prepare()
		local cfg = premake.getconfig(prj, "Debug", "x64")
		premake.gmake_cpp_config(cfg, premake.gcc)
		test.capture [[
ifeq ($(config),debug64)
  OBJDIR     = obj/x64/Debug
  TARGETDIR  = .
  TARGET     = $(TARGETDIR)/MyProject
  DEFINES   += 
  INCLUDES  += 
  CPPFLAGS  += -MMD -MP $(DEFINES) $(INCLUDES)
  CFLAGS    += $(CPPFLAGS) $(ARCH) -m64
  CXXFLAGS  += $(CFLAGS) 
  LDFLAGS   += -s -m64 -L/usr/lib64
  RESFLAGS  += $(DEFINES) $(INCLUDES) 
  LIBS      += 
  LDDEPS    += 
  LINKCMD    = $(CXX) -o $(TARGET) $(OBJECTS) $(RESOURCES) $(ARCH) $(LIBS) $(LDFLAGS)
  define PREBUILDCMDS
  endef
  define PRELINKCMDS
  endef
  define POSTBUILDCMDS
  endef
endif
		]]
	end


	function T.gmake_cpp.UniversalStaticLibBlock()
		platforms { "Universal32" }
		project "MyProject"
		kind "StaticLib"
		prepare()
		local cfg = premake.getconfig(prj, "Debug", "Universal32")
		premake.gmake_cpp_config(cfg, premake.gcc)
		test.capture [[
ifeq ($(config),debuguniv32)
  OBJDIR     = obj/Universal32/Debug
  TARGETDIR  = .
  TARGET     = $(TARGETDIR)/libMyProject.a
  DEFINES   += 
  INCLUDES  += 
  CPPFLAGS  +=  $(DEFINES) $(INCLUDES)
  CFLAGS    += $(CPPFLAGS) $(ARCH) -arch i386 -arch ppc
  CXXFLAGS  += $(CFLAGS) 
  LDFLAGS   += -s -arch i386 -arch ppc
  RESFLAGS  += $(DEFINES) $(INCLUDES) 
  LIBS      += 
  LDDEPS    += 
  LINKCMD    = libtool -o $(TARGET) $(OBJECTS)
  define PREBUILDCMDS
  endef
  define PRELINKCMDS
  endef
  define POSTBUILDCMDS
  endef
endif
		]]
	end
