	CODE16
|sub_0803983E|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	DCW      0xf5a5,0x0803
	ADD      r7, sp, #0x110
	LSR      r7, r6, #1
	POP      {r3, r5, r6, r7}
	LSR      r6, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08039874|
	LDR      r1, [pc, #0x2c]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_08039874|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	MOV      r4, #1
	LSL      r4, r4, #9
	LDR      r3, [pc, #0x20]
	ADD      r4, r1, r4
	LDR      r4, [r4, #0x10]
	LDR      r3, [r3, #4]
	SUB      r3, r3, r4
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BLE      |sub_08039896|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
