# esp32-idf activation for conda-based ESP-IDF (no IDF venv)
$idf_path = "E:\ESP-IDF\.espressif\v5.4.4\esp-idf"
$idf_tools = "E:\ESP-IDF\.espressif\tools"
$env:IDF_PATH = $idf_path
$env:IDF_TOOLS_PATH = "E:\ESP-IDF\.espressif"
$env:IDF_PYTHON_ENV_PATH = "E:\ESP-IDF\.espressif\python_env\idf5.4_py3.13_env"
$env:ESP_IDF_VERSION = "5.4.4"

$tool_dirs = @(
    "$idf_tools\idf-exe\1.0.3",
    "$idf_path\tools",
    "$idf_tools\cmake\3.30.2\bin",
    "$idf_tools\ninja\1.12.1",
    "$idf_tools\xtensa-esp-elf\esp-14.2.0_20260121\xtensa-esp-elf\bin"
)

foreach ($dir in $tool_dirs) {
    if (Test-Path $dir) {
        $env:PATH = "$dir;$env:PATH"
    }
}

Write-Output "ESP-IDF $((python $idf_path/tools/idf.py --version 2>&1) -match 'v\d+\.\d+\.\d+$') activated (conda base)"
Write-Output "IDF_PATH: $env:IDF_PATH"
