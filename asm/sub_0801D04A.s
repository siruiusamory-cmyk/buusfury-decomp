	CODE16
|sub_0801D04A|
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x3c]
	SUB      sp, #0x10
	LDR      r0, [r0]
	MOV      r2, #0
	LDR      r3, [pc, #0x38]
	STR      r2, [sp, #8]
	CMP      r1, #0
	STR      r0, [sp, #0xc]
	STR      r3, [sp, #4]
	BEQ      |loc_0801D066|
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_0801D066|
	ADD      r1, r2, #0
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0x24]
	MOV      r4, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0801D086|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D086|
	ADD      r0, r4, #0
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0801D08C|
|unk_0801D08C|
	INCBIN	baserom.gba_0x1d08c_0x1d08e.extracted
