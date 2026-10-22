	CODE16
|sub_0803AF58|
	PUSH     {r4, r5, r6}
	LDR      r2, [r0, #0x14]
	LDR      r3, [r0, #0x18]
	LDR      r4, [r1]
	ADD      r5, r2, #0
	ADD      r6, r3, #0
	CMP      r2, r4
	BGE      |loc_0803AF6A|
	ADD      r2, r4, #0
|loc_0803AF6A|
	LDR      r4, [r1, #8]
	CMP      r2, r4
	BLE      |loc_0803AF72|
	ADD      r2, r4, #0
|loc_0803AF72|
	LDR      r4, [r1, #4]
	CMP      r3, r4
	BGE      |loc_0803AF7A|
	ADD      r3, r4, #0
|loc_0803AF7A|
	LDR      r1, [r1, #0xc]
	CMP      r3, r1
	BLE      |loc_0803AF82|
	ADD      r3, r1, #0
|loc_0803AF82|
	SUB      r1, r5, r2
	ADD      r2, r1, #0
	MUL      r1, r2
	SUB      r2, r6, r3
	ADD      r3, r2, #0
	MUL      r2, r3
	LDR      r0, [r0, #0x10]
|loc_0803AF90|
	ADD      r1, r1, r2
	ADD      r2, r0, #0
	MUL      r2, r0
	ASR      r0, r2, #0x10
	CMP      r0, r1
	BLE      |sub_0803AFA2|
	MOV      r0, #1
	POP      {r4, r5, r6}
	BX       lr
