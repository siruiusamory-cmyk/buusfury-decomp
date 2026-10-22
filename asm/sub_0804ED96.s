	CODE16
|sub_0804ED96|
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x18]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r1, [r1, #0x28]
	LDR      r2, [r2, #4]
	LDR      r0, [r0, #0xc]
	SUB      r1, r2, r1
	CMP      r1, r0
	BLE      |sub_0804EDAE|
	MOV      r0, #1
	BX       lr
