%global upname xf86-video-dummy
%global commit 850c05161d554bbf6360e69294dbec9bc15dd64a
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/drivers
%global qbscommon v4.1.5

Summary:   Xorg X11 dummy video driver
Name:      xorg-dummy-egl
Version:   0.3.8
Release:   62%{?dist}
URL:       http://www.x.org
License:   MIT

Source0:   https://gitlab.freedesktop.org/xorg/driver/%{upname}/-/archive/%{commit}/%{upname}-%{commit}.tar.bz2
Source1:   https://raw.githubusercontent.com/QubesOS/qubes-gui-agent-linux/%{qbscommon}/xf86-qubes-common/include/xf86-qubes-common.h
Source2:   https://raw.githubusercontent.com/QubesOS/qubes-gui-agent-linux/%{qbscommon}/xf86-qubes-common/xf86-qubes-common.c
Source3:   https://raw.githubusercontent.com/QubesOS/qubes-gui-agent-linux/%{qbscommon}/appvm-scripts/etc/X11/xorg-qubes.conf.template
Patch0:    xorg-dummy-add-xrandr-support.patch
Patch1:	   xorg-dummy-change-driver-name.patch
Patch2:    xorg-dummy-qubes-gui-share-pixmaps.patch
Patch3:    xorg-dummy-glamor.patch
Patch4:	   xorg-dummy-qubes-template-add-glamor.patch
#TODO
#%%Patch5:    xorg-dummy-vblank-dri2-support.patch

BuildRequires: xorg-x11-server-devel >= 1.4.99.901
BuildRequires: autoconf automake libtool
BuildRequires: xen-devel
BuildRequires: mesa-libgbm-devel
Provides:  qubes-dummy == %{version}-%{release}

%description 
X.Org X11 dummy video driver.

%prep
%setup -q -n %{upname}-%{commit}
mkdir -p src/include
cp %{S:1} src/include
cp %{S:2} src/ 
cp %{S:3} src/ 
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
#%%patch5 -p1
autoreconf -vif

%build
%configure --disable-static
%make_build

%install
%make_install
mkdir -p %{buildroot}/%{_sysconfdir}/X11/

install -m 0644 -D src/xorg-qubes.conf.template \
                %{buildroot}%{_sysconfdir}/X11/xorg-qubes-egl.conf.template

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -regex ".*\.la$" | xargs rm -f --

%files
%{driverdir}/dummyegl_drv.so
%{_sysconfdir}/X11/xorg-qubes-egl.conf.template

%changelog
