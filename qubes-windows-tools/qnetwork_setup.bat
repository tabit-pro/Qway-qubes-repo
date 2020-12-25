
for /f "USEBACKQ" %%i in (`wmic nic where "Name like 'Xen%%'" get interfaceindex ^|findstr /b /r [0-9]`) do set QINDEX=%%i

for /f "delims=" %%i in ('qubesdb-cmd.exe -c read /qubes-ip') do set QIP=%%i

for /f "delims=" %%i in ('qubesdb-cmd.exe -c read /qubes-netmask') do set QMASK=%%i

for /f "delims=" %%i in ('qubesdb-cmd.exe -c read /qubes-gateway') do set QGATE=%%i

for /f "delims=" %%i in ('qubesdb-cmd.exe -c read /qubes-primary-dns') do set QPRIDNS=%%i

for /f "delims=" %%i in ('qubesdb-cmd.exe -c read /qubes-secondary-dns') do set QSECDNS=%%

netsh int ipv4 set address name=%QINDEX% static %QIP% %QMASK% %QGATE%

netsh int ipv4 set dnsservers name=%QINDEX% static %QPRIDNS%

netsh int ipv4 add dnsservers name=%QINDEX% static %SECDNS%"
