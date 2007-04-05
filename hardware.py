#!/usr/bin/env python
# Copyright (c) 2005-2006 XenSource, Inc. All use and distribution of this 
# copyrighted material is governed by and subject to terms and conditions 
# as licensed by XenSource, Inc. All other rights reserved.
# Xen, XenSource and XenEnterprise are either registered trademarks or 
# trademarks of XenSource Inc. in the United States and/or other countries.

###
# XEN CLEAN INSTALLER
# Hardware discovery tools
#
# written by Andrew Peace

import os
import version
import constants
import xelogging
import util

# More of the hardware tools will be moved into here in future.

# module => module list
# if we discover x, actually load module_map[x]:
module_map = {
    # general:
    'mptscsih'     : ['mptspi', 'mptscsih'],
    'i810-tco'     : [],
    'usb-uhci'     : [],
    'ide-scsi'     : ['ide-generic'],
    'piix'         : ['ata-piix', 'piix', 'ide-generic'],

    # blacklist framebuffer drivers (we don't need them):
    "arcfb"        : [],
    "aty128fb"     : [],
    "atyfb"        : [],
    "radeonfb"     : [],
    "cirrusfb"     : [],
    "cyber2000fb"  : [],
    "cyblafb"      : [],
    "gx1fb"        : [],
    "hgafb"        : [],
    "i810fb"       : [],
    "intelfb"      : [],
    "kyrofb"       : [],
    "i2c-matroxfb" : [],
    "neofb"        : [],
    "nvidiafb"     : [],
    "pm2fb"        : [],
    "rivafb"       : [],
    "s1d13xxxfb"   : [],
    "savagefb"     : [],
    "sisfb"        : [],
    "sstfb"        : [],
    "tdfxfb"       : [],
    "tridentfb"    : [],
    "vfb"          : [],
    "vga16fb"      : [],
    }


###
# Module loading

def module_present(module):
    mtmp = module.replace('-', '_')
    pm = open('/proc/modules', 'r')
    loaded_modules = pm.readlines()
    pm.close()

    return mtmp in [x.replace('-', '_') for x in loaded_modules]

def modprobe(module, params = ""):
    xelogging.log("Loading module %s" % " ".join([module, params]))
    rc = util.runCmd("modprobe %s %s" % (module, params))
    if rc != 0:
        xelogging.log("(Failed.)")

    return rc

def modprobe_file(module, params = "", name = None):
    INSMOD = '/sbin/insmod'

    # First use modinfo to find out what the dependants of the
    # module are and modprobe them:
    #
    # deps will initially look like 'depends:    x,y,z'
    rc, out = util.runCmdWithOutput("modinfo %s" % module)
    if rc != 0:
        raise RuntimeError, "Error interrogating module."
    [deps] = filter(lambda x: x.startswith("depends:"),
                    out.split("\n"))
    deps = deps[9:].strip()
    deps = deps.split(',')
    for dep in deps:
        if not module_present(dep):
            modprobe(dep)
    
    xelogging.log("Insertung module %s %s (%s)" %(module, params, name))
    rc = util.runCmd2([INSMOD, module, params])

    if rc != 0:
        xelogging.log("(Failed.)")

    return rc

################################################################################
# These functions assume we're running on Xen.

_vt_support = None

def VTSupportEnabled():
    global _vt_support

    # get the answer and cache it if necessary:
    if _vt_support == None:
        assert os.path.exists(constants.XENINFO)
        rc, caps = util.runCmdWithOutput(constants.XENINFO + " xen-caps")
        assert rc == 0
        caps = caps.strip().split(" ")
        _vt_support = "hvm-3.0-x86_32" in caps
    return _vt_support

def getHostTotalMemoryKB():
    assert os.path.exists(constants.XENINFO)
    rc, mem = util.runCmdWithOutput(constants.XENINFO + " host-total-mem")
    assert rc == 0
    return int(mem.strip())
