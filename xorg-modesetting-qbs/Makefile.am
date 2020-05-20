#  Copyright 2005 Adam Jackson.
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  on the rights to use, copy, modify, merge, publish, distribute, sub
#  license, and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice (including the next
#  paragraph) shall be included in all copies or substantial portions of the
#  Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT.  IN NO EVENT SHALL
#  ADAM JACKSON BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
#  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# this is obnoxious:
# -module lets us name the module exactly how we want
# -avoid-version prevents gratuitous .0.0.0 version numbers on the end
# _ladir passes a dummy rpath to libtool so the thing will actually link
# TODO: -nostdlib/-Bstatic/-lgcc platform magic, not installing the .a, etc.

AM_CFLAGS = $(XORG_CFLAGS) $(PCIACCESS_CFLAGS) $(GBM_CFLAGS) -DXSERVER_LIBPCIACCESS -DXSERVER_PLATFORM_BUS -DGLAMOR_HAS_GBM -DCOMPOSITE -DGLAMOR_HAS_GBM_LINEAR -DGBM_BO_WITH_MODIFIERS

modesettingqbs_drv_la_LTLIBRARIES = modesettingqbs_drv.la
modesettingqbs_drv_la_LDFLAGS = -module -avoid-version
modesettingqbs_drv_la_LIBADD = $(XORG_LIBS) $(GBM_LIBS)
modesettingqbs_drv_ladir = @moduledir@/drivers

modesettingqbs_drv_la_SOURCES = \
         compat-api.h \
         driver.c \
         drmmode_display.c \
         drmmode_display.h \
         dumb_bo.c \
         pageflip.c \
         present.c \
         vblank.c \
	 xf86-qubes-common.c \
         dri2.c
