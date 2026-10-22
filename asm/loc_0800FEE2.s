	CODE16
|loc_0800FEE2|
	PUSH     {r4, r5, r6}
	ADD      r5, r0, #0
	LDR      r1, [pc, #0x124]
	ADD      r5, #0xff
	ADD      r5, #0x81
	LDR      r3, [pc, #0x11c]
	LDR      r1, [r1]
	ADD      r2, r5, #0
	LDR      r3, [r3]
	ADD      r4, r1, #0
	ADD      r2, #0x20
	LDR      r6, [r5, #0x20]
	ADD      r3, #0x94
	LDR      r1, [r2]
	ADD      r4, #0x94
	CMP      r6, #0
	LDR      r3, [r3]
	BGE      |loc_0800FF0E|
	LSL      r3, r3, #8
	ADD      r1, r1, r3
	STR      r1, [r2]
	B        |loc_0800FF1A|
|loc_0800FF0E|
	ASR      r6, r1, #8
	CMP      r6, r3
	BLT      |loc_0800FF1A|
	LSL      r3, r3, #8
	SUB      r1, r1, r3
	STR      r1, [r2]
|loc_0800FF1A|
	ADD      r0, #0xff
	LDR      r1, [r5, #0x24]
	ADD      r0, #0xa5
	CMP      r1, #0
	BGE      |sub_0800FF32|
	LDR      r1, [r4, #4]
	LDR      r2, [r0]
	LSL      r1, r1, #8
	ADD      r1, r2, r1
	STR      r1, [r0]
	POP      {r4, r5, r6}
	BX       lr
