	CODE16
|sub_080117EE|
	LSL      r0, r4, #2
	ADD      r0, r0, r5
	LDR      r0, [r0, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x14]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	SUB      r4, #1
	BPL      |sub_080117EE|
|loc_08011802|
	MOV      r0, #0
	STR      r0, [r5]
|loc_08011806|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
	LSL      r0, r0, #0
	CMP      r0, #0x24
	LSR      r7, r0, #0x20
	LSL      r4, r2, #0x1a
	LSL      r0, r0, #0
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
