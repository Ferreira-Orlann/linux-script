# Minimal LVM2 Parser

### Example
```python
parser = LVM2_Parser()
parser.scan_all()
print(parser)
```
### Output on blank CentOS Stream 9
```
Type: LogicalVolume | Name: b'root' | Size: b'18249416704' Bytes | UUID: b'VOdG30-2H0J-Tr2X-sErI-i4XI-hJ6H-RlqkCw' | Volume Group's Name: b'cs' | IsMounted: True | Mount Point: b'/'
Type: LogicalVolume | Name: b'swap' | Size: b'2147483648' Bytes | UUID: b'HAUeA3-NGoO-O1qY-C1i0-uHhw-nYEo-Q7j7oJ' | Volume Group's Name: b'cs' | IsMounted: False | Mount Point: b''
Type: PhysicalVolume | Name: b'/dev/sda2' | Size: b'20396900352' Bytes | UUID: b'Ru4jiA-OHjK-BmFh-Tnf1-f7hn-YDE0-RQJ4RW' | Volume Group's Name: b'cs'
Type: VolumeGroup | Name: b'cs' | Size: b'20396900352' Bytes | UUID: b'Lsh5kw-YM14-rk3u-sO2w-J6ox-S0ZM-EVqj0W' | Logical Volume(s) (2): b'root', b'swap',  | Physical Volume(s) (1): b'/dev/sda2', 
```
