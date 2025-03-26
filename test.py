#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-2.0-only

import dmvutil

if __name__ == '__main__':
    drivers = dmvutil.getMockDMVList()
    for d in drivers:
        print(d.getHumanDriverLabel())
        for variant in d.variants:
            print(variant)

    print("")
    print("===== hardware present =====")

    hw_present_drivers = dmvutil.getHardwarePresentDrivers(drivers)
    for d in hw_present_drivers:
        print(d.getHumanDriverLabel())
        print(d.getVersion())
        for variant in d.variants:
            print(variant)

    print("")
    print("=====")

    d = dmvutil.getHardwarePresentDriver(drivers, "igb")
    print(d.getHumanDriverLabel())
    for variant in d.variants:
        print(variant)
        itemtype, _ = dmvutil.queryDriversOrVariant(variant)
        print("===> %s %s" % (itemtype, variant.getHumanVariantLabel()))

    print("")
    print("=====")

    d = dmvutil.getHardwarePresentDriver(drivers, "ice")
    got, drvname = dmvutil.sameDriverMultiVariantsSelected(d.variants)
    if got:
        print("sameDriverMultiVariantsSelected")
        print(drvname)

    print("")
    print("===== default selection =====")

    variants = dmvutil.selectDefaultDriverVariants(hw_present_drivers)
    print(variants)
    for variant in variants:
        print(variant)
        itemtype, _ = dmvutil.queryDriversOrVariant(variant)
        print("===> %s %s" % (itemtype, variant.getHumanVariantLabel()))
    d = dmvutil.getHardwarePresentDriver(drivers, "fnic")
    v = d.variants[0]
    if v in variants:
        print("got")
