
Repository is intended to provide patches and rpm specs with experimental features to run under the Qubes OS.
Some of them may affect the stability and security, so use it with caution.

Wiki pages contain features description and setup instructions.

If you have a problem with repository features, please let us know through the issue tracker.

## Qway repository features

[Intel GVT-g mediated GPU pass-through with hardware accelerated xorg dummy driver](https://github.com/tabit-pro/tabit-qubes-repo/wiki/Intel-GVT_g-on-Qubes)

[Compiz window manager on Qubes OS](https://github.com/tabit-pro/tabit-qubes-repo/wiki/Compiz-on-QubesOS)

[Qubes Windows Tools crossbuild project](https://github.com/tabit-pro/qwt-crossbuild)

## Build packages

Source packages could be built using mock-scm plugin:
```
    mock -r fedora-qbs.cfg --buildsrpm --scm-enable -scm-option package=pkgname
```
* _fedora-qbs.cfg_ - mock configuration (example in current repo)
* _pkgname_ - name of the directory in the current repo

Binary packages could be built with mockchain:
```
    mockchain -r fedora-qbs.cfg --rebuild [srpm name] [srpm name]...
```

## Install packages

Binary packages could be [copied](https://www.qubes-os.org/doc/copy-from-dom0/#copying-to-dom0) to Dom0 and installed with rpm or dnf tool.
