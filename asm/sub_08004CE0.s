	CODE16
|sub_08004CE0|
	PUSH     {r4, r5}
	LDR      r4, [r0, #0xc]
	MOV      r1, #0
	CMP      r4, #0
	BLE      |loc_08004D34|
	ADD      r2, r0, #0
	LDR      r5, [r0, #0x7c]
	ADD      r2, #0xc
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	LDR      r3, [r3, #0xc]
	CMP      r3, r5
	BNE      |loc_08004D2E|
	ADD      r1, #1
	CMP      r4, r1
	BLE      |loc_08004D2A|
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #2
	ADD      r3, r3, r2
	LDR      r3, [r3, #8]
	CMP      r3, #0
	BEQ      |sub_08004D24|
	LSL      r3, r1, #1
	ADD      r1, r3, r1
	LSL      r1, r1, #2
	ADD      r1, r1, r2
	LDR      r1, [r1, #0xc]
	STR      r1, [r0, #0x7c]
	MOV      r0, #1
	POP      {r4, r5}
	BX       lr
