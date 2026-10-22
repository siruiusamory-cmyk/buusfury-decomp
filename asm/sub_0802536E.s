	CODE16
|sub_0802536E|
	MOV      r1, #0xb
	LSL      r1, r1, #8
	ADD      r6, r4, r1
	LDR      r1, [r6, #0x14]
	ADD      r0, r4, #0
	ADD      r0, #0x10
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	LDR      r1, [pc, #0x334]
	LSL      r0, r0, #4
	ADD      r5, r0, r1
	MOV      r0, #0x68
	STR      r0, [sp, #8]
	MOV      r0, #0x38
	STR      r0, [sp, #0xc]
	LDR      r0, [pc, #0x32c]
	STR      r7, [sp]
	STR      r7, [sp, #4]
	LDR      r1, [r0, #0x10]
	ADD      r0, sp, #0x10
	MOV      r2, sp
	BL       |inc_0x03d784_0x041118| + 0x2f4
	LDRH     r0, [r5, #2]
	LDR      r1, [pc, #0x31c]
	LSL      r0, r0, #2
	LDR      r0, [r1, r0]
	MOV      r5, #0
	STR      r0, [sp, #4]
|loc_080253AA|
	MOV      r3, sp
	MOV      r2, #0x68
	ADD      r0, sp, #0x10
	LDR      r1, [sp, #4]
	BL       |inc_0x03d784_0x041118| + 0x6e6
	LDR      r0, [sp, #0xc]
	ADD      r5, #1
	CMP      r0, #0
	BEQ      |loc_080253AA|
	LSL      r0, r5, #4
	SUB      r0, #0x38
	STR      r0, [r6, #0x1c]
	BPL      |loc_080253C8|
	STR      r7, [r6, #0x1c]
|loc_080253C8|
	STR      r7, [r6, #0x18]
	STRB     r7, [r4, #0xc]
	MOV      r0, #1
	STRB     r0, [r4, #0xe]
	ADD      r0, r4, #0
	BL       |loc_08025056|
	STRB     r7, [r4, #5]
	STRB     r7, [r4, #6]
	STR      r7, [r4, #8]
	MOV      r0, #0
	ADD      sp, #0x34
	POP      {r4, r5, r6, r7, pc}
|sub_080253E2|
|unk_080253E2|
		ADD r0, r4, #0
		BL       |inc_0x1c3f2_0x2ab4c| + 0x8812
		DCW     0xE7F9
