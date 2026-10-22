	CODE16
|sub_0802AA80|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0802AAA0|
	LDR      r1, [pc, #0x30]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_0802AAA0|
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	MOV      r4, #0xff
	LDR      r3, [pc, #0x20]
	ADD      r4, #0xed
	LDR      r4, [r4, r1]
	LDR      r3, [r3, #4]
	SUB      r3, r3, r4
	LDR      r4, [r0, #0xc]
	CMP      r3, r4
	BLE      |sub_0802AAC0|
	LDR      r0, [r0, #0x10]
	LDR      r3, [r0, #4]
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
