--
-- tests/actions/vstudio/vc2010/test_header.lua
-- Validate generation of the project file header block.
-- Copyright (c) 2011-2012 Jason Perkins and the Premake project
--

	local suite = test.declare("vstudio_vc2010_header")
	local vc2010 = premake.vstudio.vc2010


--
-- If a default build target is specified, it should be included in the
-- generated Project element.
--

	function suite.project_on2010()
		premake.action.set("vs2010")
		vc2010.project()
		test.capture [[
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
		]]
	end

	function suite.project_on2011()
		premake.action.set("vs2012")
		vc2010.project()
		test.capture [[
<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
		]]
	end

	function suite.project_on2013()
		premake.action.set("vs2013")
		vc2010.project()
		test.capture [[
<Project DefaultTargets="Build" ToolsVersion="12.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
		]]
	end
