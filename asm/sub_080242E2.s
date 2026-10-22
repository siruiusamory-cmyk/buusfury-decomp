	CODE16
|sub_080242E2|
	LSL      r0, r0, #0x18
	STR      r6, [sp, #0x100]
	LSL      r0, r0, #0x18
	LSL      r1, r3, #9
	LSL      r0, r0, #0
	PUSH     {r4, r5, r6, r7, lr}
	SUB      sp, #0xc
	ADD      r4, r0, #0
	BL       |loc_08024120|
	ADD      r6, r4, #0
	ADD      r6, #0xff
	ADD      r6, #1
	LDR      r1, [r6, #0x28]
	MOV      r0, #0xff
	ADD      r0, #0x45
	MOV      r5, #7
	MOV      r7, #0
	CMP      r1, #0
	BEQ      |sub_0802437A|
	CMP      r1, #1
	BNE      |loc_08024374|
	LDR      r1, [r6, #0x18]
	STR      r1, [sp, #8]
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BEQ      |loc_0802436E|
	LDR      r0, [pc, #0x23c]
	MOV      r1, #0xff
	STR      r0, [r4]
	ADD      r1, #0x15
	STRB     r5, [r1, r4]
	ADD      r5, r4, #0
	ADD      r5, #0xff
	ADD      r5, #1
	STR      r7, [r5, #0x1c]
	STR      r7, [r5, #0x20]
	MVN      r1, r7
	ADD      r0, r4, #0
	MOV      r2, #0x80
	ADD      r0, #0x84
	STR      r7, [r5, #0x18]
	BL       |inc_0x049120_0x055620| + 0xc
	MOV      r2, #0x10
	MOV      r1, #0
	ADD      r0, r5, #4
	BL       |inc_0x049120_0x055620| + 0xc
	LDR      r0, [pc, #0x214]
	LDR      r1, [pc, #0x220]
	STR      r0, [r5, #0x24]
	LDR      r0, [pc, #0x210]
	STR      r7, [r0]
	LDR      r0, [pc, #0x210]
	STR      r7, [r0]
	LDR      r0, [pc, #0x210]
	STR      r0, [r4]
	MOV      r0, #1
	STR      r0, [r5, #0x38]
|unk_0802435C|
	INCBIN	baserom.gba_0x2435c_0x2435e.extracted
	STR      r0, [r1]
	LDR      r0, [sp, #8]
	STR      r0, [r5, #0x2c]
	MOV      r0, #0xff
	ADD      r0, #0x41
	STR      r7, [r5, #0x3c]
	STR      r7, [r0, r4]
	STR      r7, [r1, #4]
|loc_0802436E|
	ADD      r0, r4, #0
	BL       |inc_0x03d784_0x041118| + 0x29dc
|loc_08024374|
	STR      r7, [r6, #0x2c]
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
