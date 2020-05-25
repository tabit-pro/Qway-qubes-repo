%define QEMU_VERSION 4.2.0
%define LINUX_VERSION 5.4.30
%define BUSYBOX_VERSION 1.31.1
%define PULSEAUDIO_VERSION 13.99.1

Name: xen-hvm-stubdom-linux
Version: 1.0.14
Release: 9%{?dist}
Summary: Linux stubdom files for Xen

Group: System
License: GPL
URL: https://www.qubes-os.org/

Provides: xen-stubdom-gvt

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

# pulseaudio
BuildRequires: gettext-devel
BuildRequires: libtool-ltdl-devel
BuildRequires: libsndfile-devel
BuildRequires: m4

# qemu --audio-drv-list=pa
BuildRequires: pulseaudio-libs-devel

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

Source0: https://github.com/qubesos/qubes-vmm-xen-stubdom-linux/tarball/v1.0.14#/%{name}-%{version}.tar.gz
Source1: https://kernel.org/pub/linux/kernel/v5.x/linux-%{LINUX_VERSION}.tar.xz
Source2: https://download.qemu.org/qemu-%{QEMU_VERSION}.tar.xz
Source3: https://busybox.net/downloads/busybox-%{BUSYBOX_VERSION}.tar.bz2
SOurce4: https://github.com/marmarek/qubes-gui-agent-xen-hvm-stubdom/tarball/qemu-4.2.0#/gui-agent.tar.gz
Source5: http://freedesktop.org/software/pulseaudio/releases/pulseaudio-%{PULSEAUDIO_VERSION}.tar.xz#/pulseaudio.tar.xz
Source20: module-vchan-sink.c

Patch0:	 qemu-stub-xengt-support.patch 
Patch1:  gui-agent-configure-message-acknowledge.patch
Patch2:  pulseaudio-run-system-instance-workaround.patch
Patch3:	 qubes-stubdom-add-pulseaudio.patch

%define debug_package %{nil}

%description
This package contains the files (i.e. kernel and rootfs) for a Linux based
stubdom.


%prep
%setup -n QubesOS-qubes-vmm-xen-stubdom-linux-c48d8ca 
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} .
tar -xf %{S:4} -C qemu/gui-agent --strip-components=1
patch -p1 -d qemu/gui-agent < %{P:1}
make -f Makefile.stubdom build/qemu/.patched
patch -p1 -d build/qemu/ < %{P:0}
tar -xf %{S:5}
cp %{S:20} pulseaudio-%{PULSEAUDIO_VERSION}/src/modules/
patch -p1 -d pulseaudio-%{PULSEAUDIO_VERSION} < %{P:2}

%patch3 -p1

%build
pushd pulseaudio-%{PULSEAUDIO_VERSION}

echo '
# vchan sink module
module_vchan_sink_la_SOURCES = modules/module-vchan-sink.c
module_vchan_sink_la_LDFLAGS = $(MODULE_LDFLAGS) -lvchan-xen 
module_vchan_sink_la_LIBADD = $(MODULE_LIBADD)
module_vchan_sink_la_CFLAGS = $(AM_CFLAGS) -I/usr/include/vchan-xen -DPA_MODULE_NAME=module_vchan_sink

modlibexec_LTLIBRARIES = libprotocol-native.la \
                         module-native-protocol-unix.la \
			 module-vchan-sink.la
bin_PROGRAMS = pulseaudio pacat pactl
lib_LTLIBRARIES = libpulse.la' >> src/Makefile.am

%configure \
  --disable-silent-rules \
  --disable-static \
  --disable-static-bins \
  --disable-rpath \
  --disable-oss-output \
  --disable-coreaudio-output \
  --disable-jack \
  --disable-nls \
  --disable-lirc \
  --disable-tcpwrap \
  --disable-bluez5 \
  --disable-gconf \
  --disable-gsettings \
  --disable-neon-opt \
  --disable-webrtc-aec \
  --disable-systemd-daemon \
  --disable-dbus \
  --disable-gtk3 \
  --disable-alsa \
  --disable-esound \
  --disable-largefile \
  --disable-x11 \
  --disable-oss-wrapper \
  --without-caps \
  --with-database=simple \
  --without-fftw \
  --without-speex \
  --without-soxr \
  --disable-manpages \
  --disable-per-user-esound-socket \
  --disable-gstreamer \
  --disable-systemd-journal \
  --disable-systemd-login \
  --disable-systemd-daemon \
  --disable-openssl \
  --disable-udev \
  --disable-ipv6 \
  --disable-hal-compat \
  --disable-tcpwrap \
  --disable-asyncns \
  --disable-waveout \
  --disable-memfd \
  --disable-tests \
  --disable-glib2 \
  --with-module-dir=/lib \
  --libdir=/lib \
  ac_cv_header_locale_h=no \
  ac_cv_func_strtod_l=no \
  ac_cv_header_langinfo_h=no \
  ac_cv_func_shm_open=no \
  ac_cv_func_fork=no \
  ac_cv_func_getaddrinfo=no \
  ac_cv_func_getuid=no \
  ac_cv_func_seteuid=no \
  ac_cv_func_setresuid=no \
  ac_cv_func_setreuid=no \
  ac_cv_header_pwd_h=no \
  ac_cv_header_grp_h=no


%make_build V=1
mkdir ../dist
%make_install DESTDIR=${PWD}/../dist
strip -s ../dist/lib/*.so* \
	../dist/lib/pulseaudio/*.so* \
	../dist/usr/bin/pulseaudio \
	../dist/usr/bin/pactl \
	../dist/usr/bin/pacat
popd

make -f Makefile.stubdom %{?_smp_mflags}


%install
make -f Makefile.stubdom DESTDIR=${RPM_BUILD_ROOT} STUBDOM_BINDIR=/usr/libexec/xen/boot install


%files
/usr/libexec/xen/boot/stubdom-linux-rootfs
/usr/libexec/xen/boot/stubdom-linux-kernel


%changelog
