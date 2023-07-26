import os
import subprocess
import json


def parse(result):
    if len(result.stderr) > 0:
        return False, result.args
    return True, " ".join(result.stdout.decode().split())


class LVM2_Size:
    sizes = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}

    def __init__(self, size):
        self.__size = size

    def set_size(self, size):
        self.__size = size

    def get_size(self):
        return self.__size

    @staticmethod
    def bytesto(bytes, to, bsize=1024):
        """convert bytes to megabytes, etc.
        sample code:
                print('mb= ' + str(bytesto(314575262000000, 'm')))
        sample output:
                mb= 300002347.946
        """
        r = float(bytes)
        for i in range(LVM2_Size.sizes[to]):
            r = r / bsize
        return r

    @staticmethod
    def tobytes(size, to, bsize=1024):
        """convert bytes to megabytes, etc.
        sample code:
                print('mb= ' + str(bytesto(314575262000000, 'm')))
        sample output:
                mb= 300002347.946
        """
        r = float(size)
        for i in range(LVM2_Size.sizes[to]):
            r = r * bsize
        return int(r)


class LVM2_Volume:
    def __init__(self):
        pass

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_size(self, size):
        self.size = size

    def get_size(self):
        return self.size

    def set_uuid(self, uuid):
        self.uuid = uuid

    def get_uuid(self):
        return self.uuid

    def __repr__(self):
        return (
            "Name: "
            + str(self.name)
            + " | Size: "
            + str(self.size.get_size())
            + " Bytes | UUID: "
            + str(self.uuid)
        )


class LVM2_PhysicalVolume(LVM2_Volume):
    def __init__(self):
        pass

    def set_group(self, group):
        self.group = group

    def get_group(self):
        return self.group

    def __repr__(self):
            return (
                "Type: PhysicalVolume | Name: "
                + str(self.name)
                + " | Size: "
                + str(self.size.get_size())
                + " Bytes | UUID: "
                + str(self.uuid)
                + " | Volume Group's Name: "
                + str(self.group.get_name())
            )


class LVM2_VolumeGroup(LVM2_Volume):
    def __init__(self):
        self.__pv = []
        self.__lv = []

    def add_physical_volume(self, pv):
        self.__pv.append(pv)

    def add_logical_volume(self, logical_volume):
        self.__lv.append(logical_volume)

    def __repr__(self):
        repr = str(
            "Type: VolumeGroup | Name: "
            + str(self.name)
            + " | Size: "
            + str(self.size.get_size())
            + " Bytes | UUID: "
            + str(self.uuid)
            + " | Logical Volume(s) ("
            + str(len(self.__lv))
            + "): "
        )
        for lv in self.__lv:
            repr += str(lv.get_name()) + ", "
        repr += " | Physical Volume(s) (" + str(len(self.__pv)) + "): "
        for pv in self.__pv:
            repr += str(pv.get_name()) + ", "
        return repr


class LVM2_LogicalVolume(LVM2_Volume):
    def __init__(self):
        self.mount_point = b''
        pass

    def set_group(self, group):
        self.group = group

    def get_group(self):
        return self.group

    def set_mounted(self, mtn):
        self.is_mounted = mtn

    def is_mounted(self):
        return self.is_mounted

    def get_mount_point(self):
        return self.mount_point

    def set_mount_point(self, point):
        self.mount_point = point

    def __repr__(self):
        return (
            "Type: LogicalVolume | Name: "
            + str(self.name)
            + " | Size: "
            + str(self.size.get_size())
            + " Bytes | UUID: "
            + str(self.uuid)
            + " | Volume Group's Name: "
            + str(self.group.get_name())
            + " | IsMounted: "
            + str(self.is_mounted)
            + " | Mount Point: "
            + str(self.mount_point)
        )


