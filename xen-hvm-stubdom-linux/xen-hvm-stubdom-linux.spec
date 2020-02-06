%define QEMU_VERSION 3.0.0
%define LINUX_VERSION 4.14.68
%define BUSYBOX_VERSION 1.29.3

Name: xen-hvm-stubdom-linux
Version: 1.0.12
Release: 2%{?dist}
Summary: Linux stubdom files for Xen

Group: System
License: GPL
URL: https://www.qubes-os.org/

Requires: xen-libs >= 2001:4.12.0~rc1-0

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
BuildRequires: xen-runtime >= 2001:4.8.2-10
BuildRequires: dracut
BuildRequires: inotify-tools

%if 0%{?fedora} == 25
BuildRequires: gcc-c++ >= 6.4.1-1.qubes1
%endif

Source0: https://github.com/QubesOS/qubes-vmm-xen-stubdom-linux/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1: https://kernel.org/pub/linux/kernel/v4.x/linux-%{LINUX_VERSION}.tar.xz
Source2: https://download.qemu.org/qemu-%{QEMU_VERSION}.tar.xz
Source3: https://busybox.net/downloads/busybox-%{BUSYBOX_VERSION}.tar.bz2
Source4: https://github.com/QubesOS/qubes-gui-agent-xen-hvm-stubdom/archive/v4.1.0.tar.gz

Patch0:	 qemu-stub-xengt-support.patch 


%define debug_package %{nil}

%description
This package contains the files (i.e. kernel and rootfs) for a Linux based
stubdom.


%prep
%setup -q -n qubes-vmm-xen-stubdom-linux-%{version}
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} .
tar -xzvf %{S:4} -C qemu/gui-agent --strip-components=1
make -f Makefile.stubdom build/qemu/.patched
patch -p1 -d build/qemu/ < %{P:0}


%build
make -f Makefile.stubdom %{?_smp_mflags}


%install
make -f Makefile.stubdom DESTDIR=${RPM_BUILD_ROOT} STUBDOM_BINDIR=/usr/libexec/xen/boot install


%files
/usr/libexec/xen/boot/stubdom-linux-rootfs
/usr/libexec/xen/boot/stubdom-linux-kernel


%changelog
