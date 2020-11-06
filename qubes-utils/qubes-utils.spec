Name:		qubes-utils
Version:	4.1.6
Release:	1%{?dist}
Summary:	Common Linux files for Qubes Dom0 and VM
Source0:        https://github.com/QubesOS/qubes-linux-utils/archive/v%{version}.tar.gz
Patch0:		qubes-utils-generate-own-uuid.patch
Patch1:		qubes-utils-identify-by-ids.patch

Group:		Qubes
License:	GPL
URL:		http://www.qubes-os.org

Requires:	udev
Requires:	%{name}-libs
Requires:	ImageMagick
Requires:	python%{python3_pkgversion}-qubesimgconverter
%{?systemd_requires}
BuildRequires:  systemd
BuildRequires:  python2-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python2-rpm-macros
BuildRequires:  python3-rpm-macros
# for meminfo-writer
BuildRequires:  xen-devel
BuildRequires:	gcc

%description
Common Linux files for Qubes Dom0 and VM

%package -n python2-qubesimgconverter
Summary:    Python package qubesimgconverter
Requires:   python2
Requires:   pycairo
%if 0%{?rhel} >= 7
Requires:   python-pillow
Requires:   numpy
%else
Requires:   python2-pillow
Requires:   python2-numpy
%endif

%description -n python2-qubesimgconverter
Python package qubesimgconverter

%package -n python%{python3_pkgversion}-qubesimgconverter
Summary:    Python package qubesimgconverter
Requires:   python%{python3_pkgversion}
Requires:   python%{python3_pkgversion}-cairo
Requires:   python%{python3_pkgversion}-pillow
Requires:   python%{python3_pkgversion}-numpy

%description -n python%{python3_pkgversion}-qubesimgconverter
Python package qubesimgconverter

%package devel
Summary:	Development headers for qubes-utils
Requires:	%{name}-libs

%description devel
Development header and files for qubes-utils

%package libs
Summary: Qubes utils libraries

%description libs
Libraries for qubes-utils

%prep
%setup -q -n qubes-linux-utils-%{version}
%patch0 -p1
%patch1 -p1

%build
export PYTHON=%{__python2}
make all BACKEND_VMM=xen

%install
make install DESTDIR=%{buildroot} PYTHON=%{__python2}
rm -rf imgconverter/build
%make_install -C imgconverter PYTHON=%{__python3}

%post
# dom0
%systemd_post qubes-meminfo-writer-dom0.service
# VM
%systemd_post qubes-meminfo-writer.service

%preun
%systemd_preun qubes-meminfo-writer-dom0.service
%systemd_preun qubes-meminfo-writer.service

%postun
%systemd_postun_with_restart qubes-meminfo-writer-dom0.service
%systemd_postun_with_restart qubes-meminfo-writer.service

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/lib/udev/rules.d/*-qubes-*.rules
/usr/lib/qubes/udev-*
%{_sbindir}/meminfo-writer
%{_unitdir}/qubes-meminfo-writer.service
%{_unitdir}/qubes-meminfo-writer-dom0.service

%files -n python2-qubesimgconverter
%{python2_sitelib}/qubesimgconverter/__init__.py*
%{python2_sitelib}/qubesimgconverter/imggen.py*
%{python2_sitelib}/qubesimgconverter/test.py*
%{python2_sitelib}/qubesimgconverter/test_integ.py*
%{python2_sitelib}/qubesimgconverter-%{version}-py?.?.egg-info

%files -n python%{python3_pkgversion}-qubesimgconverter
%{python3_sitelib}/qubesimgconverter/__init__.py
%{python3_sitelib}/qubesimgconverter/imggen.py
%{python3_sitelib}/qubesimgconverter/test.py
%{python3_sitelib}/qubesimgconverter/test_integ.py
%{python3_sitelib}/qubesimgconverter-%{version}-py?.?.egg-info
%{python3_sitelib}/qubesimgconverter/__pycache__

%files libs
%{_libdir}/libqubes-rpc-filecopy.so.2

%files devel
%defattr(-,root,root,-)
/usr/include/libqubes-rpc-filecopy.h
%{_libdir}/libqubes-rpc-filecopy.so

%changelog
