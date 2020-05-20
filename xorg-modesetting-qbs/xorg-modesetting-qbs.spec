%global moduledir %(pkg-config xorg-server --variable=moduledir )
%global driverdir %{moduledir}/drivers

Summary:    Xorg X11 modesetting video driver for Qubes
Name:	    xorg-modesetting-qbs
Version:    1.20.6 
Release:    3%{?dist}
URL:	    http://www.x.org
License:    MIT

Source0:    https://gitlab.freedesktop.org/xorg/xserver/-/archive/xorg-server-%{version}/xserver-xorg-server-%{version}.tar.gz?path=hw/xfree86/drivers/modesetting#/modesetting-%{version}.tar.gz

Source1:    xf86-qubes-common.h
Source2:    xf86-qubes-common.c
Source3:    xorg-qubes.conf.template
Source4:    configure.ac
Source5:    Makefile.am

Patch0:	    xorg-modesetting-add-qubes-shm-support.patch

BuildRequires: xorg-x11-server-devel
BuildRequires: autoconf automake libtool
BuildRequires: xen-devel
BuildRequires: mesa-libgbm-devel

%description 
Xorg X11 modesetting video driver for Qubes

%prep
%setup -q -n xserver-xorg-server-%{version}-hw-xfree86-drivers-modesetting/hw/xfree86/drivers/modesetting/
cp %{S:1} %{S:2} %{S:3} %{S:4} %{S:5} .
%patch0 -p1

autoreconf -vif

%build
%configure
%make_build

%install
%make_install
mkdir -p %{buildroot}/%{_sysconfdir}/X11/

install -m 0644 -D xorg-qubes.conf.template \
                %{buildroot}%{_sysconfdir}/X11/xorg-modesetting-qbs.conf.template

# FIXME: Remove all libtool archives (*.la) from modules directory.  This
# should be fixed in upstream Makefile.am or whatever.
find $RPM_BUILD_ROOT -regex ".*\.la$" | xargs rm -f --

%files
%{driverdir}/*.so
%{_sysconfdir}/X11/*.conf.template

%changelog
