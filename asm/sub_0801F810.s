	CODE16
|sub_0801F810|
	PUSH     {r3, r4, r5, lr}
	ADD      r3, r0, #0
	LDRB     r2, [r3, #4]
	ADD      r0, r1, #0
	LDR      r1, [pc, #0x31c]
	CMP      r2, #0
	BEQ      |sub_0801F836|
	CMP      r2, #1
	BEQ      |loc_0801F84E|
	CMP      r2, #2
	BNE      |loc_0801F834|
	MOV      r2, #0xff
	ADD      r2, #0x49
	LDR      r2, [r1, r2]
	LDR      r3, [r3]
	ADD      r1, pc, #0x30C
	BL       |inc_0x03d784_0x041118| + 0x512
|loc_0801F834|
	POP      {r3, r4, r5, pc}
