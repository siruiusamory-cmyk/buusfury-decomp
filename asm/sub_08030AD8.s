	CODE16
|sub_08030AD8|
|unk_08030AD8|
		CMP r4, #5
		BLT      |loc_08030AE0|
		STR r1, [r0, #0xc]
		B        |loc_08030AD4|
|loc_08030AE0|
		LDR r0, [pc, #0x34]
		LDRB r4, [r0, r4]
|loc_08030AE4|
|unk_08030AE4|
		MOV r2, #0x40
		MOV r1, #0x40
		ADD r6, sp, #4
		ADD r0, r6, #0
		BL       |loc_0803F540|
		LDR r2, [pc, #0x24]
		LSL r1, r4, #2
		ADD r2, #8
		ADD r1, r1, r2
		LDR r0, [sp, #0x28]
		LDR r1, [r1, #4]
		BL       |inc_0x049120_0x055620|
		LDRH r0, [r5, #0x16]
		LDR r1, [pc, #0x18]
		LSL r0, r0, #5
		ADD r1, r0, r1
		ADD r0, r6, #0
		BL       |inc_0x03d784_0x041118| + 0x2234
		MOV r1, #0
		ADD r0, r6, #0
	INCBIN  baserom.gba_0x30b12_0x30b14.extracted
|sub_08030B14|
|unk_08030B14|
	INCBIN	baserom.gba_0x30b14_0x30b18.extracted
	STRH     r4, [r7, #0xe]
	LSR      r5, r6, #1
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
|unk_08030B20|
	MOV      r0, #1
	BX       lr
|unk_08030B24|
	LDR      r1, [r0, #0x58]
	MOV      r3, #0x10
	SUB      r1, #1
	ADD      r2, r1, #0
	STR      r1, [r0, #0x58]
	LDR      r1, [pc, #0x3c4]
	STRB     r2, [r1, #2]
	LDR      r2, [r0, #0x58]
	SUB      r2, r3, r2
	STRB     r2, [r1, #3]
	LDR      r0, [r0, #0x58]
	MOV      r1, #1
	CMP      r0, #0
	BEQ      |loc_08030B42|
	MOV      r1, #0
|loc_08030B42|
	ADD      r0, r1, #0
	BX       lr
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030B5A|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x3a4]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030B5A|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030B66|
	LDR      r0, [pc, #0x398]
	STR      r0, [r4, #0x60]
	POP      {r4, pc}
|loc_08030B66|
	LDR      r0, [pc, #0x398]
	STR      r0, [r4, #0x60]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r5, [pc, #0x388]
	LDR      r2, [r0, #0x10]
	ADD      r4, r0, #0
	LDR      r1, [r5]
	LDR      r0, [pc, #0x38c]
	CMP      r2, #0
	LDRH     r1, [r1, #4]
	BEQ      |loc_08030BA4|
	LSL      r3, r1, #0x19
	LSR      r3, r3, #0x1f
	BEQ      |loc_08030B90|
	LDR      r3, [r0]
	SUB      r3, #1
	STR      r3, [r0]
	BPL      |loc_08030B90|
	SUB      r3, r2, #1
	STR      r3, [r0]
|loc_08030B90|
	LSL      r3, r1, #0x18
	LSR      r3, r3, #0x1f
	BEQ      |loc_08030BA4|
	LDR      r3, [r0]
	ADD      r3, #1
	STR      r3, [r0]
	CMP      r2, r3
	BGT      |loc_08030BA4|
	MOV      r2, #0
	STR      r2, [r0]
|loc_08030BA4|
	LSL      r1, r1, #0x1e
	LSR      r1, r1, #0x1f
	LDR      r6, [pc, #0x350]
	LDR      r7, [pc, #0x354]
	BEQ      |sub_08030BCE|
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0]
	LDR      r0, [r4, #0x54]
	CMP      r0, #0
	BEQ      |loc_08030BC2|
	ADD      r1, r0, #0
	LDR      r0, [r5, #4]
	BL       |inc_0x0158_0x143f2| + 0x117ec
|loc_08030BC2|
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |sub_08030BCC|
	STR      r6, [r4, #0x60]
	B        |sub_08030BCE|
