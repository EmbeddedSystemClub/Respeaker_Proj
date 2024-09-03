import usb
dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
if dev is None:
    print("장치를 찾을 수 없습니다.")
else:
    print("Found")