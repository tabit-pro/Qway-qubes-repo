%define QEMU_VERSION 4.2.0
%define LINUX_VERSION 5.4.30
%define BUSYBOX_VERSION 1.31.1
%define PULSEAUDIO_VERSION 13.99.1

Name: xen-hvm-stubdom-linux
Version: 1.1.0
Epoch:   2
Release: 5%{?dist}
Summary: Linux stubdom files for Xen
Provides: xen-hvm-stubdom-gvt

Group: System
License: GPL
URL: https://www.qubes-os.org/

Provides: xen-stubdom-gvt

Requires: xen-libs >= 2002:4.14.0

BuildRequires: quilt

# QEMU
BuildRequires: python
BuildRequires: zlib-devel
BuildRequires: xen-devel
BuildRequires: glib2-devel
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: edk2-tools
BuildRequires: libtool
BuildRequires: libseccomp-devel
BuildRequires: pixman-devel

# pulseaudio
BuildRequires: gettext-devel
BuildRequires: libtool-ltdl-devel
BuildRequires: libsndfile-devel
BuildRequires: m4

# QEMU Qubes gui-agent
BuildRequires: qubes-gui-common-devel
BuildRequires: qubes-libvchan-xen-devel

# Linux
BuildRequires: bc
BuildRequires: bison
BuildRequires: flex
# gcc with support for BTI mitigation
%if 0%{?fedora} == 25
BuildRequires: gcc >= 6.4.1-1.qubes1
%endif
BuildRequires: gcc-plugin-devel
BuildRequires: gcc-c++

# Busybox
BuildRequires: libselinux-devel >= 1.27.7-2
BuildRequires: libsepol-devel

# rootfs
BuildRequires: xen-runtime >= 2002:4.8.2-10
BuildRequires: dracut
BuildRequires: inotify-tools

%if 0%{?fedora} == 25
BuildRequires: gcc-c++ >= 6.4.1-1.qubes1
%endif

Source0: https://github.com/qubesos/qubes-vmm-xen-stubdom-linux/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1: https://kernel.org/pub/linux/kernel/v5.x/linux-%{LINUX_VERSION}.tar.xz
Source2: https://download.qemu.org/qemu-%{QEMU_VERSION}.tar.xz
Source3: https://busybox.net/downloads/busybox-%{BUSYBOX_VERSION}.tar.bz2
Source4: https://freedesktop.org/software/pulseaudio/releases/pulseaudio-%{PULSEAUDIO_VERSION}.tar.xz
Source5: https://github.com/QubesOS/qubes-gui-agent-xen-hvm-stubdom/archive/mm_91eac617.tar.gz#/qemu-gui-agent.tar.gz
Source6: https://github.com/QubesOS/qubes-gui-agent-linux/archive/mm_391160eb.tar.gz#/pulseaudio-gui-agent.tar.gz

Patch0:	 qemu-stub-xengt-support.patch 
Patch1:  gui-agent-configure-message-acknowledge.patch

%define debug_package %{nil}

%description
This package contains the files (i.e. kernel and rootfs) for a Linux based
stubdom.

%prep
%setup -n qubes-vmm-xen-stubdom-linux-%{version}
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} .
tar -xf %{S:5} -C qemu/gui-agent --strip-components=1
cp %{P:0} qemu/patches/
echo $(basename %{P:0}) >> qemu/patches/series
patch -p1 -d qemu/gui-agent < %{P:1}
tar -xf %{S:6} -C pulseaudio/gui-agent --strip-components=1

%build
make -f Makefile.stubdom %{?_smp_mflags}


%install
make -f Makefile.stubdom DESTDIR=${RPM_BUILD_ROOT} STUBDOM_BINDIR=/usr/libexec/xen/boot install


%files
/usr/libexec/xen/boot/qemu-stubdom-linux-rootfs
/usr/libexec/xen/boot/qemu-stubdom-linux-kernel


%changelog
