#ifndef XF86_QUBES_COMMON_H
#define XF86_QUBES_COMMON_H

// Order is important!
#include <xorg-server.h>
#include <xf86.h>

#include <poll.h>
#define xserver_poll(fds, nfds, timeout) poll(fds, nfds, timeout)

#include <xengnttab.h>

static xengntshr_handle *xgs;
static uint32_t gui_domid;

// Metadata of mapped grant pages
struct xf86_qubes_pixmap {
    size_t pages; // Number of pages
    uint32_t *refs; // Pointer to grant references
    uint8_t *data; // Local mapping
};

// Only intended for use in the Qubes xorg modules.

extern _X_EXPORT Bool xf86_qubes_pixmap_register_private(void);
extern _X_EXPORT DevPrivateKeyRec xf86_qubes_pixmap_get_private_key(void);
extern _X_EXPORT void xf86_qubes_pixmap_set_private_key(DevPrivateKeyRec msPrivateKey);

extern _X_EXPORT void xf86_qubes_pixmap_set_private(
        PixmapPtr pixmap,
        struct xf86_qubes_pixmap *priv);

extern _X_EXPORT struct xf86_qubes_pixmap *xf86_qubes_pixmap_get_private(
        PixmapPtr pixmap);

// xenctrl and xorg headeres are not compatible. So define the requires
// constants here.
#ifndef XC_PAGE_SHIFT
#define XC_PAGE_SHIFT           12
#define XC_PAGE_SIZE            (1UL << XC_PAGE_SHIFT)
#define XC_PAGE_MASK            (~(XC_PAGE_SIZE-1))
#endif

#endif
