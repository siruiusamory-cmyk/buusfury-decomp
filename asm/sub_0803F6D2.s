	CODE16
|sub_0803F6D2|
	LSL      r3, r1, #0x1f
	BPL      |loc_0803F6DA|
	LDRB     r3, [r4, #2]
	STRB     r3, [r2]
|loc_0803F6DA|
	LDR      r3, [r4, #0x28]
	LSR      r0, r0, #1
	LSR      r1, r1, #1
	ADD      r2, r3, r2
	ADD      r3, r0, #0
	ORR      r3, r1
	BNE      |loc_0803F6C8|
	MOV      r0, ip
	ADD      r0, #1
	LDR      r1, [sp, #0x10c]
	ADD      r7, #1
	CMP      r0, r1
	MOV      ip, r0
	BLT      |loc_0803F6A0|
	LDR      r0, [r6]
	ADD      r0, r0, r5
	ADD      r0, #1
	STR      r0, [r6]
	ADD      sp, #0x134
	POP      {r4, r5, r6, r7, pc}
|loc_0803F702|
	DCW      0x0000
	DCW      0x1d9d,0x0000,0xf445,0x0803
