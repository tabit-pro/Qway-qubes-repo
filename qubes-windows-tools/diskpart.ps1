if (-not (Get-PSDrive Q) -and (Get-WmiObject Win32_physicalMedia |where {$_.serialnumber -match "QM00002"}))
{
@"
  select disk 1
  clean
  convert gpt
  create partition primary
  format quick fs=ntfs label="Qubes Private Image"
  assign letter="Q"
"@|diskpart
}
