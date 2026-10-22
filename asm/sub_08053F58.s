	CODE16
|sub_08053F58|
	STRH     r0, [r0, #4]
	LDRB     r7, [r7, #0x19]
	LDRB     r5, [r7, #0x11]
	LDRB     r3, [r7, #9]
	LDRB     r1, [r7, #1]
	STRB     r7, [r6, #0x19]
	STRB     r6, [r6, #0x15]
	STRB     r4, [r6, #0xd]
	STRB     r2, [r6, #5]
	STRB     r1, [r6, #1]
	LDR      r7, [r5, #0x64]
	LDR      r6, [r5, #0x54]
	LDR      r4, [r5, #0x44]
	LDR      r3, [r5, #0x24]
	LDR      r2, [r5, #0x14]
	LDR      r0, [r5, #4]
	STR      r7, [r4, #0x64]
	STR      r6, [r4, #0x54]
	STR      r4, [r4, #0x44]
	STR      r3, [r4, #0x34]
	STR      r2, [r4, #0x14]
	STR      r1, [r4, #4]
	LDRSH    r0, [r4, r5]
	LDRSH    r7, [r3, r1]
	LDRB     r6, [r3, r5]
	LDRB     r5, [r3, r1]
	LDRH     r4, [r3, r5]
	LDRH     r3, [r3, r1]
	LDR      r2, [r3, r5]
	LDR      r1, [r3, r1]
	LDRSB    r0, [r3, r5]
	LDRSB    r7, [r2, r1]
	STRB     r6, [r2, r5]
	STRB     r5, [r2, r5]
	STRB     r4, [r2, r1]
	STRH     r3, [r2, r5]
	STRH     r2, [r2, r1]
	STR      r2, [r2, r5]
	STR      r1, [r2, r1]
	STR      r0, [r2, r1]
	LDR      r7, [pc, #0x13c]
	LDR      r6, [pc, #0x13c]
	LDR      r5, [pc, #0x138]
	LDR      r5, [pc, #0x134]
	LDR      r4, [pc, #0x130]
	LDR      r3, [pc, #0x130]
	LDR      r3, [pc, #0x12c]
	LDR      r2, [pc, #0x128]
	LDR      r1, [pc, #0x128]
	LDR      r1, [pc, #0x124]
	LDR      r0, [pc, #0x120]
	BX       sb
|unk_08053FC0|
	INCBIN	baserom.gba_0x53fc0_0x53fc2.extracted
	MOV      r7, r8
	MOV      r6, r8
	CMP      r5, r8
	ADD      r5, r8
	ADD      r4, r8
	MUL      r4, r0
	MUL      r3, r0
|unk_08053FD0|
	INCBIN	baserom.gba_0x53fd0_0x53fd4.extracted
	ADC      r2, r0
	ADC      r1, r0
	LSL      r0, r0, #0
	LSL      r7, r7, #0x1f
	LSL      r0, r0, #0
	LDRB     r0, [r6, #0x1f]
	LSL      r4, r2, #0
	LSR      r0, r0, #0x20
	LSL      r4, r2, #0
	LSL      r0, r0, #0x10
	BX       pc
	LSL      r0, r0, #0
