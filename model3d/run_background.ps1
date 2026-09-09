param(
    [string]$Blender = 'D:\Users\11171344\blender\blender.exe',
    [ValidateSet('Build','Verify','All','Render')][string]$Mode = 'All',
    [string]$Camera = '01_Axonometric'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Blender)) { throw "Blender not found: $Blender" }
$commonArgs = @('--background','--factory-startup','--disable-autoexec','--python-exit-code','1')
function Invoke-BlenderTask([string]$Script, [string[]]$ExtraArgs = @()) {
    & $Blender @commonArgs --python (Join-Path $PSScriptRoot $Script) -- @ExtraArgs
    if ($LASTEXITCODE -ne 0) { throw "Blender $Script failed with exit code $LASTEXITCODE" }
}
if ($Mode -in @('Build','All')) { Invoke-BlenderTask 'build_scene.py' }
if ($Mode -in @('Verify','All')) { Invoke-BlenderTask 'verify_scene.py' }
if ($Mode -eq 'Render') { Invoke-BlenderTask 'render_scene.py' @('--camera',$Camera) }
exit 0
