# Downloads Latitude Margaritaville Watersound images for every model
# (full-size gallery photos + floor plan image/PDF), organized by Collection and Model.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # avoids slow progress-bar rendering on large files
$headers = @{ 'User-Agent' = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }
$base = 'https://www.latitudemargaritaville.com'
$root = Join-Path $PSScriptRoot '..\..\downloads\watersound-floor-plans'

$collections = [ordered]@{
  'Conch Collection - Cottages'             = @{ path = '/watersound-conch-cottages-collection'; models = @('bamboo','camellia','dreamsicle','aloha','hula','mango') }
  'Caribbean Collection - Villas'           = @{ path = '/watersound-caribbean-collection';       models = @('jamaica','antigua','lucia','barbuda','barbuda-bay','nevis','tortola') }
  'Beach Collection - Single-Family Homes'  = @{ path = '/watersound-beach-collection';           models = @('coconut','parrot','breeze','breeze-bay','seashell','seashell-bay','cabana-tandem','cabana','cabana-bay-tandem','cabana-bay','escape-bay','escape') }
  'Island Collection - Single-Family Homes' = @{ path = '/watersound-island-collection';          models = @('aruba','st-bart','trinidad','trinidad-bay') }
  'Vista Collection - Single-Family Homes'  = @{ path = '/watersound-vista-collection';           models = @('mainsail','mainsailbay','spinnaker','wayfarer','grand-mainsail','grandmainsailbay','grandspinnaker','grandwayfarer') }
}

function Get-TextInfo { (Get-Culture).TextInfo }
$ti = Get-TextInfo

$summary = @()
foreach ($collName in $collections.Keys) {
  $coll = $collections[$collName]
  foreach ($slug in $coll.models) {
    $url = "$base$($coll.path)/$slug"
    $modelName = $ti.ToTitleCase(($slug -replace '-', ' '))
    $destDir = Join-Path (Join-Path $root $collName) $modelName
    New-Item -ItemType Directory -Force -Path $destDir | Out-Null

    try {
      $html = (Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing).Content
    } catch {
      Write-Warning "Failed to load $url : $_"
      continue
    }

    # Collect every image asset hosted on S3 (busites bucket), excluding UI chrome.
    $all = [regex]::Matches($html, 'https?:(?://|\\/\\/)?[^"''<> ]*busites[^"''<> ]*\.(?:jpg|jpeg|png|gif|pdf)') |
           ForEach-Object { ($_.Value -replace '\\/', '/') } |
           ForEach-Object { if ($_ -match '^//') { 'https:' + $_ } else { $_ } } |
           Where-Object { $_ -notmatch '(?i)logo|minto|housing|equal-housing' } |
           Sort-Object -Unique

    # Floor plans live under pages/meta; gallery photos live under gallery-media.
    $floorPlans = $all | Where-Object { $_ -match '(?i)pages/meta' }
    # Prefer full-size gallery images; drop the "-thumb" variants.
    $gallery    = $all | Where-Object { $_ -match '(?i)gallery-media' -and $_ -notmatch '(?i)-thumb\.' }

    if (-not $floorPlans -and -not $gallery) { Write-Warning "No images found for $modelName ($url)"; continue }

    $count = 0

    # Floor plan image(s) + PDF(s)
    $fpIndex = 0
    foreach ($fileUrl in ($floorPlans | Sort-Object)) {
      $ext = [System.IO.Path]::GetExtension(($fileUrl -split '\?')[0])
      $fpIndex++
      $suffix = if (@($floorPlans).Count -gt 1) { "-$fpIndex" } else { '' }
      $outFile = Join-Path $destDir ("$modelName-floorplan$suffix$ext")
      try {
        Invoke-WebRequest -Uri $fileUrl -Headers $headers -UseBasicParsing -OutFile $outFile
        Write-Host "  saved $outFile"; $count++
      } catch {
        Write-Warning "  failed $fileUrl : $_"
      }
    }

    # Gallery photos (keep their descriptive source filenames)
    $galleryDir = Join-Path $destDir 'gallery'
    if ($gallery) { New-Item -ItemType Directory -Force -Path $galleryDir | Out-Null }
    foreach ($fileUrl in $gallery) {
      $name = [System.IO.Path]::GetFileName(($fileUrl -split '\?')[0])
      $outFile = Join-Path $galleryDir $name
      try {
        Invoke-WebRequest -Uri $fileUrl -Headers $headers -UseBasicParsing -OutFile $outFile
        Write-Host "  saved $outFile"; $count++
      } catch {
        Write-Warning "  failed $fileUrl : $_"
      }
    }

    $summary += [pscustomobject]@{
      Collection  = $collName
      Model       = $modelName
      FloorPlans  = @($floorPlans).Count
      Gallery     = @($gallery).Count
      Files       = $count
    }
  }
}

Write-Host "`n=== Download summary ===" -ForegroundColor Cyan
$summary | Format-Table -AutoSize
Write-Host "Total models: $($summary.Count); Total files: $(($summary | Measure-Object Files -Sum).Sum)"
Write-Host "Output root: $root"
