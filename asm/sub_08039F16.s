	CODE16
|sub_08039F16|
	SUB      r6, #0x22
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	CMP      r0, #0
	BNE      |loc_08039F2A|
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08039F4C|
|loc_08039F2A|
	LDR      r1, [pc, #0x158]
	MOV      r3, #4
	STR      r1, [r0]
	LDRSH    r1, [r4, r3]
	MOV      r3, #6
	LDRSH    r2, [r4, r3]
	STR      r1, [r0, #4]
	MOV      r3, #8
	STR      r2, [r0, #8]
	LDRSH    r1, [r4, r3]
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x81
	STR      r1, [r0, #0xc]
	ADD      r1, r2, #0
	MUL      r1, r2
	STR      r1, [r0, #0x10]
|loc_08039F4C|
	POP      {r4, pc}
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [pc, #0x134]
	ADD      r7, r1, #0
	LDR      r0, [r0]
	SUB      sp, #0x14
	CMP      r0, #0
	BNE      |sub_08039F62|
	ADD      sp, #0x14
	POP      {r4, r5, r6, r7, pc}
