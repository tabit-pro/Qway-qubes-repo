# qwt-crossbuild
Qubes Windows Tools crossbuild project

In comparison with the original ITL's Qubes Tools qwt-crossbuild contains several in-progress improvements:

- [x] rebuild QWT utils (mingw, x86, x86\_64) (QI#5065)
- [x] include updated xen pv drivers (8.2.2)
- [x] prepare reproducible/deterministic build (binaries only)
- [x] hide command prompt windows during setup execution (WixQuiteExec)
- [x] sign and install drivers without prompt (libwdi-based pkihelper utility)
- [x] avoid high cpu consumption (move qga CreateEvent outside an event processing loop) (QI#3418)
- [x] use dhcp instead of network setup service
- [x] stop disabling audio services while R4.1 have audio support for HVM 
- [x] disable Windows recovery console with preparation script
- [x] remove format dialog (diskpart instead of prepare-volume) (QI#5090, QI#5768)
- [x] support Qubes-r4.1 (qrexec v2 backward compatibility)
- [x] fix qvideo early restart error (QI#5864)
- [x] fix qvideo incorrect destroy procedure (possibly fixes BSOD 0x50)
- [x] fix installer relocate-dir fails on Windows 10 due to special reparse points (QI#5093)
- [x] fix halting DispVM right after start (QI#4369)


## QWT Runtime prerequisuites

1. Fully/partially updated Windows 7/10
1. Testsigning mode on
1. Backup

## Feature status
| Feature | Windows 7 x64 (en,ru)| Windows 10 x64 (en,ru) |
| --- | :---: | :---: |
| Qubes Video Driver (Seamless mode) | + | - |
| Private Volume Setup (move profiles)  | + | + |
| File sender/receiver | + | + |
| Clipboard Copy/Paste | + | + |
| Application shortcuts | + | + |
| Copy/Edit in Disposable VM | + | + |
| Audio support (requires R4.1)| + | + |
