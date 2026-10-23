	CODE16
|sub_08035E8C|
	PUSH     {r4, r5, lr}
	SUB      sp, #0x14
	ADD      r5, sp, #4
	ADD      r4, r1, #0
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xfca2
	LDR      r0, [pc, #0x64]
	ADD      r2, r5, #0
	MOV      r1, #0x21
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x11b18
	CMP      r0, #0
	BNE      |sub_08035EAE|
	ADD      sp, #0x14
	POP      {r4, r5, pc}
