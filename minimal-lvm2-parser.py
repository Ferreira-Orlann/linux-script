import subprocess
import json

class LVM2_Commmand_Result:
    def __init__(self, completed_process):
        self.__stdout = " ".join(completed_process.stdout.decode().split())
        self.__stderr = " ".join(completed_process.stderr.decode().split())
        self.__completed_process = completed_process
        if (len(completed_process.stderr) > 0 or completed_process.returncode != 0):
            self.__error = True
        else:
            self.__error = False
        
    def has_error(self):
        return self.__error
        
    def get_result(self):
        if (self.__error):
            return self.__stderr
        return self.__stdout
    
    def get_ccompleted_process(self):
        return self.__completed_process

    def get_stdout(self):
        return self.__stdout
    
    def get_stderr(self):
        return self.__stder

    def get_return_code(self):
        return self.__completed_process.returncode


class Size:
    sizes = {"k": 1, "m": 2, "g": 3, "t": 4, "p": 5, "e": 6}

    def __init__(self, bytes):
        self.__bytes = bytes

    def set_bytes(self, bytes):
        self.__bytes = bytes

    def get_bytes(self):
        return self.__bytes

    @staticmethod
    def bytesto(bytes, to, bsize=1024):
        """convert bytes to megabytes, etc.
        sample code:
                print('mb= ' + str(bytesto(314575262000000, 'm')))
        sample output:
                mb= 300002347.946
        """
        r = float(bytes)
        for i in range(Size.sizes[to]):
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
        for i in range(Size.sizes[to]):
            r = r * bsize
        return int(r)


class JsonDataContener:
    def __init__(self):
        self.__values = {}
        self.__is_valid = False
        
    def get_value(self, key):
        return self.__values[key]

    def set_value(self, key, value):
        self.__values[key] = value
    
    def is_valid(self):
        return self.__is_valid

    def set_valid(self, value):
        self.__is_valid = value
        
    def get_all_values(self):
        return self.__values
        
    def __repr__(self) -> str:
        return str(json.dumps(self.__values, indent = 4))
    

class Device(JsonDataContener):
    pass


class LVM2_PhysicalVolume(JsonDataContener):
    pass


class LVM2_VolumeGroup(JsonDataContener):
    pass


class LVM2_LogicalVolume(JsonDataContener):
    pass


class LVM2_PhysicalVolume_Segment(JsonDataContener):
    pass


class LVM2_Segment(JsonDataContener):
    pass


class LVM2():
    def __init__(self):
        self.__objects = []
        self.__volumes = {}
        self.__devices = {}
        self.scan_all()
        
    def create_logical_volume():
        pass
    
    def scan_all(self):
        for obj in self.__objects:
            obj.set_valid(False)
        self.__objects.clear()
        self.__volumes.clear()
        self.__devices.clear()
        self.scan_devices()
        self.scan_lvm2()
        
    def scan_devices(self):
        report_cmd_result = self.exec_cmd("lsblk -lnOJb")
        if (report_cmd_result.has_error()):
            raise Exception("Command Error: lsblk -lnOJb")
        lsblk_data_json = json.loads(report_cmd_result.get_result())["blockdevices"]
        for contener_data in lsblk_data_json:
            device = Device()
            self.parse_object(contener_data, device)
            self.__devices[device.get_value("name") + " | " + device.get_value("kname") + " | " +device.get_value("path")] = device
            self.__objects.append(device)
        
    def scan_lvm2(self):
        report_cmd_result = self.exec_cmd("lvm fullreport --reportformat json --units B")
        if (report_cmd_result.has_error()):
            raise Exception("Command Error: lvm fullreport --reportformat json --units B")
        report_data_json = json.loads(report_cmd_result.get_result())["report"][0]
        for contener_data in report_data_json["vg"]:
            vg = LVM2_VolumeGroup()
            self.parse_object(contener_data,vg)
            self.__volumes[vg.get_value("vg_name")] = vg
            self.__objects.append(vg)
        for contener_data in report_data_json["pv"]:
            pv = LVM2_PhysicalVolume()
            self.parse_object(contener_data,pv)
            self.__volumes[pv.get_value("pv_name")] = pv
            self.__objects.append(pv)
        for contener_data in report_data_json["lv"]:
            lv = LVM2_LogicalVolume()
            self.parse_object(contener_data,lv)
            self.__volumes[lv.get_value("lv_name")] = lv
            self.__objects.append(lv)
        for contener_data in report_data_json["pvseg"]:
            pvseg = LVM2_PhysicalVolume_Segment()
            self.parse_object(contener_data,pvseg)
            self.__objects.append(pvseg)
        for contener_data in report_data_json["seg"]:
            seg = LVM2_Segment()
            self.parse_object(contener_data,seg)
            self.__objects.append(seg)
    
    def parse_object(self, data, lvm2_obj=JsonDataContener()):
        for key, value in data.items():
            lvm2_obj.set_value(key, value)
        
    def exec_cmd(self, cmd):
        return LVM2_Commmand_Result(subprocess.run(cmd.split(' '),capture_output=True))
    
    def get_all(self):
        return self.__objects
    
    def output_data(self, path="data.json"):
        json_data = {}
        for obj in self.__objects:
            name = obj.__class__.__name__
            if (name not in json_data):
                json_data[name] = []
            json_data[name].append(obj.get_all_values())
        with open(path, "w") as outfile:
            outfile.write(json.dumps(json_data, sort_keys=True, indent=4))

# if (__name__ == "__main__"):
    # lvm2 = LVM2()
    # lvm2.output_data("py-report.json")
