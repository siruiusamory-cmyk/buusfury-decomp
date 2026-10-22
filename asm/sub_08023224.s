	CODE16
|sub_08023224|
	LDR      r0, [pc, #0x280]
	LDR      r2, [pc, #0x27c]
	ADD      r1, r5, r0
	ADD      r7, r1, #0
	LDR      r0, [r6, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [sp, #4]
	LDR      r1, [r0]
	LDR      r0, [sp, #8]
	LDR      r2, [r0]
	ADD      r1, r2, r1
|loc_0802323C|
	STR      r1, [r0]
	LDR      r2, [r0]
	CMP      r2, r1
	BNE      |loc_0802323C|
	MOV      r0, #0
|loc_08023246|
	ADD      r2, r5, r0
	ADD      r2, #0xff
	LDR      r1, [r6, #0xc]
	ADD      r2, #0x41
	LDRB     r2, [r2, #1]
	ADD      r1, r1, r0
	LDRB     r3, [r1, #2]
	ADD      r2, r3, r2
	MOV      r3, #0xff
	ADD      r3, #1
	CMP      r2, r3
	BGE      |loc_08023262|
	STRB     r2, [r1, #2]
	B        |loc_08023266|
|loc_08023262|
	MOV      r2, #0xff
	STRB     r2, [r1, #2]
|loc_08023266|
	ADD      r0, #1
	CMP      r0, #0x53
	BLT      |loc_08023246|
	LDR      r0, [r4]
	MOV      r5, #0
	CMP      r0, #0
	BLE      |loc_08023288|
|loc_08023274|
	LSL      r0, r5, #2
	ADD      r0, r0, r4
	LDR      r1, [r0, #4]
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x42f0
	LDR      r0, [r4]
	ADD      r5, #1
	CMP      r0, r5
	BGT      |loc_08023274|
|loc_08023288|
	LDR      r2, [pc, #0x218]
	ADD      r0, r7, #0
	LDR      r1, [r6, #0xc]
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [pc, #0x218]
	LDR      r1, [r0]
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x489a
	LDR      r0, [r6, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x41a4
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
|sub_080232A6|
|unk_080232A6|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		LDR r7, [pc, #0x1d8]
		LDR r0, [pc, #0x204]
		ADD r4, r5, #0
		LDR r3, [r7]
		ADD r4, #0xff
		ADD r4, #1
		MOV r6, #0
		ADD r0, r3, r0
		CMP r2, #0
		LDR r1, [pc, #0x1f0]
		BEQ      |loc_0802336E|
		CMP r2, #1
		BEQ      |sub_080232FA|
		ADD r5, #0xff
		ADD r5, #0x41
		SUB r1, #0xc
		CMP r2, #4
		BEQ      |loc_080232E6|
		CMP r2, #5
		DCW     0xD174
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x1c]
		ADD r0, #1
		STR r0, [r4, #0x1c]
		MOV r0, #2
		STRB r0, [r5]
		DCW     0xE06A
|loc_080232E6|
		ADD r3, r6, #0
		MOV r2, #0x40
		BL       |inc_0x03d784_0x041118| + 0xbf4
		LDR r0, [r4, #0x1c]
		SUB r0, #1
		STR r0, [r4, #0x1c]
		MOV r0, #3
		STRB r0, [r5]
		DCW     0xE060
