%global    core_plugins    blur clone cube decoration fade ini inotify minimize move place png regex resize rotate scale screenshot switcher water wobbly zoom fs obs commands wall annotate svg matecompat

# List of plugins passed to ./configure.  The order is important

%global    plugins         core,dbus,decoration,fade,minimize,move,obs,place,png,resize,scale,screenshot,svg,switcher,wall

Name:           compiz
License:        GPLv2+ and LGPLv2+ and MIT
Version:        0.8.18
Release:        1%{?dist}
Epoch:          1
Summary:        OpenGL window and compositing manager

URL:            https://gitlab.com/compiz/compiz-core
Source0:        %{url}/-/archive/v%{version}/compiz-core-v%{version}.tar.bz2

Patch0:        0001-force-qubes-decoration.patch
Patch1:        0002-decor-minimal-window.patch
Patch2:        0003-title-center-alignment.patch
Patch3:        0004-force-qubes-vm-name-to-title.patch
Patch4:        0005-allow-stubdom-fullscreen.patch

BuildRequires: libX11-devel
BuildRequires: libdrm-devel
BuildRequires: libXcursor-devel
BuildRequires: libXfixes-devel
BuildRequires: libXrandr-devel
BuildRequires: libXrender-devel
BuildRequires: libXcomposite-devel
BuildRequires: libXdamage-devel
BuildRequires: libXext-devel
BuildRequires: libXt-devel
BuildRequires: libSM-devel
BuildRequires: libICE-devel
BuildRequires: libXmu-devel
BuildRequires: desktop-file-utils
BuildRequires: intltool
BuildRequires: gettext
BuildRequires: librsvg2-devel
BuildRequires: mesa-libGLU-devel
BuildRequires: fuse-devel
BuildRequires: cairo-devel
BuildRequires: libtool
BuildRequires: libjpeg-turbo-devel
BuildRequires: libxslt-devel
#BuildRequires: marco-devel
BuildRequires: glib2-devel
BuildRequires: libwnck3-devel
BuildRequires: dbus-devel
BuildRequires: dbus-glib-devel
BuildRequires: automake

Requires:      glx-utils

Provides:      qubes-compiz-core = %{version}

# obsolete old subpackges
Obsoletes: %{name}-xfce < %{epoch}:%{version}-%{release}
Obsoletes: %{name}-lxde < %{epoch}:%{version}-%{release}
Obsoletes: %{name}-mate < %{epoch}:%{version}-%{release}
%if 0%{?fedora} < 25
Provides:  compiz-mate = %{epoch}:%{version}-%{release}
%endif


%description
Compiz is one of the first OpenGL-accelerated compositing window
managers for the X Window System. The integration allows it to perform
compositing effects in window management, such as a minimization
effect and a cube work space. Compiz is an OpenGL compositing manager
that use Compiz use EXT_texture_from_pixmap OpenGL extension for
binding redirected top-level windows to texture objects.

%package devel
Summary: Development packages for compiz
Requires: %{name}%{?_isa} = %{epoch}:%{version}-%{release}
Requires: pkgconfig
Requires: libXcomposite-devel libXfixes-devel libXdamage-devel libXrandr-devel
Requires: libXinerama-devel libICE-devel libSM-devel libxml2-devel
Requires: libxslt-devel startup-notification-devel

%description devel
The compiz-devel package includes the header files,
and developer docs for the compiz package.
Install compiz-devel if you want to develop plugins for the compiz
windows and compositing manager.

%package qubes
Summary: Metapackage to install compatible compiz bundle on Qubes
Requires: qubes-compiz-core
Requires: qubes-gui-dom0-compiz
Requires: compiz-plugins-main
Requires: compiz-plugins-extra
Requires: ccsm

%description qubes
Metapackage to easily install packages compatible with Qubes.

%prep
%setup -q -n compiz-core-v%{version}

#%patch0 -p1 -b .fedora-logo
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
./autogen.sh
%configure \
    --with-gtk=3.0 \
    --enable-librsvg \
    --enable-gtk \
    --enable-menu-entries \
    --enable-xi2-events \
    --with-default-plugins=%{plugins}
#    --enable-marco \

make %{?_smp_mflags} V=1


%install
%{make_install}

desktop-file-install                              \
    --delete-original                             \
    --dir=%{buildroot}%{_datadir}/applications \
