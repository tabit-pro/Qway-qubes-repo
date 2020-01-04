
Repository is intended to provide patches and rpm specs with experimental features to run under the Qubes OS.

At the moment the only feature that we are publishing here is an **Intel GVT-g mediated pass-through with hardware accelerated xorg dummy driver**.

# Intel GVT-g on Qubes

## Prerequisites
Existing GVT-g runtime implementation raise security risks at least due to executing qemu in dom0 without stubdom (or other) restrictions. Use it with caution.

Our 'proven to work' configurations is limited to Intel KabyLake and experimental Qubes r4.1, but [supported xengt platforms](https://01.org/node/28748) should also work fine.

## Build and install dom0 packages

The following packages should be built from current repo and installed in the dom0: _libvirt, kernel-gvt, qemu-qubes, xen_.

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
## Configure dom0

Add the following options to _GRUB_CMDLINE_LINUX_ in _/etc/default/grub_:  
* _i915.enable_gvt=1_ - to enable GVT-g;
* _intel_iommu=igfx_off_ - to avoid domU stability issues.

Add _force_drivers+="xengt"_ to _/etc/dracut.conf_ if xengt module wasn't loaded while booting gvt-enabled domU.

Don't forget to regenerate initrd image (_dracut -f_) and recreate grub menu (_grub2-mkconfig -o /boot/grub2/grub.cfg_).

## Modify qubes libvirt template

Add new _qemu-qubes_ option to _/usr/share/qubes/templates/libvirt/xen.xml_, so we could use _qvm-feature_ to conditionally run _qemu-qubes_ in dom0.
```xml
    {% if vm.features.get('qemu-qubes', False) %}
    <emulator>/usr/bin/qemu-qubes</emulator>
    <video>
          <model type="xengt" low_gm_sz='128'/>
    </video>
    {% else %}
    <!-- existing definitions of hvm emulator and video -->
    {% endif %}
```
Supported xengt variables:  
* **low_gm_sz** - the low graphic memory size which is CPU visible, default is 64.
* **high_gm_sz** - the high gm size which is CPU invisible, default is 448.  
* **fence_sz** - the number of the fence registers, default is 4.

## Modify domU template

Clone existing fedora template and customize the configuration:
* switch VM mode to HVM;
* set _none_ in VM kernel option to boot with domU kernel;
* set qrexec_timeout 120 (device init requires some time);
* setup ssh service and iptable rules to allow access via netvm for debug purposes;
* install the latest available kernel - kernel upstream should have GVT-g support. If you are experiencing issues then the _kernel-gvt_ package from dom0 might work;
* install _xorg-dummy-egl_ package;
* replace _/etc/X11/xorg-qubes.conf.template_ with _xorg-qubes-egl.conf.template_ to enable hardware accelerated dummy driver.

## Known issues

There is an issue with a font rendering in gtk applications due to our basic EGL implementation. Turning off hardware acceleration on gtk side is a common workaround (set env variable _GDK_RENDERING=image_).

Intel drm driver requires some time to init or render will fail with error in _.local/share/xorg/Xorg.0.log_). Easy (and ugly) way is to add sleep timeout to _/usr/bin/qubes-run-xorg_ script.

Maximize Total Graphic Memory in UEFI settings.

Properly created vGPU in qemu logs looks like that (_/var/log/xen/qemu-dm-VM.log_):

    Create vgt ISA bridge successfully
    set vendor id(0) for devfn(10)
    vgt: vgt_initfn
    Create vgt VGA successfully
    set vendor id(8086) for devfn(9)
    set vendor id(8086) for devfn(b)
    set vendor id(5853) for devfn(18)
    set vendor id(10ec) for devfn(20)
    vGT: create_vgt_instance: domid=29, low_gm_sz=64MB, high_gm_sz=448MB, fence_sz=4, vgt_primary=-1

## Screenshots

![glmark](https://user-images.githubusercontent.com/49684805/71646212-6b0c7200-2cb2-11ea-92f0-a16b7e8c0694.png)
![mpv](https://user-images.githubusercontent.com/49684805/71646214-6e9ff900-2cb2-11ea-879b-56e384f96fdc.png)

## Based on

* [glamor acceleration which enables native OpenGL support](https://patchwork.freedesktop.org/patch/143119/)
* [GVT-g qemu implementation](https://github.com/intel/igvtg-qemu)
* [gvt-linux project](https://github.com/intel/gvt-linux)
* [xen.pg patches](https://github.com/xenserver/xen.pg.git)
