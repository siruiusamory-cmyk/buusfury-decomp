	CODE16
|loc_08013E38|
	PUSH     {r4, r5}
	LDR      r5, [pc, #0x24]
	MOV      r2, #0
	LSL      r3, r2, #4
	ADD      r3, r3, r5
	LDRB     r4, [r3]
	CMP      r4, r0
	BNE      |sub_08013E54|
	LDRB     r4, [r3, #1]
	CMP      r4, r1
	BNE      |sub_08013E54|
	ADD      r0, r3, #0
	POP      {r4, r5}
	BX       lr
