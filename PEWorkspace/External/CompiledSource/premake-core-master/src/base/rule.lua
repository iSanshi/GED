---
-- base/rule.lua
-- Defines rule sets for generated custom rule files.
-- Copyright (c) 2014 Jason Perkins and the Premake project
---

	local p = premake
	p.rule = p.api.container("rule", p.global)

	local rule = p.rule



---
-- Create a new rule container instance.
---

	function rule.new(name)
		local self = p.container.new(rule, name)

		-- create a variable setting function. Do a version with lowercased
		-- first letter(s) to match Premake's naming style for other calls

		_G[name .. "Vars"] = function(vars)
			rule.setVars(self, vars)
		end

		local lowerName =  name:gsub("^%u+", string.lower)
		_G[lowerName .. "Vars"] = _G[name .. "Vars"]

		return self
	end



---
-- Enumerate the property definitions for a rule.
---

	function rule.eachProperty(self)
		local props = self.propertydefinition
		local i = 0
		return function ()
			i = i + 1
			if i <= #props then
				return props[i]
			end
		end
	end



---
-- Find a property definition by its name.
--
-- @param name
--    The property name.
-- @returns
--    The property definition if found, nil otherwise.
---

	function rule.getProperty(self, name)
		local props = self.propertydefinition
		for i = 1, #props do
			local prop = props[i]
			if prop.name == name then
				return prop
			end
		end
	end



---
-- Find the field definition for one this rule's properties. This field
-- can then be used with the api.* functions to manipulate the property's
-- values in the current configuration scope.
--
-- @param prop
--    The property definition.
-- @return
--    The field definition for the property; this will be created if it
--    does not already exist.
---

	function rule.getPropertyField(self, prop)
		if prop._field then
			return prop._field
		end

		local kind = prop.kind or "string"
		if kind == "list" then
			kind = "list:string"
		end

		local fld = p.field.new {
			name = "_rule_" .. self.name .. "_" .. prop.name,
			scope = "config",
			kind = kind,
			tokens = true,
		}

		prop._field = fld
		return fld
	end



---
-- Given the value for a particular property, returns a formatted string.
--
-- @param prop
--    The property definition.
-- @param value
--    The value of the property to be formatted.
-- @returns
--    A string value.
---

	function rule.getPropertyString(self, prop, value)
		-- list?
		if type(value) == "table" then
			local sep = prop.separator or " "
			return table.concat(value, sep)
		end

		-- enum?
		if prop.values then
			local i = table.indexof(prop.values, value)
			return tostring(i)
		end

		-- primitive
		value = tostring(value)
		if #value > 0 then
			return value
		else
			return nil
		end
	end



---
-- Set one or more rule variables in the current configuration scope.
--
-- @param vars
--    A key-value list of variables to set and their corresponding values.
---

	function rule.setVars(self, vars)
		for key, value in pairs(vars) do
			local prop = rule.getProperty(self, key)
			if not prop then
				error (string.format("rule '%s' does not have property '%s'", self.name, key))
			end

			local fld = rule.getPropertyField(self, prop)
			p.api.storeField(fld, value)
		end
	end
