	CODE16
|sub_0803FFE8|
	PUSH     {r4}
	LDRH     r3, [r1]
	MOV      r2, #0
	CMP      r3, #0
	BEQ      |loc_08040014|
|loc_0803FFF2|
	LDRH     r3, [r1]
	ADD      r1, #2
	CMP      r3, #0xff
	BCC      |loc_08040000|
	LDR      r3, [r0, #4]
	ADD      r3, #1
	B        |loc_0804000C|
|loc_08040000|
	LDR      r4, [r0]
	LSL      r3, r3, #1
	LDRH     r3, [r4, r3]
	LSL      r3, r3, #1
	LDRH     r3, [r4, r3]
	ADD      r3, #1
|loc_0804000C|
	ADD      r2, r3, r2
	LDRH     r3, [r1]
	CMP      r3, #0
	BNE      |loc_0803FFF2|
|loc_08040014|
	ADD      r0, r2, #0
	POP      {r4}
	BX       lr
