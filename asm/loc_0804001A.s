	CODE16
|loc_0804001A|
	PUSH     {r4, r5}
	MOV      r4, #0
	SUB      r2, #1
	BCC      |loc_08040042|
|loc_08040022|
	LDRH     r3, [r1]
	ADD      r1, #2
	CMP      r3, #0xff
	BCC      |loc_08040030|
	LDR      r3, [r0, #4]
	ADD      r3, #1
	B        |loc_0804003C|
|loc_08040030|
	LDR      r5, [r0]
	LSL      r3, r3, #1
	LDRH     r3, [r5, r3]
	LSL      r3, r3, #1
	LDRH     r3, [r5, r3]
	ADD      r3, #1
|loc_0804003C|
	ADD      r4, r3, r4
	SUB      r2, #1
	BCS      |loc_08040022|
|loc_08040042|
	ADD      r0, r4, #0
	POP      {r4, r5}
	BX       lr
