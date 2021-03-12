
Repository is intended to provide patches and rpm specs with experimental features to run under the Qubes OS.
Some of them may affect the stability and security, so use it with caution.

Wiki pages contain features description and setup instructions.

If you have a problem with repository features, please let us know through the issue tracker.

## Qway repository features

[Intel GVT-g mediated GPU pass-through with hardware accelerated xorg dummy driver](https://github.com/tabit-pro/tabit-qubes-repo/wiki/Intel-GVT_g-on-Qubes)

[Compiz window manager on Qubes OS](https://github.com/tabit-pro/tabit-qubes-repo/wiki/Compiz-on-QubesOS)

[Qubes Windows Tools crossbuild project](https://github.com/tabit-pro/tabit-qubes-repo/wiki/Qubes-Windows-Tools-crossbuild-project)

## Build packages

Source packages could be built using mock-scm plugin:
```
    mock -r fedora-qbs.cfg --buildsrpm --scm-enable --scm-option package=pkgname
```
* _fedora-qbs.cfg_ - mock configuration (example in current repo)
* _pkgname_ - name of the directory in the current repo

Binary packages could be built with mockchain:
```
    mockchain -r fedora-qbs.cfg --rebuild [srpm name] [srpm name]...
```

For detailed instance, take a look at process of building _qubes-windows-tools_ package:

```
# take a copy of mock config, it's not necessary to clone whole gitrepo
wget https://raw.githubusercontent.com/tabit-pro/qway-qubes-repo/master/fedora-qbs.cfg
# build source rpm package and place it to current directory (for qwt package downloading all tarballs may take a while)
mock -r fedora-qbs.cfg --buildsrpm --scm-enable --scm-option package=qubes-windows-tools --resultdir ./
# build binary package using srpm from previous step
mock -r fedora-qbs.cfg --rebuild qway-qubes-repo qubes-windows-tools*.srpm --resultdir ./
```

## Install packages

Binary packages could be [copied](https://www.qubes-os.org/doc/copy-from-dom0/#copying-to-dom0) to Dom0 and installed with rpm or dnf tool.
