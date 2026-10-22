	CODE16
|sub_0801F1AC|
	MOV      r3, #0
	ADD      r5, r0, #0
	ADD      r5, #0xff
	ADD      r5, #1
	LDR      r0, [pc, #0xa8]
	STR      r3, [r5, #0x2c]
	LDR      r0, [r0]
	CMP      r0, #0
	BNE      |loc_0801F21A|
	CMP      r4, #0
	BLE      |loc_0801F214|
|loc_0801F1C2|
	ADD      r3, r2, #0
	LDRB     r6, [r1, r3]
	ADD      r2, #1
	ADD      r3, r2, #1
	LDRB     r2, [r1, r2]
	MOV      r7, #0xff
	LSL      r7, r7, #8
	LSL      r2, r2, #8
	AND      r2, r7
	ORR      r2, r6
	STR      r2, [sp]
	LDRB     r6, [r1, r3]
	ADD      r2, r3, #1
	ADD      r3, sp, #0
	STRB     r6, [r3, #4]
	ADD      r3, r2, #0
	LDRB     r6, [r1, r3]
	ADD      r3, sp, #0
	ADD      r2, #1
	STRB     r6, [r3, #5]
	LDR      r3, [r5, #0x30]
	LDR      r6, [pc, #0x7c]
	ADD      r0, #1
	ADD      r3, r3, r6
	LDR      r6, [r3]
	ADD      r7, r6, #1
	LSL      r6, r6, #3
	ADD      r6, r6, r3
	STR      r7, [r3]
	ADD      r3, sp, #0
	LDRH     r3, [r3]
	ADD      r6, #4
	CMP      r0, r4
	STRH     r3, [r6]
	ADD      r3, sp, #0
	LDRH     r3, [r3, #2]
	STRH     r3, [r6, #2]
	ADD      r3, sp, #0
	LDRH     r3, [r3, #4]
	STRH     r3, [r6, #4]
	BLT      |loc_0801F1C2|
|loc_0801F214|
	LDR      r1, [pc, #0x48]
	MOV      r0, #1
	STR      r0, [r1]
|loc_0801F21A|
	ADD      sp, #8
	POP      {r4, r5, r6, r7}
	BX       lr
|sub_0801F220|
|unk_0801F220|
	INCBIN	baserom.gba_0x1f220_0x1f22a.extracted
