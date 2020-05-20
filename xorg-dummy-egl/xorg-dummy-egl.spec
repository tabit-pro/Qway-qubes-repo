%global upname xf86-video-dummy
%global commit 850c05161d554bbf6360e69294dbec9bc15dd64a
%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/drivers

Summary:   Xorg X11 dummy video driver
Name:      xorg-dummy-egl
Version:   0.3.8
Release:   65%{?dist}
URL:       http://www.x.org
License:   MIT

Source0:   https://gitlab.freedesktop.org/xorg/driver/%{upname}/-/archive/%{commit}/%{upname}-%{commit}.tar.bz2
Source1:   xf86-qubes-common.h
Source2:   xf86-qubes-common.c
Source3:   xorg-qubes.conf.template
Patch0:    xorg-dummy-add-xrandr-support.patch
Patch1:	   xorg-dummy-change-driver-name.patch
Patch2:	   xorg-dummy-glamor-qubes-support.patch

BuildRequires: xorg-x11-server-devel >= 1.4.99.901
BuildRequires: autoconf automake libtool
BuildRequires: xen-devel
BuildRequires: mesa-libgbm-devel
Provides:  qubes-dummy == %{version}-%{release}

%description 
X.Org X11 dummy video driver.

%prep
%setup -q -n %{upname}-%{commit}
cp %{S:1} src
cp %{S:2} src 
cp %{S:3} src 
%patch0 -p1
%patch1 -p1
%patch2 -p1
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
