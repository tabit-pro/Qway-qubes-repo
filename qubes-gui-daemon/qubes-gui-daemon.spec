#
# This is the SPEC file for creating binary and source RPMs for the Dom0.
#
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2010  Joanna Rutkowska <joanna@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#


#removed %{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		qubes-gui-daemon	
Version:	4.1.6
Release:	6%{dist}
Summary:	The Qubes GUI virtualization (Dom0 side) 

Group:		Qubes
Vendor:		Invisible Things Lab
License:	GPL
URL:		http://www.qubes-os.org

Requires:	xorg-x11-server-Xorg 
Requires:	service(graphical-login)
Requires:	libconfig
Requires:	qubes-libvchan-xen
Requires:   python%{python3_pkgversion}-xcffib
Requires:   qubes-core-qrexec >= 4.1.5
Requires:   qubes-utils >= 4.1.4
Requires:   socat

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:	pulseaudio-libs-devel
BuildRequires:	libXt-devel
BuildRequires:	libXext-devel
BuildRequires:	libXrandr-devel
BuildRequires:	libconfig-devel
BuildRequires:	libpng-devel
BuildRequires:	libnotify-devel
BuildRequires:	xen-devel
BuildRequires:	qubes-db-devel
BuildRequires:	help2man
BuildRequires:	gcc
BuildRequires:	qubes-core-libs-devel >= 1.6.1
BuildRequires:	qubes-core-libs
BuildRequires:	qubes-gui-common-devel >= 3.2.0
BuildRequires:	qubes-libvchan-xen-devel

Provides:     qubes-gui-dom0-compiz

Source0: https://github.com/QubesOS/qubes-gui-daemon/archive/v%{version}.tar.gz
Patch1: 0002-event-configure.patch
Patch2: 0003-fullscreen-stubdomain-window.patch

%description
The Qubes GUI virtualization infrastructure that needs to be installed in GuiVM.

%package -n qubes-gui-dom0
Summary:    Dom0 part of Qubes GUI
# For now require also gui-daemon in dom0, when dropping GUI in dom0, this
# dependency should be dropped
Requires:   qubes-gui-daemon
# Pull also audio packages for easier upgrade
Requires:   qubes-audio-daemon
Requires:   qubes-audio-dom0
Requires:   qubes-core-dom0 >= 4.1.1
Requires:   python%{python3_pkgversion}-setuptools


%description -n qubes-gui-dom0
Dom0 files for Qubes GUI virtualization. This include core-admin extension,
policy files etc.

%package -n qubes-audio-daemon
Summary:    The Qubes AUDIO virtualization
Requires:   pulseaudio-libs
Requires:   pulseaudio
Requires:   libconfig
Requires:   qubes-libvchan-xen
Requires:   qubes-utils >= 3.1.0
Requires:   python%{python3_pkgversion}-pydbus
 
%description -n qubes-audio-daemon
The Qubes AUDIO virtualization infrastructure that needs to be installed in AudioVM.

%package -n qubes-audio-dom0
Summary:    Dom0 part of Qubes AUDIO
Requires:   qubes-core-dom0 >= 1.3.14
Requires:   python%{python3_pkgversion}-setuptools

%description -n qubes-audio-dom0
Dom0 files for Qubes AUDIO virtualization. This include core-admin extension, policy files etc.

%prep
#removed %setup -q -n qubes-gui-daemon-%{version}
%setup -q 
%patch1 -p1
%patch2 -p1

%build
%{?set_build_flags}
make clean
make all BACKEND_VMM=xen

%py3_build

%pre

%install
rm -rf $RPM_BUILD_ROOT
%make_install
%py3_install

%triggerin -- xorg-x11-server-Xorg
ln -sf /usr/bin/X-wrapper-qubes /usr/bin/X

%postun
if [ "$1" = 0 ] ; then
	# no more packages left
    ln -sf /usr/bin/Xorg /usr/bin/X
fi

%clean
rm -rf $RPM_BUILD_ROOT
rm -f %{name}-%{version}

%files
%defattr(-,root,root,-)
%attr(4750,root,qubes) /usr/bin/qubes-guid
%{_mandir}/man1/qubes-guid.1.gz
/usr/bin/X-wrapper-qubes
%{_libdir}/qubes-gui-daemon/shmoverride.so
%config(noreplace) %{_sysconfdir}/qubes/guid.conf
/etc/xdg/autostart/qubes-screen-layout-watches.desktop
/etc/xdg/autostart/qubes-icon-receiver.desktop
/etc/X11/xinit/xinitrc.d/qubes-localgroup.sh
/usr/libexec/qubes/watch-screen-layout-changes
/usr/lib/qubes/icon-receiver
%config %{_sysconfdir}/qubes-rpc/qubes.WindowIconUpdater
%config %{_sysconfdir}/qubes/rpc-config/qubes.WindowIconUpdater

%files -n qubes-audio-daemon
/usr/bin/pacat-simple-vchan
/etc/qubes-rpc/qubes.AudioInputEnable
/etc/qubes-rpc/qubes.AudioInputDisable

