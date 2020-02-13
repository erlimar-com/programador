#requires -version 2

<#
.SYNOPSIS
Atualiza os arquivos de distribuição disponibilizados pelo site.

.DESCRIPTION
Basicamente copia o que está em cli/dist/ProgramadorCLI-*.tar.gz
para servidor/programador_servidor/static/download/*
#>

Set-StrictMode -Version 2

$originFile1 = Join-Path $PSScriptRoot "../cli/dist/ProgramadorCLI-0.1.tar.gz"
$originFile2 = Join-Path $PSScriptRoot "../servidor/dist/ProgramadorServidor-0.1.tar.gz"
$destFolder = Join-Path $PSScriptRoot "../servidor/programador_servidor/static/download/"

if (!(test-path $destFolder)) {
    New-Item -ItemType Directory  -Path $destFolder
}

Copy-Item $originFile1 $destFolder
Copy-Item $originFile2 $destFolder

