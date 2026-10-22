	CODE16
|sub_08027B4C|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r5, [r1, #4]
	SUB      sp, #0x10
	ADD      r7, sp, #8
	ADD      r4, r0, #0
	ADD      r1, r5, #0
	ADD      r0, r7, #0
	BL       |inc_0x0158_0x143f2| + 0xfdec
	LDR      r2, [r4, #0x14]
	ADD      r3, r4, #0
	STR      r2, [sp]
	ADD      r2, r4, #0
	ADD      r3, #8
	ADD      r6, r3, #0
	ADD      r2, #0x10
	ADD      r0, r7, #0
	LDR      r1, [sp, #0x18]
	BL       |inc_0x153f2_0x1a3f2| + 0x3edc
	MOV      r1, #3
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xeb82
	LDR      r1, [pc, #0xa8]
	ADD      r0, r5, #0
	BL       |inc_0x0158_0x143f2| + 0xebc0
	LDR      r0, [r4, #8]
	ADD      r2, r0, #0
	CMP      r0, #0
	BGE      |loc_08027B8E|
|unk_08027B8C|
	INCBIN	baserom.gba_0x27b8c_0x27b8e.extracted
