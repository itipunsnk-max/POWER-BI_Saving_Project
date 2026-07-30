param(
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$routes = [ordered]@{
    "/" = "index.html"
    "/index.html" = "index.html"
    "/styles.css" = "styles.css"
    "/README.md" = "README.md"
    "/assets/infographic/repair-triage-safe.svg" = "assets/infographic/repair-triage-safe.svg"
    "/docs/01-current-state-assessment.md" = "docs/01-current-state-assessment.md"
    "/docs/02-power-bi-blueprint.md" = "docs/02-power-bi-blueprint.md"
    "/docs/03-cost-reduction-plan.md" = "docs/03-cost-reduction-plan.md"
    "/docs/04-self-maintenance.md" = "docs/04-self-maintenance.md"
    "/docs/05-implementation-runbook.md" = "docs/05-implementation-runbook.md"
    "/docs/06-infographic-backlog.md" = "docs/06-infographic-backlog.md"
    "/powerbi/data-contract.md" = "powerbi/data-contract.md"
    "/powerbi/measures.dax" = "powerbi/measures.dax"
}

$mime = @{
    ".html" = "text/html; charset=utf-8"
    ".css" = "text/css; charset=utf-8"
    ".svg" = "image/svg+xml; charset=utf-8"
    ".md" = "text/markdown; charset=utf-8"
    ".dax" = "text/plain; charset=utf-8"
}

$payload = [ordered]@{}
foreach ($route in $routes.Keys) {
    $relative = $routes[$route]
    $full = Join-Path $ProjectRoot $relative
    if (-not (Test-Path -LiteralPath $full)) {
        throw "Missing source file: $relative"
    }
    $extension = [System.IO.Path]::GetExtension($relative)
    $payload[$route] = [ordered]@{
        body = Get-Content -LiteralPath $full -Raw -Encoding UTF8
        type = $mime[$extension]
    }
}

$json = $payload | ConvertTo-Json -Depth 5 -Compress
$worker = @"
const routes = $json;

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const route = routes[url.pathname];
    if (!route) {
      return new Response("Not found", {
        status: 404,
        headers: { "content-type": "text/plain; charset=utf-8" }
      });
    }
    return new Response(route.body, {
      headers: {
        "content-type": route.type,
        "cache-control": url.pathname === "/" ? "public, max-age=300" : "public, max-age=3600",
        "x-content-type-options": "nosniff"
      }
    });
  }
};
"@

$serverDir = Join-Path $ProjectRoot "dist/server"
New-Item -ItemType Directory -Force -Path $serverDir | Out-Null
$workerPath = Join-Path $serverDir "index.js"
Set-Content -LiteralPath $workerPath -Value $worker -Encoding UTF8
Write-Output $workerPath
