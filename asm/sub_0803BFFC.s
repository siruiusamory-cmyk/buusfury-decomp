	CODE16
|sub_0803BFFC|
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r1, #0x58]
	ADD      r4, r1, #0
	ADD      r0, #0x3c
	LDR      r0, [r0, #0x54]
	LDR      r1, [r1, #0x50]
	CMP      r0, r1
	BEQ      |loc_0803C022|
	MOV      r1, #0xf
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0x98]
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	MOV      r0, #0x24
	STRB     r0, [r4, #8]
|loc_0803C022|
	LDR      r0, [r5, #0xc]
	SUB      r1, r0, #1
	STR      r1, [r5, #0xc]
	CMP      r0, #0
	BNE      |sub_0803C030|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
