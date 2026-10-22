	CODE16
|sub_0800953E|
	PUSH     {r0, r1, r2, r3, r4, r5, r6, r7, lr}
	ADD      r5, r1, #0
	MOV      r1, #0
	SUB      sp, #0xc
	STR      r1, [r0, #0xc]
	ADD      r4, r0, #0
	STR      r1, [r0, #0x40]
	ADD      r4, #0x80
	ADD      r6, r0, #0
	ADD      r0, #0x30
	STR      r5, [r4, #0xc]
	STMIA    r0!, {r1}
	STR      r1, [r0]
	LDR      r0, [r5, #0x3c]
	MOV      r7, #1
	STR      r0, [r4, #0x10]
	LDR      r0, [r4, #0x28]
	LSL      r7, r7, #0xd
	CMP      r0, #0
	BNE      |loc_0800956E|
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	STR      r0, [r4, #0x28]
|loc_0800956E|
	LDR      r0, [r4, #0x2c]
	CMP      r0, #0
	BNE      |loc_0800957C|
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	STR      r0, [r4, #0x2c]
|loc_0800957C|
	LDR      r0, [r4, #0x30]
	CMP      r0, #0
	BNE      |loc_0800958A|
	ADD      r0, r7, #0
	BL       |GBARam_Malloc|
	STR      r0, [r4, #0x30]
|loc_0800958A|
	LDRH     r0, [r5, #8]
	ADD      r1, r5, #0
	SUB      r0, #1
	STRH     r0, [r4, #0x1c]
	LDRH     r0, [r5, #0xa]
	SUB      r0, #1
	STRH     r0, [r4, #0x1e]
	LDRH     r0, [r5, #8]
	ADD      r0, #0xef
	STR      r0, [r4, #0x14]
	LDRH     r0, [r5, #0xa]
	ADD      r0, #0x9f
	STR      r0, [r4, #0x18]
	ADD      r0, r6, #0
	BL       |loc_08009420|
	LDR      r1, [r4, #0x28]
	LDR      r0, [r5, #0x34]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r1, [r4, #0x2c]
	LDR      r0, [r5, #0x38]
	BL       |inc_0x03d784_0x041118| + 0x1bc
	LDR      r0, [r4, #0x30]
	LDR      r1, [r4, #0x28]
	ADD      r2, r7, #0
	BL       |inc_0x049120_0x055620| + 0x18
	LDR      r0, [pc, #0x84]
	LDR      r0, [r0, #0x10]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4cc4
	ADD      r7, r6, #0
	LDR      r0, [r5, #0x3c]
	ADD      r7, #0xa0
	CMP      r0, #0
	BEQ      |loc_08009608|
	LDR      r1, [sp, #0x14]
	LDR      r0, [r1]
	LDR      r1, [r1, #4]
	ADD      r0, #0x70
	LSL      r0, r0, #0xa
	STR      r0, [sp, #4]
	ADD      r1, #0x4c
	LSL      r1, r1, #0xa
	MOV      r0, #0x1f
	LSL      r0, r0, #0xa
	STR      r1, [sp, #8]
	STR      r0, [r6, #0x10]
	MOV      r0, #0xf
	LSL      r0, r0, #0xc
	STR      r0, [r6, #8]
	LDR      r0, [sp, #4]
	STR      r0, [r6]
	LDR      r1, [sp, #8]
	ADD      r0, r6, #0
	STR      r1, [r6, #4]
	BL       |sub_0802ed98|
	LDR      r0, [pc, #0x54]
	STRH     r0, [r7, #2]
	B        |loc_0800961E|
|loc_08009608|
	ADD      r0, r6, #0
	LDR      r1, [sp, #0x14]
	BL       |loc_080094F0|
	LDR      r0, [r6, #0x18]
	LDR      r1, [r6, #0x1c]
	STR      r0, [r6, #0x38]
	MOV      r0, #0x7d
	LSL      r0, r0, #6
	STR      r1, [r6, #0x3c]
	STRH     r0, [r7, #2]
|loc_0800961E|
	LDRB     r0, [r5, #4]
	MOV      r1, #0xc0
	STR      r0, [r4, #0x34]
	LDRB     r0, [r5, #5]
	STR      r0, [r4, #0x38]
	LDRB     r0, [r5, #6]
	STR      r0, [r4, #0x3c]
	LDRB     r0, [r5, #7]
	STR      r0, [r1, r6]
	LDRH     r0, [r5]
	STRH     r0, [r7, #4]
	LDRB     r0, [r5, #2]
	STRB     r0, [r7, #1]
	LDRB     r0, [r5, #3]
	STRB     r0, [r7]
	LDR      r1, [sp, #0x18]
	ADD      r0, r6, #0
	BL       |loc_0800938C|
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_08009648|
|unk_08009648|
	INCBIN	baserom.gba_0x9648_0x964a.extracted
