# SPDX-License-Identifier: GPL-2.0-only

import json
from json.decoder import JSONDecodeError
#from xcp import logger

class DriverVariant:
    def __init__(self, drvname, vartype, varinfo):
        self.drvname = drvname
        self.oemtype = vartype
        self.version = varinfo["version"]
        self.hardware_present = varinfo["hardware_present"]
        self.priority = varinfo["priority"]
        self.status = varinfo["status"]

    def __repr__(self):
        return "<%s variant: %s (%s)>" % (self.drvname, self.oemtype, self.version)

    def getHumanVariantLabel(self):
        template = "Driver: {name}-{oemtype} {version} {status}"
        return template.format(name=self.drvname, oemtype=self.oemtype,
                               version=self.version,
                               status=self.status)

    def getHardwarePresentText(self):
        if self.hardware_present:
            return "Yes"
        return "No"

    def getPriorityText(self):
        return str(self.priority)

class Drivers:
    def __init__(self, drvname, drvinfo=None):
        def sortKey(e):
            return e.oemtype

        self.drvname = drvname
        self.type = ""
        self.friendly_name = ""
        self.description = ""
        self.info = ""
        self.selected = None
        self.active = None
        self.variants = []
        if drvinfo != None:
            self.type = drvinfo["type"]
            self.friendly_name = drvinfo["friendly_name"]
            self.description = drvinfo["description"]
            self.info = drvinfo["info"]
            self.selected = drvinfo["selected"]
            self.active = drvinfo["active"]
            for vartype, varinfo in drvinfo["variants"].items():
                self.variants.append(DriverVariant(drvname, vartype, varinfo))
            self.variants.sort(key=sortKey)

    def __repr__(self):
        return "<drivers: %s (%s)>" % (self.friendly_name, self.description)

    def getHumanDriverLabel(self):
        template = "{friendly_name} ({info})"
        #template = "{devtype} device driver {name} [{description}]"
        return template.format(friendly_name=self.friendly_name, info=self.info)

    def getVersion(self):
        if len(self.variants) == 0:
            return "unknown"
        return self.variants[0].version

    def getDriversVariants(self):
        variants = []
        template = "{description} variant: {vartype}"
        for variant in self.variants:
            label = template.format(description=self.description, vartype=variant.oemtype)
            variants.append((label, variant))
        return variants

    def selectVariantByDefault(self):
        variant = None
        l = [float(v.priority) for v in self.variants]
        if len(l) > 0:
            idx = l.index(max(l))
            variant = self.variants[idx]
        return variant

    def getSelectedText(self):
        if self.selected != None:
            return self.selected
        return "N/A"

    def getActiveText(self):
        if self.active != None:
            return self.active
        return "N/A"

def parseDMVJsonData(dmvlist):
    def sortKey(e):
        return e.type

    drivers = []
    for name, info in dmvlist.items():
        drivers.append(Drivers(name, info))
    drivers.sort(key=sortKey)
    return drivers

def cloneDriverWithoutVariants(olddrv, newdrv):
    newdrv.type = olddrv.type
    newdrv.friendly_name = olddrv.friendly_name
    newdrv.description = olddrv.description
    newdrv.info = olddrv.info
    newdrv.selected = olddrv.selected
    newdrv.active = olddrv.active

def getHardwarePresentDrivers(drivers):
    hw_present_drivers = []
    for d in drivers:
        driver = Drivers(d.drvname)
        cloneDriverWithoutVariants(d, driver)
        driver.variants = list(filter(lambda x:x.hardware_present, d.variants))
        if len(driver.variants) > 0:
            hw_present_drivers.append(driver)
    return hw_present_drivers

def getHardwarePresentDriver(drivers, name):
    hw_present_drivers = None
    for d in drivers:
        if d.drvname == name:
            driver = Drivers(d.drvname)
            cloneDriverWithoutVariants(d, driver)
            driver.variants = list(filter(lambda x:x.hardware_present, d.variants))
            if len(driver.variants) > 0:
                hw_present_drivers = driver
    return hw_present_drivers

def selectDefaultDriverVariants(drivers):
    variants = []
    for d in drivers:
        v = d.selectVariantByDefault()
        if v != None:
            variants.append(v)
    return variants

def queryMultipleVariants(context):
    return context

def querySingleVariant(context):
    return context

def queryDriversOrVariant(context):
    if isinstance(context, Drivers):
        return ("drivers", context)
    elif isinstance(context, list):
        return ("variants", queryMultipleVariants(context))
    elif isinstance(context, DriverVariant):
        return ("variant", querySingleVariant(context))
    return ("unknown", None)

def sameDriverMultiVariantsSelected(variants):
    for i in range(0, len(variants)):
        item1 = variants[i]
        a = variants[i+1:len(variants)]
        for item2 in a:
            if item1.drvname == item2.drvname:
                return (True, item1.drvname)
    return (False, "")

def getMockDMVList():
    jsondata = '''
    {
        "igb": {
            "type": "network",
            "friendly_name": "Intel I350 Gigabit Ethernet Controller",
            "description": "intel-igb",
            "info": "igb",
            "selected": null,
            "active": null,
            "variants": {
                "generic": {
                    "version": "5.17.5",
                    "hardware_present": true,
                    "priority": 30,
                    "status": "production"
                },
                "dell": {
                    "version": "5.17.5",
                    "hardware_present": false,
                    "priority": 40,
                    "status": "production"
                }
            }
        },
        "ice": {
            "type": "network",
            "friendly_name": "Intel E810 Ethernet Controller",
            "description": "intel-ice",
            "info": "ice",
            "selected": "supermicro",
            "active": null,
            "variants": {
                "generic": {
                    "version": "1.15.5",
                    "hardware_present": true,
                    "priority": 50,
                    "status": "production"
                },
                "supermicro": {
                    "version": "1.15.5",
                    "hardware_present": true,
                    "priority": 30,
                    "status": "production"
                }
            }
        },
        "fnic": {
            "type": "storage",
            "friendly_name": "Cisco UCS VIC Fibre Channel over Ethernet HBA",
            "description": "cisco-fnic",
            "info": "fnic",
            "selected": "generic",
            "active": null,
            "variants": {
                "generic": {
                    "version": "3.18.2",
                    "hardware_present": true,
                    "priority": 50,
                    "status": "production"
                } 
            }
        }
    }
    '''
    try:
        dmvlist = json.loads(jsondata)
    except JSONDecodeError as e:
        #print(f"Invalid JSON: {e}")
        return None
    return parseDMVJsonData(dmvlist)
