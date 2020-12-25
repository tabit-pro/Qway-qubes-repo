
ARCH=x64
CC=/usr/bin/x86_64-w64-mingw32-gcc
CXX=/usr/bin/x86_64-w64-mingw32-g++
DLLTOOL=/usr/bin/x86_64-w64-mingw32-dlltool
STRIP=/usr/bin/x86_64-w64-mingw32-strip
WINDRES=/usr/bin/x86_64-w64-mingw32-windres
WINDMC=/usr/bin/x86_64-w64-mingw32-windmc
DDKPATH=/usr/x86_64-w64-mingw32/sys-root/mingw/include/ddk
DEBUG=-U_DEBUG -UDBG -UDEBUG

TARGETS=devcon.exe qubes-core-agent-windows \
	qubes-gui-agent-windows qubes-installer-qubes-os-windows-tools
OUTDIR=$(PWD)/bin/$(ARCH)

sources:
	mkdir -p devcon
	svn --force export https://github.com/microsoft/Windows-driver-samples/trunk/setup/devcon && tar -czvf devcon.tar.gz devcon

prep: 
	mkdir -p $(OUTDIR)

clean:
	rm -rf $(ARCH)
	rm -f *.msi

all: prep $(TARGETS)

devcon.exe: qubes-windows-utils
	cd devcon/ && \
	$(WINDMC) msg.mc && \
	$(WINDRES) devcon.rc rc.so && \
	$(CXX) -municode -Wno-write-strings -L $(OUTDIR) -I include -D__MINGW__ -DWIN32_LEAN_AND_MEAN=1 -DUNICODE -D_UNICODE *.cpp rc.so -lsetupapi -lole32 -static-libstdc++ -static-libgcc -static -lpthread -o $(OUTDIR)/$@

qubes-vmm-xen-win-pvdrivers-xeniface: 
	$(CC) $@-*/src/xencontrol/xencontrol.c -I $@-*/include -lsetupapi -I include -DXENCONTROL_EXPORTS -DUNICODE -shared -o $(OUTDIR)/xencontrol.dll
	cp -f $@-*/include/xencontrol.h include
	cp -f $@-*/include/xeniface_ioctls.h include

qubes-vmm-xen-windows-pvdrivers: qubes-vmm-xen-win-pvdrivers-xeniface
	$(CC) $@-*/src/libxenvchan/*.c -std=c11 -fgnu89-inline -D__MINGW__ -D_INC_TCHAR -DNO_SHLWAPI_STRFCNS -DUNICODE -D_UNICODE -mwindows -D_WIN32_WINNT=0x0600 -L $(OUTDIR) -I include -I $@-*/include -lxencontrol -Wl,--no-insert-timestamp -DXENVCHAN_EXPORTS -D_NTOS_ -shared -o $(OUTDIR)/libxenvchan.dll
	cp -f $@-*/include/libxenvchan.h include
	cp -f $@-*/include/libxenvchan_ring.h include

qubes-core-vchan-xen: qubes-vmm-xen-windows-pvdrivers
	cd $@-*/windows && \
	CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include" LDFLAGS="-L $(OUTDIR)" make all
	cp -f $@-*/windows/include/*.h include
	cp -f $@-*/windows/bin/$(ARCH)/* $(OUTDIR)

qubes-windows-utils: qubes-core-vchan-xen
	cd $@-* && \
	CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include" LDFLAGS="-L $(OUTDIR)" make all
	cp -f $@-*/include/*.h include
	cp -f $@-*/bin/$(ARCH)/* $(OUTDIR)

qubes-core-agent-windows: qubes-core-qubesdb
	cd $@-* && \
	DDK_PATH=$(DDKPATH) WINDRES=$(WINDRES) CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include" LDFLAGS="-L $(OUTDIR)" make all
	cp -fr $@-*/bin/$(ARCH)/* $(OUTDIR)
	cp -fr $@-*/bin/$(ARCH)/advertise-tools.exe ./
	cp -fr $@-*/bin/AnyCPU $(PWD)/bin/

qubes-core-qubesdb: qubes-windows-utils
	cd $@-*/windows && \
	CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include" LDFLAGS="-L $(OUTDIR)" make all
	cp -f $@-*/include/*.h include/
	cp -f $@-*/windows/bin/$(ARCH)/* $(OUTDIR)

qubes-installer-qubes-os-windows-tools:
	cd $@-*/ && \
	DDK_PATH=$(DDKPATH) WINDRES=$(WINDRES) CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include" LDFLAGS="-L $(OUTDIR)" make all
	cp -fr $@-*/bin/$(ARCH)/* $(OUTDIR)
	cp $@-*/iso-README.txt ./
	cp $@-*/license.rtf ./
	cp $@-*/qubes-logo.png ./
	cp $@-*/qubes.ico ./
	cp $@-*/power_settings.bat ./

qubes-gui-common:
	cp -f $@-*/include/*.h include

qubes-gui-agent-windows: qubes-gui-common
	cd $@-* && \
	DLLTOOL=$(DLLTOOL) STRIP=$(STRIP) DDK_PATH=$(DDKPATH) WINDRES=$(WINDRES) CC=$(CC) ARCH=$(ARCH) CFLAGS="-I $(PWD)/include -mwindows -U__cplusplus" LDFLAGS="-L $(OUTDIR)" make all
	cp -f $@-*/include/*.h include
	cp -f $@-*/bin/$(ARCH)/* $(OUTDIR)

