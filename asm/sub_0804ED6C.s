	CODE16
|sub_0804ED6C|
	PUSH     {r3, lr}
	LDR      r0, [r0, #0xc]
	BL       |inc_0x03d784_0x041118| + 0x235a
	POP      {r3, pc}
	LSL      r0, r0, #0
	MOV      r3, #1
	LSL      r3, r3, #9
	LDR      r2, [pc, #0x14]
	ADD      r1, r1, r3
	LDR      r1, [r1, #0x10]
	LDR      r2, [r2, #4]
	LDR      r0, [r0, #0xc]
	SUB      r1, r2, r1
	CMP      r1, r0
	BLE      |sub_0804ED90|
	MOV      r0, #1
	BX       lr