class LVM2_Parse_Result:
    def __init__(self, pvs, vgs, lvs):
        self.__lvs = lvs
        self.__pvs = pvs
        self.__vgs = vgs

    def get_all(self):
        all = []
        all.extend(self.__lvs)
        all.extend(self.__pvs)
        all.extend(self.__vgs)
        return all

    def get_logical_volumes(self):
        return self.__lvs

    def get_physical_volumes(self):
        return self.__pvs

    def get_volume_groups(self):
        return self.__vgs

    def get_by_name(self, name):
        for volume in self.get_all():
            if volume.get_name() == name:
                return volume
            
    def __repr__(self):
        repr = ""
        for volume in parser.get_all():
            repr += "\n" + str(volume)
        return repr

class LVM2_Parser(LVM2_Parse_Result):
    def __init__(self):
        super().__init__([], [], [])

    def scan_all(self):
        super().__init__([], [], [])
        self.parse_pvs()
        self.parse_lvs()
        self.parse_vgs()
        valid, mounteds = parse(
            subprocess.run(["findmnt", "-l", "-J"], capture_output=True)
        )
        if valid:
            temp_mounteds = json.loads(mounteds)["filesystems"]
            mounteds = {}
            for mtn_data in temp_mounteds:
                mounteds[mtn_data["source"]] = mtn_data
        for volume in self.get_all():
            if isinstance(volume, LVM2_VolumeGroup):
                continue
            vg = self.get_by_name(volume.get_group())
            volume.set_group(vg)
            if isinstance(volume, LVM2_LogicalVolume):
                if (valid):
                    mtn_data = mounteds.get(
                        "/dev/mapper/" 
                        + vg.get_name().decode()
                        + "-" 
                        + volume.get_name().decode()
                    )
                    if (mtn_data != None):
                        volume.set_mounted(True)
                        volume.set_mount_point(bytes(mtn_data["target"], encoding='utf-8'))
                    else:
                        volume.set_mounted(False)
                vg.add_logical_volume(volume)
            else:
                vg.add_physical_volume(volume)

    def parse_pvs(self):
        result = subprocess.run(
            [
                "pvs",
                "--noheadings",
                "--units",
                "B",
                "--separator",
                ":",
                "-o",
                "+pv_uuid",
            ],
            capture_output=True,
        )
        pvs_data = result.stdout.split(b"\n")
        pvs = self.get_physical_volumes()
        for pv_data in pvs_data:
            if len(pv_data) < 1:
                break
            pv = LVM2_PhysicalVolume()
            splited_data = pv_data.split(b":")
            pv.set_name(splited_data[0].replace(b" ", b""))
            pv.set_uuid(splited_data[6])
            pv.set_group(splited_data[1])
            pv.set_size(LVM2_Size(splited_data[4].replace(b"B", b"")))
            pvs.append(pv)

    def parse_vgs(self):
        result = subprocess.run(
            [
                "vgs",
                "--noheadings",
                "--units",
                "B",
                "--separator",
                ":",
                "-o",
                "+vg_uuid",
            ],
            capture_output=True,
        )
        vgs_data = result.stdout.split(b"\n")
        vgs = self.get_volume_groups()
        for vg_data in vgs_data:
            if len(vg_data) < 1:
                break
            vg = LVM2_VolumeGroup()
            splited_data = vg_data.split(b":")
            vg.set_name(splited_data[0].replace(b" ", b""))
            vg.set_uuid(splited_data[7])
            vg.set_size(LVM2_Size(splited_data[5].replace(b"B", b"")))
            vgs.append(vg)

    def parse_lvs(self):
        result = subprocess.run(
            [
                "lvs",
                "--noheadings",
                "--units",
                "B",
                "--separator",
                ":",
                "-o",
                "+lv_uuid",
            ],
            capture_output=True,
        )
        lvs_data = result.stdout.split(b"\n")
        lvs = self.get_logical_volumes()
        for lv_data in lvs_data:
            if len(lv_data) < 1:
                break
            lv = LVM2_LogicalVolume()
            splited_data = lv_data.split(b":")
            lv.set_name(splited_data[0].replace(b" ", b""))
            lv.set_group(splited_data[1])
            lv.set_uuid(splited_data[12])
            lv.set_size(LVM2_Size(splited_data[3].replace(b"B", b"")))
            lvs.append(lv)

# parser = LVM2_Parser()
# parser.scan_all()
# print(parser)
