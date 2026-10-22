	CODE16
|sub_0801A2AA|
	ADD      r0, sp, #0x24
	LDR      r4, [r0]
	ADD      r0, sp, #0xc
	ADD      r1, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xfcdc
	LDR      r0, [sp, #0xc]
	LDR      r2, [sp, #0x14]
	LDR      r3, [sp, #0x18]
	ADD      r2, r0, r2
	LDR      r0, [sp, #0x10]
	STR      r2, [sp, #4]
	ADD      r0, r0, r3
	STR      r0, [sp, #8]
	ASR      r0, r0, #1
	ASR      r2, r2, #1
	STR      r2, [sp, #4]
	STR      r2, [sp, #0x1c]
	ADD      r3, r4, #0
	ADD      r6, sp, #0x2c
	ADD      r2, r6, #0
	STR      r0, [sp, #8]
	STR      r0, [sp, #0x20]
	MOV      r0, #0
	ADD      r1, sp, #0x1c
	BL       |inc_0x1c3f2_0x2ab4c| + 0x5ce6
	BL       |inc_0x03d784_0x041118| + 0x11c
	LDR      r0, [sp, #0x2c]
	CMP      r0, #0
	BEQ      |sub_0801A2FE|
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |loc_0801ba0e| + 0xa2
	ADD      r1, r0, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	ADD      sp, #0x60
	POP      {r4, r5, r6, pc}
