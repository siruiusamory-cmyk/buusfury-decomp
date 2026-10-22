	CODE16
|Object_Destroy7|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x21c]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r0, [r4, #0x38]
	BL       |GBARam_Free|
	LDR      r0, [pc, #0x218]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08013F0A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08013F0A|
	POP      {r3, r4, r5, pc}
	PUSH     {r4}
	STR      r1, [r0, #0x24]
	STR      r2, [r0, #0x28]
	LDR      r4, [r0, #0x20]
	LDRB     r3, [r4, #4]
	LDRB     r4, [r4, #5]
	ADD      r1, r1, r3
	STR      r1, [r0, #0x2c]
	ADD      r1, r2, r4
	STR      r1, [r0, #0x30]
	POP      {r4}
	BX       lr
	ADD      r2, r0, #0
	ADD      r0, r1, #0
	PUSH     {r4, lr}
	LDR      r1, [r2, #0x10]
	CMP      r1, #0
	BEQ      |loc_08013F56|
	LDR      r3, [r2, #8]
	MOV      r1, #2
	CMP      r3, #0
	BEQ      |loc_08013F48|
	LDR      r3, [r2, #4]
	MOV      r1, #1
	ADD      r3, #0xff
	ADD      r3, #1
	LDR      r3, [r3, #8]
	CMP      r3, r2
	BEQ      |loc_08013F48|
	MOV      r1, #0
|loc_08013F48|
	LDR      r3, [r2, #0x34]
	LDR      r4, [r2, #0x38]
	MUL      r3, r1
	ADD      r1, r4, r3
	ADD      r2, #0x24
	BL       |inc_0x03d784_0x041118| + 0x219e
|loc_08013F56|
	POP      {r4, pc}
	PUSH     {r3, lr}
	ADD      r1, r0, #0
	LDR      r0, [r0, #8]
	CMP      r0, #0
	BEQ      |loc_08013F7A|
	LDR      r2, [r1, #4]
	MOV      r0, #0
	ADD      r2, #0xff
	ADD      r2, #1
	STR      r0, [r2, #0x10]
	LDR      r0, [r1, #4]
	LDR      r2, [r0]
	LDR      r3, [r2, #0x20]
	ADD      r3, r3, r2
	LDR      r2, [r1, #0x14]
	BL       |inc_0x046118_0x049114| + 0x98e
|loc_08013F7A|
	POP      {r3, pc}
|sub_08013F7C|
|unk_08013F7C|
		PUSH {r3, r4, r5, lr}
		LDR r1, [r0, #4]
		LDR r3, [pc, #0x190]
		ADD r1, #0xff
		ADD r1, #1
		ADD r4, r0, #0
		LDR r0, [r0, #0x20]
		LDR r2, [r1, #8]
		MOV r5, #0
		SUB r3, #8
		CMP r2, r4
		LDRH r0, [r0, #2]
		BNE      |sub_08014000|
		LDR r2, [r3]
		LDRH r2, [r2, #6]
		AND r2, r0
		BEQ      |inc_0x0158_0x143f2| + 0x13e6c
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e5a
		LDR r0, [r4, #8]
		CMP r0, #0
		BEQ      |loc_08013FFC|
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		STR r5, [r0, #0x10]
		LDR r0, [r4, #4]
		LDR r1, [r0]
		LDR r2, [r1, #0x20]
		ADD r3, r2, r1
		LDR r2, [r4, #0x14]
		ADD r1, r4, #0
	INCBIN  baserom.gba_0x13fbe_0x13fc0.extracted
|sub_08013FC0|
|unk_08013FC0|
	INCBIN	baserom.gba_0x13fc0_0x13fc4.extracted
	LDR      r0, [r4, #0xc]
	CMP      r0, #0
	BEQ      |loc_08013FFC|
	LDR      r0, [r4, #0x18]
	SUB      r0, #1
	STR      r0, [r4, #0x18]
	BNE      |loc_08013FFC|
	LDR      r0, [r4, #0x1c]
	CMP      r0, #4
	BLE      |loc_08013FE0|
	LSR      r2, r0, #0x1f
	ADD      r0, r2, r0
	ASR      r0, r0, #1
	STR      r0, [r4, #0x1c]
|loc_08013FE0|
	LDR      r0, [r4, #0x1c]
	STR      r0, [r4, #0x18]
	LDR      r0, [r4, #8]
	CMP      r0, #0
	BEQ      |loc_08013FFC|
	STR      r5, [r1, #0x10]
	LDR      r0, [r4, #4]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x20]
	ADD      r3, r2, r1
	LDR      r2, [r4, #0x14]
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98e
|loc_08013FFC|
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
|sub_08014000|
|unk_08014000|
		LDR r1, [r3]
		LDRH r1, [r1, #4]
		AND r1, r0
		BEQ      |loc_08014024|
		LDR r0, [r4, #8]
		CMP r0, #0
		BNE      |loc_08014010|
		B        |inc_0x0158_0x143f2| + 0x13ea6
|loc_08014010|
		MOV r0, #0x10
		STR r0, [r4, #0x18]
		STR r0, [r4, #0x1c]
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x5e50
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #1
		STR r5, [r0, #0x10]
|loc_08014024|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x13ea6