%{buildroot}%{_datadir}/applications/*.desktop

find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

%find_lang %{name}

cat %{name}.lang > core-files.txt

for f in %{core_plugins}; do
  echo %{_libdir}/compiz/lib$f.so
  echo %{_datadir}/compiz/$f.xml
done >> core-files.txt

# placeholder for local icons
mkdir -p %{buildroot}%{_datadir}/compiz/icons/hicolor/{scalable/{apps,\
categories},22x22/{categories,devices,mimetypes}}

%if 0%{?fedora} > 25
%ldconfig_scriptlets
%else
%post -p /sbin/ldconfig
%endif

%postun -p /sbin/ldconfig

%files -f core-files.txt
%doc AUTHORS COPYING.GPL COPYING.LGPL README.md TODO NEWS
%{_bindir}/compiz
%{_bindir}/compiz-decorator
%{_bindir}/gtk-window-decorator
%{_libdir}/libdecoration.so.*
%dir %{_libdir}/compiz
%{_libdir}/compiz/libdbus.so
%{_libdir}/compiz/libglib.so
%dir %{_datadir}/compiz
%{_datadir}/compiz/*.png
%{_datadir}/compiz/icons
%{_datadir}/compiz/core.xml
%{_datadir}/compiz/dbus.xml
%{_datadir}/compiz/glib.xml
%{_datadir}/icons/hicolor/scalable/apps/*.svg
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/applications/compiz.desktop
%{_datadir}/applications/compiz-start.desktop
%{_datadir}/glib-2.0/schemas/org.compiz-0.gwd.gschema.xml

%files devel
%{_libdir}/pkgconfig/compiz.pc
%{_libdir}/pkgconfig/libdecoration.pc
%{_libdir}/pkgconfig/compiz-cube.pc
%{_libdir}/pkgconfig/compiz-scale.pc
%{_includedir}/compiz/
%{_libdir}/libdecoration.so

%files qubes

%changelog
* Fri May 10 2019 Jaroslav Škarvada <jskarvad@redhat.com> - 1:0.8.16.1-1.1
- Rebuilt to fix gtk-window-decorator crash under MATE
  Resolves: rhbz#1708056

* Tue Apr  2 2019 Jaroslav Škarvada <jskarvad@redhat.com> - 1:0.8.16.1-1
- New version
  Resolves: rhbz#1656467
- New URL

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sun Jan 07 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1:0.8.14-4
- Remove obsolete scriptlets

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Apr 20 2017 Wolfgang Ulbrich <fedora@raveit.de> - 1:0.8.14-1
- update to 0.8.14 release
- Handle _NET_WM_MOVERESIZE ClientMessages.
  Fixes the whisker menu resize bug.
- Improve horizontal and vertical maximizing.
- Remove the "Number of Desktops" option.
- Fix a crash when displaying special characters in gtk-window-decorator.
- Set rotate and wall default flip bindings to None.
  Fixes a problem where edges of screen are unclickable by default.
- Fix potential for skydome silently failing to render.
- Don't fallback for exceeding max texture size.
- Improve --button-layout behavior for gtk-window-decorator.
- Update translations.
- video plugin is dropped
- modernize spec file

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.12.3-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sun Nov 20 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.3-5
- enable BR libcompizconfig-devel again

* Sun Nov 20 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.3-4
- disable BR libcompizconfig-devel for rebuilding libcompizconfig
- for libprotobuf soname bump

* Sat Jun 11 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.3-3
- bump version for rebuild with libcompizconfig-devel

* Sat Jun 11 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.3-2
- switch to gtk3

* Tue Apr 12 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.3-1
- update 0.8.12.3 release
- remove ExcludeArch: s390 s390x, they have libdrm now
- remove video from default plugins

* Mon Mar 28 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12.2-1
- update to 0.8.12.2 release

* Sat Feb 13 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.12-1
- update to 0.8.12
- Move mate-window-decorator.py into gtk-window-decorator.
- Add an optional libcompizconfig build dependency that makes it so
- gtk-window-decorator honors ccsm shadow settings and MATE or
- GNOME Flashback cursor theme settings.
- changes with annotate plugin
- Fix Desktop Wall settings of arrow and gradient thumbs colors.
- implement native GSettings lookup for gwd

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:0.8.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.10-3
- fix crash with gwd using close button, rhbz (#1300162, #1298016)

* Sun Dec 20 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.10-2
- fix runtime requires

* Sat Dec 19 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.10-1
- update to 0.8.10 release
- use gtk3 for gwd decorator (mate-window-manager)
- remove old start sripts + desktop files
- use only one menuentry to start compiz
- honor decorator changes in mate-control-center if mate-window-decorator is running
- 'compiz' is now the gsettings key value to start compiz with session start
- drop mate subpackage

* Sun Nov 22 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.9-2
- remove runtime requires fedora-logos, fix rhbz (#1284217)
 
* Fri Nov 06 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.9-1
- update to 0.8.9
- new upstream is at https://github.com/raveit65/compiz
- remove upstreamed patches
- move emerald scripts to emerald
- no xfce/lxde subpackages anymore
- remove runtime requires emerald and hicolors
- use runtime require fedora-logos for the cube plugin
- remove external matecompat logo, it's in the tarball now
- remove mate gwd scripts, they are in the tarball now
- remove old obsoletes for f15/16
- some spec file cleanup
- add desktop-file-install scriptlet
- update build requires
- move gtk-window-decorator to main package
- update configure flags

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Mar 18 2015 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-29
- rebuild for f22

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Feb 16 2014 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-26
- change BR to marco-devel for f21
- rework remove-keybindings-and-mate-windows-settings-files patch
- rework remove-kde patch
- rwork compiz_remove_mateconf_dbus_glib.patch
- rework compiz_remove_old_metacity_checks.patch
- compiz_cube-set-opacity-during-rotation-to-70-as-default.patch
- switch to libwnck for f21

* Thu Aug 15 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-25
- obsolete old compiz versions from f15/f16, rhbz (#997557)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.8.8-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 03 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-23
- fix windows-decorator scripts and desktop files

* Sun May 26 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-22
- add patch to speed up start
- remove --sm-disable --ignore-desktop-hints from start scipts
- fix build for aarch64
- add xfce subpackage again with start script and desktop file
- move matecompat plugin to main package
- add requires hicolor-icon-theme
- add scripts and desktop files for switch the windows-decorator to
- mate subpackage
- remove useless compiz_new_add-cursor-theme-support.patch
- complete removal of gconf
- clean up patches
- rename patches and add more descriptions to spec file
- remove unnecessary desktop-file-validate checks
- update icon-cache scriptlets

* Wed May 08 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-21
- remove compiz-lxde-gtk script and desktop file

* Tue May 07 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-20
- DISABLE XFCE SUPPORT
- remove xfce subpackage
- move gwd decorator to a subpackage

* Mon Apr 29 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-19
- remove compiz-xfce-gtk start script

* Mon Apr 29 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-18
- rename compiz_disable_gtk_disable_deprecated.patch

* Mon Apr 29 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-17
- remove compiz-xfce-gtk.desktop

* Wed Apr 24 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-16
- enable gtk-windows-decorator based on marco (mate-window-manager)
- add compiz_disable_gdk_gtk_disable_deprecated patch
- remove dbus
- remove glib
- remove mateconf
- remove kde
- remove keybindings
- add start scripts for gtk-windows-decorator
- update start scripts for emerald
- add ldconfig scriptlet for mate subpackage
- using libmatewnck instead of libwnck

* Wed Feb 13 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-15
- fix primary-is-control in wall patch

* Sun Feb 10 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-14
- add compiz_primary-is-control.patch
- this will set all default configurations to pimary key
- change compiz-wall.patch for set primary is control key
- fix (#909657)

* Fri Jan 04 2013 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-13
- add require emerald again

* Tue Dec 25 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-12
- remove require emerald until it is in fedora stable

* Sat Dec 22 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-11
- do some major changes
- disable mateconf and use libini text file configuration backend
- remove mateconf from scriptlet section
- move glib annotate svg plugins to core package
- disable gtk-windows-decorator
- drop compiz-mate-gtk compiz session script
- disable gtk-windows-decorator patches
- disable marco/metacity
- disable mate/gnome
- disable mate/gnome keybindings
- insert compiz-mate-emerald compiz session script
- insert compiz-xfce-emerald compiz session script
- insert compiz-lxde-emerald compiz session script
- add emerald as require
- add matecompat icon
- add icon cache scriptlets 


* Sun Dec 02 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-10
- add %%global  plugins_schemas again

* Sun Dec 02 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-9
- revert scriptlet change

* Sun Dec 02 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 1:0.8.8-8
- add %%global  plugins_schemas
- change mateconf scriptlets
- remove (Requires(post): desktop-file-utils)
- add some patches from Jasmine Hassan jasmine.aura@gmail.com
- remove (noreplace) from mateconf schema directory
- add desktop-file-validate
- disable mate keybindings for the moment

* Fri Oct 05 2012 Leigh Scott <leigh123linux@googlemail.com> - 1:0.8.8-7
- remove and obsolete compiz-kconfig schema

* Fri Oct 05 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-6
- remove update update-desktop-database from %%post mate
- remove (noreplace) from mateconf schema dir
- remove Requires(post): desktop-file-utils
- add epoch tags

* Wed Sep 26 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-5
- change compiz-0.88_incorrect-fsf-address.patch

* Wed Sep 26 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-4
- remove upstreamed patches
- own include dir
- add compiz-mate-gtk source and compiz-mate-gtk.desktop file
- add keybinding sources
- change %%define to %%global entries
- rename no-more-gnome-wm-settings.patch to no-more-mate-wm-settings.patch
- add compiz-0.88_incorrect-fsf-address.patch
- clean up build section

* Sun Sep 16 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-3
- add isa tags
- remove kde stuff
- remove obsolete beryl stuff
- add comiz_mate_fork.patch
- remove %%defattr(-, root, root)
- add compiz_gtk_window_decoration_button_placement.patch
- enable some compiz keybindings

* Tue May 15 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-2
- add compiz_mate_fix.patch

* Tue May 15 2012 Wolfgang Ulbrich <chat-to-me@raveit.de> - 0.8.8-1
- build for mate

* Sun May 06 2012 Andrew Wyatt <andrew@fuduntu.org> - 0.8.8-1
- Update to latest stable release

* Tue Nov 30 2010 leigh scott <leigh123linux@googlemail.com> - 0.8.6-6
- add more upstream gdk fixes

