	CODE16
|sub_0800E0F4|
	PUSH     {r4, r5, r6, lr}
	ADD      r4, r0, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r0, #0
	ADD      r1, #0x16
	MOV      r3, #0
	LDRSH    r2, [r1, r3]
	CMP      r2, #0
	BEQ      |loc_0800E15A|
	MOV      r3, #0x64
	LDRH     r3, [r3, r0]
	LDR      r2, [r4, #8]
	ADD      r2, r2, r3
	STR      r2, [r4, #8]
	LSR      r3, r2, #8
	BEQ      |loc_0800E15A|
	ASR      r2, r2, #8
	MOV      r3, #0
	LDRSH    r5, [r1, r3]
	ADD      r5, r5, r2
	MOV      r3, #2
	LDRSH    r6, [r1, r3]
	CMP      r5, r6
	BLE      |loc_0800E136|
	LDRH     r2, [r1, #2]
	STRH     r2, [r1]
	B        |loc_0800E148|
|loc_0800E136|
	LDRH     r3, [r1]
	ADD      r2, r3, r2
	LSL      r2, r2, #0x10
	ASR      r2, r2, #0x10
|loc_0800E13E|
	STRH     r2, [r1]
	MOV      r3, #0
	LDRSH    r5, [r1, r3]
	CMP      r5, r2
	BNE      |loc_0800E13E|
|loc_0800E148|
	LDR      r1, [r4, #8]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	STR      r1, [r4, #8]
	LDRB     r1, [r0, #0x13]
	LSL      r1, r1, #0x1f
	BPL      |loc_0800E15A|
	BL       |loc_08013C66|
|loc_0800E15A|
	POP      {r4, r5, r6, pc}
