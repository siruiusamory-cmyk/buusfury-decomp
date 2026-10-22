	CODE16
|sub_08008096|
	LSR      r7, r0, #0x20
	MOV      r0, #1
	LSL      r0, r0, #0x1a
	PUSH     {r4}
	LDRB     r0, [r0, #6]
	CMP      r0, #0x37
	BLT      |loc_080080BC|
	CMP      r0, #0xa0
	BGE      |loc_080080BC|
	LDR      r1, [pc, #0x3dc]
	ADD      r0, #1
	LDR      r1, [r1, #4]
	LSL      r0, r0, #4
	ADD      r1, #0x80
	LDR      r1, [r1, #0x28]
	LDR      r4, [pc, #0x3d4]
	ADD      r0, r1, r0
	LDMIA    r0!, {r0, r1, r2, r3}
	STMIA    r4!, {r0, r1, r2, r3}
|loc_080080BC|
	POP      {r4}
	BX       lr
