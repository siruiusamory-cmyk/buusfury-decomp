	CODE16
|sub_0804EDB2|
	LSL      r0, r0, #0
	LSR      r0, r2, #0x1e
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x18]
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r1, [r1, #0x2c]
	LDR      r2, [r2, #4]
	LDR      r0, [r0, #0xc]
	SUB      r1, r2, r1
	CMP      r1, r0
	BLE      |sub_0804EDCE|
	MOV      r0, #1
	BX       lr
