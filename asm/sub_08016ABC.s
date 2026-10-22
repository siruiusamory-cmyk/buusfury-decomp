	CODE16
|sub_08016ABC|
	LSL      r0, r1, #0
	LSL      r5, r2, #1
	LSL      r1, r5, #2
	LSL      r4, r7, #2
	LSL      r6, r1, #3
	LSL      r6, r1, #3
	LSL      r3, r4, #1
	LSL      r1, r1, #2
	LDR      r0, [pc, #0x1fc]
	MOV      r7, #0
	LDR      r5, [pc, #0x200]
	LDR      r0, [r0, #4]
	ADD      r3, r7, #0
	MOV      r2, #0x40
	ADD      r0, r0, r5
	LDR      r1, [pc, #0x1f4]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #0x35
	ADD      r5, r6, #0
	SUB      r5, #0x34
	LDR      r0, [r5, #0x1c]
	CMP      r0, #0
	BEQ      |loc_08016AF6|
	MOV      r0, #0xa1
	LSL      r0, r0, #2
	ADD      r6, r4, r0
|loc_08016AF6|
	LDR      r0, [r6]
	CMP      r0, #0
	BNE      |sub_08016AFE|
	POP      {r3, r4, r5, r6, r7, pc}
