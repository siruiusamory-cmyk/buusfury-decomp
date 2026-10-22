	CODE16
|sub_08019BBC|
	LDR      r0, [r0, #0x34]
	LDR      r1, [r1, #4]
	CMP      r0, r1
	BLE      |sub_08019BC8|
	MOV      r0, #1
	BX       lr
