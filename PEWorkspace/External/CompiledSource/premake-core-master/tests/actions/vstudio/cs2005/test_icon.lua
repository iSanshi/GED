--
-- tests/actions/vstudio/cs2005/test_icon.lua
-- Validate generation of the application icon declaration.
-- Copyright (c) 2013 Jason Perkins and the Premake project
--

	local suite = test.declare("vstudio_cs2005_icon")
	local cs2005 = premake.vstudio.cs2005


--
-- Setup
--

	local wks

	function suite.setup()
		wks, prj = test.createWorkspace()
	end

	local function prepare()
		prj = test.getproject(wks, 1)
		cs2005.applicationIcon(prj)
	end


--
-- By default, there should be no output.
--

	function suite.noOutput_onNoIcon()
		prepare()
		test.isemptycapture()
	end


--
-- If an icon is specified, output the property group.
--

	function suite.doesOutput_onIcon()
		icon "MyApp.ico"
		prepare()
		test.capture [[
	<PropertyGroup>
		<ApplicationIcon>MyApp.ico</ApplicationIcon>
	</PropertyGroup>
		]]
	end