%files -n qubes-gui-dom0
%config(noreplace) %{_sysconfdir}/qubes-rpc/policy/qubes.ClipboardPaste
%config(noreplace) %{_sysconfdir}/qubes-rpc/policy/qubes.WindowIconUpdater

%files -n qubes-audio-dom0
%{python3_sitelib}/qubesguidaemon-*.egg-info
%{python3_sitelib}/qubesguidaemon


%changelog
* Sun Oct 20 2019 Qubes OS Team <qubes-devel@groups.google.com>
- For complete changelog see: https://github.com/QubesOS/qubes-

* Sun Oct 20 2019 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 0770f27
- travis: switch to bionic

* Sun Sep 16 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 1f55c60
- version 4.0.9

* Sun Sep 16 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - a90544a
- xside: avoid making X11 calls in signal handler

* Thu Sep 13 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - af14f3e
- Clarify error message on mic attach if audio not enabled in the VM

* Fri Jul 27 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 840c849
- Merge remote-tracking branch 'qubesos/pr/23'

* Fri Jul 27 2018 Jean-Philippe Ouellet <jpo@vt.edu> - 148fb42
- Correct note about "temporary" shm lifecycle

* Tue May 08 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 6f5587b
- version 4.0.8

* Tue May 08 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 325a784
- gui-daemon: fix potential int overflow

* Sat Apr 21 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 2057273
- gui-daemon: fix forcing colorful frame when vm_window->image == NULL

* Tue Apr 03 2018 Frédéric Pierret <frederic.epitre@orange.fr> - 8eb0ae9
- spec.in: add changelog placeholder

* Sun Apr 01 2018 Frédéric Pierret <frederic.epitre@orange.fr> - 8d09634
- Create .spec.in and Source0

* Sun Mar 04 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 5340e17
- version 4.0.7

* Sun Mar 04 2018 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 72c8cda
- icon-receiver: make it more defensive against X11 race conditions

* Fri Dec 29 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 7b4c255
- icon-receiver: cache icons received for not (yet) existing windows

* Sat Dec 23 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 35ec463
- version 4.0.6

* Thu Dec 07 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - d1e1167
- Merge remote-tracking branch 'qubesos/pr/19'

* Thu Dec 07 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 1d31918
- Merge remote-tracking branch 'qubesos/pr/18'

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 94fd49d
- Move path to qvm-kill into header

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 4b0fd06
- Group file paths

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 0304cd2
- Remove dependency on xl toolstack

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - bf46809
- Actually dispatch resolution change notifications

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 4f3c468
- Coalesce at least some screen-change events

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 772997a
- Use cached x11 sock fd value

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 26f6c3a
- Simplify error handling with err(3) family

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 15adf34
- Improve usage msg

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 5c04122
- Sort includes

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 87a68c8
- Make resource exhaustion not fatal

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - 7a8aa76
- More idiomatic C

* Wed Dec 06 2017 Jean-Philippe Ouellet <jpo@vt.edu> - fa35ae6
- Remove dead code

* Thu Nov 30 2017 Your Name <you@example.com> - a132820
- Fix Gtk-Warning: {Unknown tag "br" on line 1 char 365} that causes the dialog to not be shown.

* Thu Oct 12 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 975e2c6
- version 4.0.5

* Sat Sep 23 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 2a314ca
- gui-daemon: force colorful frame even when VM have not sent window image

* Fri Aug 11 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - dd6a22f
- version 4.0.4

* Wed Aug 09 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - f6348bb
- Merge branch 'icon-updater-r4'

* Mon Aug 07 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 6b92222
- icon-updater: migrate to python3, use python3-xcffib

* Mon Aug 07 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 3fe820e
- icon-updater: make sure DISPLAY=:0 is set

* Mon Aug 07 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 3df3c2b
- icon-updater: fix for core3 API

* Mon Aug 07 2017 Paras Chetal <paras.chetal@gmail.com> - d441c49
- Fix always true conditional

* Sat Jul 29 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 0871961
- version 4.0.3

* Thu Jul 27 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 3ff26d3
- Add core3 extension to control microphone access

* Thu Jul 27 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - e6ceb93
- pulse: control over system bus not session bus

* Thu Jul 27 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - f20f23d
- gui-daemon: handle SIGUSR1 with exit(0)

* Wed Jul 05 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 14d7c66
- version 4.0.2

* Thu Jun 01 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - ad966dd
- xside: Fix handling -n flag - don't crach child process

* Fri May 26 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 8830fa0
- Update path to qrexec-policy

* Tue Apr 18 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - f14dc1c
- Add a config option for startup timeout

* Sun Apr 09 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 22c2042
- version 4.0.1

* Sun Apr 09 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 4372c48
- rpm: add missing BR: xen-devel

* Sat Apr 08 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 62146bf
- travis: switch to Qubes 4.0

* Sun Apr 02 2017 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 33ed70e
- Merge remote-tracking branch 'qubesos/pr/12'

