%global         basever 0.8.16

Name:           libcompizconfig
Version:        0.8.18
Release:        1%{?dist}
Epoch:          1
Summary:        Configuration back end for compiz
# backends/libini.so is GPLv2+, other parts are LGPLv2+
License:        LGPLv2+ and GPLv2+
URL:            https://gitlab.com/compiz/%{name}
Source0:        %{url}/-/archive/v%{version}/%{name}-v%{version}.tar.bz2

BuildRequires:  gcc-c++
BuildRequires:  compiz-devel >= %{basever}
BuildRequires:  compiz-bcop >= %{basever}
BuildRequires:  libX11-devel
BuildRequires:  gettext
BuildRequires:  intltool
BuildRequires:  perl(XML::Parser)
BuildRequires:  mesa-libGL-devel
BuildRequires:  protobuf-devel
BuildRequires:  libtool
BuildRequires:  automake

Requires:       compiz >= %{basever}


%description
The Compiz Project brings 3D desktop visual effects that improve
usability of the X Window System and provide increased productivity
through plugins and themes contributed by the community giving a
rich desktop experience.

This package contains the library for plugins to configure compiz 
settings.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires:       compiz-devel >= %{version}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q -n %{name}-v%{version}

%build
./autogen.sh
%configure --disable-static

sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
           
make %{?_smp_mflags} V=1

%install
%{make_install}
find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'


%ldconfig_scriptlets


%files
%doc AUTHORS COPYING NEWS
%config(noreplace) %{_sysconfdir}/compizconfig/
%{_libdir}/*.so.*
%{_datadir}/compiz/ccp.xml
%{_libdir}/compiz/*.so
%dir %{_libdir}/compizconfig/
%dir %{_libdir}/compizconfig/backends/
%{_libdir}/compizconfig/backends/libini.so

%files devel
%{_includedir}/compizconfig/
%{_libdir}/*.so
%{_libdir}/pkgconfig/libcompizconfig.pc


%changelog
* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Tue Apr  2 2019 Jaroslav Škarvada <jskarvad@redhat.com> - 1:0.8.16-1
- New version
  Related: rhbz#1656467
- New URL

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 13 2017 Orion Poplawski <orion@cora.nwra.com> - 1:0.8.14-2
- Rebuild for protobuf 3.3.1

* Thu Apr 20 2017 Wolfgang Ulbrich <fedora@raveit.de> - 1:0.8.14-1
- update to 0.8.14 release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.12.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jan 26 2017 Orion Poplawski <orion@cora.nwra.com> - 1:0.8.12.1-3
- Rebuild for protobuf 3.2.0

* Sat Nov 19 2016 Orion Poplawski <orion@cora.nwra.com> - 1:0.8.12.1-2
- Rebuild for protobuf 3.1.0

* Tue Apr 12 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.1-1
- update to 0.8.12.1 release
- remove ExcludeArch: s390 s390x, they have libdrm now

* Sat Feb 13 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12-1
- update to 0.8.12 release

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Nov 06 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.9-1
- update to 0.8.9
- new upstream is at https://github.com/raveit65/libcompizconfig
- removed upstreamed patches
- add requires compiz base version
- use modern make install macro

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Apr 24 2015 Leigh Scott <leigh123linux@googlemail.com> - 1:0.8.8-13
- rebuild for new protobuf .so

* Wed Mar 18 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-12
- rebuild for f22

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Apr 24 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-8
- rework mate patch

* Sun Mar 10 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-7
- rebuild for protobuf ABI change to 8 for rawhide

* Sun Feb 10 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-6
- add libcompizconfig_primary-is-control.patch
- fix (#909657)

* Sat Dec 08 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-5
- change default backend for mate-session
- with libcompizconfig_default_backend_for_mate-session.patch

* Sat Dec 08 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-4
- fix incoherent-version-in-changelog
- remove requires pkgconfig
- fix mixed-use-of-spaces-and-tabs

* Sun Dec 02 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-3
- add patch from Jasmine Hassan jasmine.aura@gmail.com
- fix binary-or-shlib-defines-rpath
- initial build for fedora
- add epoch

* Tue May 15 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-2
- add libcompizconfig_mate.patch

* Tue May 15 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-1
- build for mate

