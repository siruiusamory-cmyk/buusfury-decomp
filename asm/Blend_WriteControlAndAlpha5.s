	CODE16
|Blend_WriteControlAndAlpha5|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x70]
	ADD      r5, r1, #0
	STR      r0, [r4]
	ADD      r0, #0x2c
	STR      r0, [r4, #0xc]
	LDR      r0, [pc, #0x64]
	MOV      r1, #0
	LDR      r0, [r0, #0xc]
	BL       |inc_0x0158_0x143f2| + 0x953a
	LDR      r0, [r4, #0x5c]
	CMP      r0, #0
	BEQ      |loc_08030FA4|
	MOV      r0, #0x41
	LDR      r1, [pc, #0x58]
	LSL      r0, r0, #6
	STRH     r0, [r1, #0x10]
	MOV      r0, #0x10
	STRB     r0, [r1, #0x12]
	STRB     r0, [r1, #0x13]
|loc_08030FA4|
	LDR      r0, [pc, #0x50]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08030FB2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08030FB2|
	POP      {r3, r4, r5, pc}
|sub_08030FB4|
|unk_08030FB4|
		MOV r0, #0
		BX       lr
