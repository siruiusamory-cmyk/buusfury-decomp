	CODE16
|sub_0803B5AA|
	ADD      r0, r7, #0
	SUB      r7, #1
	CMP      r0, #0
	BGT      |loc_0803B530|
	MOV      r7, #0xff
	LDR      r0, [sp, #0x24]
	LDR      r1, [sp, #0x34]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [sp, #0x28]
	LDR      r1, [sp, #0x38]
	ADD      r0, r0, r1
	STR      r0, [sp, #0x28]
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x54]
	ADD      r2, r2, r1
	ADD      r1, sp, #0x24
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |sub_0803B602|
	LDR      r0, [sp, #0x24]
	LDR      r1, [sp, #0x34]
	SUB      r0, r0, r1
	STR      r0, [sp, #0x24]
	LDR      r0, [sp, #0x28]
	LDR      r1, [sp, #0x38]
	SUB      r0, r0, r1
	STR      r0, [sp, #0x28]
	LDR      r0, [sp, #0x34]
	STR      r1, [sp, #0x20]
	STR      r0, [sp, #0x1c]
	LDR      r0, [sp, #0x44]
	LDR      r1, [sp, #0x48]
|unk_0803B5F0|
	INCBIN	baserom.gba_0x3b5f0_0x3b5f2.extracted
	STR      r0, [sp, #0x34]
	LDR      r0, [sp, #0x1c]
|unk_0803B5F6|
	INCBIN	baserom.gba_0x3b5f6_0x3b5f8.extracted
	STR      r0, [sp, #0x44]
	LDR      r0, [sp, #0x20]
	STR      r1, [sp, #0x38]
	STR      r0, [sp, #0x48]
	B        |loc_0803B62C|
