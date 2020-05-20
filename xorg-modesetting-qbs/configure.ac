# Initialize Autoconf
AC_PREREQ([2.60])
AC_INIT([xorg-modesetting-qbs],
        [1.20.6],
        [],
        [xorg-modesetting-qbs])
AC_CONFIG_SRCDIR([Makefile.am])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_AUX_DIR(.)

# Initialize Automake
AM_INIT_AUTOMAKE([foreign dist-bzip2])

# Require xorg-macros: XORG_DEFAULT_OPTIONS
m4_ifndef([XORG_MACROS_VERSION],
          [m4_fatal([must install xorg-macros 1.3 or later before running autoconf/autogen])])
XORG_MACROS_VERSION(1.3)
XORG_DEFAULT_OPTIONS

# Initialize libtool
AC_DISABLE_STATIC
AC_PROG_LIBTOOL

AH_TOP([#include "xorg-server.h"])

# Define a configure option for an alternate module directory
AC_ARG_WITH(xorg-module-dir, [  --with-xorg-module-dir=DIR ],
                             [ moduledir="$withval" ],
                             [ moduledir="$libdir/xorg/modules" ])
AC_SUBST(moduledir)

# Store the list of server defined optional extensions in REQUIRED_MODULES
XORG_DRIVER_CHECK_EXT(RANDR, randrproto)
XORG_DRIVER_CHECK_EXT(RENDER, renderproto)

PKG_CHECK_MODULES(XORG, [xorg-server >= 1.4.99.901] xproto fontsproto $REQUIRED_MODULES)

# Checks for libraries.
AC_CHECK_LIB([xengnttab], [xengntshr_open])

# Checks for header files.
AC_HEADER_STDC
AC_CHECK_HEADER([xengnttab.h])

DRIVER_NAME=modesettingqbs
AC_SUBST([DRIVER_NAME])

AC_CONFIG_FILES([
                Makefile
])
AC_OUTPUT
