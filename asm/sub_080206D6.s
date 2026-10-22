	CODE16
|sub_080206D6|
|unk_080206D6|
		LDR r0, [pc, #0x3a0]
		LDR r6, [pc, #0x3a0]
		STR r0, [r4]
		MOV r0, #3
		LSL r0, r0, #8
		STRH r0, [r4, #0xe]
		ADD r1, r0, #0
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
		ADD r3, r0, #1
		BNE      |loc_08020702|
		MOV r1, #3
		LSL r1, r1, #8
		LDR r0, [r6, #4]
		BL       |sub_08011732|
		MOV r1, #3
		LSL r1, r1, #8
		LDR r0, [r6, #4]
		BL       |loc_0801124C|
|loc_08020702|
		STRH r0, [r4, #0xc]
		LDR r0, [pc, #0x378]
		STR r0, [r4]
		LDMIA r5!, {r1, r2}
		STR r1, [r4, #0x20]
		STR r2, [r4, #0x24]
		LDR r0, [sp, #0xc]
		SUB r5, #8
		STRB r0, [r4, #8]
		LDR r0, [r5, #4]
		MOV r5, #0
		STR r0, [r4, #4]
		LDR r0, [sp, #0x10]
		MOV r1, #8
		STR r0, [r4, #0x50]
		STR r5, [r4, #0x18]
		STRB r5, [r4, #0x11]
		STRB r5, [r4, #0x10]
		STR r1, [r4, #0x38]
		STR r7, [r4, #0x40]
		LDRB r0, [r0, #0x10]
		LDR r2, [pc, #0x358]
		LSR r0, r0, #1
		LDRB r0, [r7, r0]
		STRB r0, [r4, #0x12]
		LDR r1, [r7, #8]
		LDR r0, [pc, #0x34c]
		STR r1, [r4, #0x4c]
		STR r1, [r4, #0x48]
		STR r1, [r4, #0x44]
		LDR r0, [r0, #4]
		STR r0, [r4, #0x14]
		MVN r0, r5
		STR r0, [r4, #0x1c]
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r2
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		ADD r3, r5, #0
		LDR r5, [pc, #0x338]
		LDR r0, [r6]
		MOV r2, #0x40
		ADD r0, r0, r5
		LDR r1, [pc, #0x32c]
		BL       |inc_0x03d784_0x041118| + 0xbf4
		ADD r0, r4, #0
		DCW     0xE7B4
		PUSH {r0, r1, r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r0, [pc, #0x310]
		SUB sp, #4
		STR r0, [r4]
		LDR r7, [pc, #0x308]
		LDRB r0, [r4, #0x10]
		LDR r2, [r7]
		LDR r6, [pc, #0x310]
		LDR r1, [pc, #0x314]
		SUB r6, #0x24
		ADD r5, r2, r1
		CMP r0, #1
		DCW     0xD30E
		ADD r1, r6, #0
		ADD r1, #0xff
		ADD r1, #0x81
		ADD r0, r5, #0
		BL       |inc_0x03d784_0x041118| + 0xb7e
		ADD r1, r6, #0
		ADD r1, #0xff
		ADD r1, #0x8d
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r5, #0
	INCBIN  baserom.gba_0x2079c_0x2079e.extracted
|sub_0802079E|
|unk_0802079E|
	INCBIN	baserom.gba_0x2079e_0x207a2.extracted
	ADD      r1, r6, #0
	ADD      r1, #0x24
	ADD      r0, r5, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	LDR      r0, [pc, #0x2c8]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x2e0]
	CMP      r1, r0
	BEQ      |loc_080207BE|
	LDR      r0, [r7, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080207BE|
	LDR      r0, [pc, #0x2d8]
	STR      r0, [r4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_080207CE|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080207CE|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, lr}
	STR      r1, [r0, #0x3c]
	LDR      r3, [r2]
	LDR      r2, [r2, #4]
	LDR      r5, [pc, #0x2b0]
	STR      r2, [r0, #0x24]
	STR      r3, [r0, #0x20]
	LDR      r1, [r0, #0x40]
	SUB      r5, #0x24
	LDR      r2, [r1, #0xc]
	LDR      r1, [r0, #0x3c]
	LSL      r3, r1, #1
	ADD      r3, r3, r1
	LSL      r3, r3, #6
	ADD      r2, r2, r3
	STR      r2, [r0, #0x4c]
	STR      r2, [r0, #0x48]
	LDR      r2, [pc, #0x2a4]
	LSL      r1, r1, #3
	ADD      r1, r1, r2
	LDR      r2, [r1]
	LDR      r1, [r1, #4]
	STR      r1, [r0, #0x34]
	STR      r2, [r0, #0x30]
	MOV      r1, #1
	STRB     r1, [r0, #0x10]
	LDR      r0, [pc, #0x274]
	LDR      r2, [pc, #0x284]
	LDR      r0, [r0]
	ADD      r1, r5, #0
	ADD      r1, #0x24
	ADD      r0, r0, r2
	ADD      r4, r0, #0
	BL       |inc_0x03d784_0x041118| + 0xb7e
	ADD      r1, r5, #0
	ADD      r1, #0xff
	ADD      r1, #0x81
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0xbf4
	POP      {r3, r4, r5, pc}
	PUSH     {r3, lr}
	LDRB     r1, [r0, #0x10]
	CMP      r1, #0
	BEQ      |sub_08020840|
	CMP      r1, #1
	BNE      |loc_0802083E|
	MOV      r1, #2
	STRB     r1, [r0, #0x10]
	SUB      r1, #3
	STR      r1, [r0, #0x1c]
|loc_0802083E|
	POP      {r3, pc}
