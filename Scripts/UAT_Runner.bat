@echo off
cls
setlocal enabledelayedexpansion

set PLUGIN_PATH="%cd%\YasiuSplineMeshed\YasiuSplineMeshed.uplugin"
echo Plugin Path: %PLUGIN_PATH%

set "EXTRA_PARAMS=-StrictIncludes"

for %%v in (5.0 5.2 5.4 5.5 5.7) do (		
	set "RUNUAT_PATH=P:\UnrealEngines\UE_%%v\Engine\Build\BatchFiles\RunUAT.bat"
		
	echo.
	echo.
	echo ==================== Compiling %%v !EXTRA_PARAMS! ====================
	
	
	echo UAT Path: !RUNUAT_PATH!
	set "PACKAGE_PATH=P:\Unreal Plugins\Build-%%v"
	echo Packing path: !PACKAGE_PATH!
	
	rem This code is removing old folder in windows.
	echo Removing old destination: !PACKAGE_PATH!
	rmdir "!PACKAGE_PATH!" /S /Q
	
	echo.
	call "!RUNUAT_PATH!" BuildPlugin -Plugin=!PLUGIN_PATH! -Package="!PACKAGE_PATH!" -HostPlatforms=Win64 -TargetPlatforms=Win64 !EXTRA_PARAMS!

	
	echo ==================== Finished: %%v !EXTRA_PARAMS! ====================
	echo.
)

pause
