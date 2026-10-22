	CODE16
|sub_0801906E|
	LSR      r4, r0, #0x20
	STR      r3, [sp, #0x30]
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x1b8]
	ADD      r6, r1, #0
	STR      r0, [r5]
	LDR      r0, [r5, #4]
	MOV      r4, #0
	CMP      r0, #0
	BLE      |loc_0801909E|
|loc_08019086|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #8]
	LDR      r1, [r0]
	LDR      r2, [r1, #0xc]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDR      r0, [r5, #4]
	ADD      r4, #1
	CMP      r0, r4
	BGT      |loc_08019086|
|loc_0801909E|
	CMP      r6, #0
	BEQ      |loc_080190A8|
	ADD      r0, r5, #0
	BL       |GBARam_Free|
|loc_080190A8|
	POP      {r4, r5, r6, pc}
