Summary: QEMU is a FAST! processor emulator
Name: qemu-qubes
Version: 4.2.0
Release: 7%{?dist}
Epoch: 2000
License: GPLv2 and BSD and MIT and CC-BY
URL: http://www.qemu.org/

Source0: http://wiki.qemu-project.org/download/qemu-%{version}.tar.xz

# gvt-g
Patch3001: qemu-qubes-4.2.0-add-vgt-support.patch

# seccomp containment support
BuildRequires: libseccomp-devel >= 2.3.0
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
BuildRequires: xen-devel

BuildRequires: glibc-static glib2-static zlib-static
BuildRequires: python gcc chrpath

Requires: libseccomp >= 1.0.0
Requires: xen-runtime

%description
QEMU is a generic and open source processor emulator which achieves a good
emulation speed by using dynamic translation. QEMU has two operating modes:

 * Full system emulation. In this mode, QEMU emulates a full system (for
   example a PC), including a processor and various peripherials. It can be
   used to launch different Operating Systems without rebooting the PC or
   to debug system code.
 * User mode emulation. In this mode, QEMU can launch Linux processes compiled
   for one CPU on another CPU.

As QEMU requires no host kernel patches to run, it is safe and easy to use.

%prep
%autosetup -p1 -n qemu-%{version}

%build

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id -Wl,-z,nodlopen -Wl,-z,nodump -Wl,-z,noexecstack"

run_configure() {
    ../configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
	--datadir=%{_datadir}/qemu-xen \
        --with-pkgversion=%{name}-%{version}-%{release} \
        --disable-strip \
        --disable-werror \
        --disable-kvm \
        --enable-pie \
        --enable-xen \
        --enable-vgt \
        --enable-seccomp \
        --enable-xen-pci-passthrough \
        --python=/usr/bin/python3 \
        --enable-trace-backend="log" \
        --extra-ldflags="$extraldflags" \
        --extra-cflags="-DXEN_PT_LOGGING_ENABLED=1" \
        "$@" || cat config.log
}

mkdir build
pushd build

run_configure \
    --target-list="i386-softmmu" \
    --disable-modules \
    --disable-tcg \
    --disable-mpath \
    --disable-sdl \
    --disable-gtk \
    --disable-fdt \
    --disable-bluez \
    --disable-libusb \
    --disable-slirp \
    --disable-docs \
    --disable-vhost-net \
    --disable-spice \
    --disable-guest-agent \
    --disable-guest-agent-msi \
    --audio-drv-list= \
    --disable-smartcard \
    --enable-vnc \
    --disable-spice \
    --disable-gnutls \
    --disable-nettle \
    --disable-gcrypt \
    --disable-vte \
    --disable-curses \
    --disable-cocoa \
    --disable-virtfs \
    --disable-brlapi \
    --disable-curl \
    --disable-rdma \
    --disable-vde \
    --disable-netmap \
    --disable-linux-aio \
    --disable-cap-ng \
    --disable-attr \
    --disable-rbd \
    --disable-libiscsi \
    --disable-libnfs \
    --disable-usb-redir \
    --disable-lzo \
    --disable-snappy \
    --disable-bzip2 \
    --disable-coroutine-pool \
    --disable-glusterfs \
    --disable-tpm \
    --disable-numa \
    --disable-tcmalloc \
    --disable-jemalloc \
    --disable-vhost-scsi \
    --disable-qom-cast-debug \
    --disable-virglrenderer \
    --disable-tools \
    --disable-replication \
    --disable-vhost-vsock \
    --disable-hax \
    --disable-vhost-vsock \
    --disable-opengl \
    --disable-xfsctl \
    --disable-blobs \
    --disable-crypto-afalg \
    --disable-live-block-migration \
    --disable-vxhs \
    --disable-vhost-user \
    --disable-vhost-crypto \
    --disable-xkbcommon \
    --disable-slirp \
    --disable-blobs \
    --disable-user \
    --cxx=/non-existent

make V=1 %{?_smp_mflags} $buildldflags  

popd

%install

pushd build
mv ./i386-softmmu/qemu-system-i386 qemu-qubes
install -D -p -m 0755 -t %{buildroot}%{_bindir} qemu-qubes
#make DESTDIR=%{buildroot} install
popd

# It should always be safe to remove RPATHs from
# the final binaries:
for f in %{buildroot}%{_bindir}/* %{buildroot}%{_libdir}/* \
         %{buildroot}%{_libexecdir}/*; do
  if file $f | grep -q ELF | grep -q -i shared; then chrpath --delete $f; fi
done

%files
%{_bindir}/qemu-qubes

%changelog

