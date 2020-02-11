#requires -version 2

<#
.SYNOPSIS
Atualiza os arquivos de distribuição disponibilizados pelo site.

.DESCRIPTION
Basicamente copia o que está em cli/dist/ProgramadorCLI-*.tar.gz
para servidor/programador_servidor/static/download/*
#>

Set-StrictMode -Version 2

$originFile = Join-Path $PSScriptRoot "../cli/dist/ProgramadorCLI-0.1.tar.gz"
$destFolder = Join-Path $PSScriptRoot "../servidor/programador_servidor/static/download"
$destFile = "programador-0.1.tar.gz"

if (!(test-path $destFolder)) {
    New-Item -ItemType Directory  -Path $destFolder
}

Copy-Item $originFile (Join-Path $destFolder $destFile)
