	CODE16
|sub_0802CD12|
	LSR      r5, r6, #1
	LSR      r4, r4, #0x1e
	LSL      r0, r0, #0
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	STMIA    r2!, {r2, r3, r4}
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	BEQ      |loc_0802CD40|
	MOV      r0, #0xb0
	LDR      r5, [r4, #0x58]
	BL       |inc_0x0158_0x143f2|
	CMP      r5, r0
	BNE      |sub_0802CD42|
	MOV      r0, #0xaf
	BL       |inc_0x0158_0x143f2|
	ADD      r1, r0, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xeca0
|loc_0802CD40|
	POP      {r3, r4, r5, pc}
