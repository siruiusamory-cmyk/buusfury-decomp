	CODE16
|sub_08019BCC|
	LDR      r0, [r0, #0x30]
	LDR      r1, [r1]
	CMP      r0, r1
	BLE      |sub_08019BD8|
	MOV      r0, #1
	BX       lr
