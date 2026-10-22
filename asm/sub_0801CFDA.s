	CODE16
|sub_0801CFDA|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0801CFEE|
	LDR      r1, [pc, #0x14]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_0801CFEE|
	POP      {r4, pc}
|sub_0801CFF0|
	DCW      0x1c34
	DCW      0x0300,0xe254
|sub_0801CFF6|
	LSR      r1, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LDR      r2, [sp, #0xb0]
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r0, [pc, #0x84]
	SUB      sp, #0x10
	LDR      r0, [r0]
	MOV      r2, #0
	LDR      r3, [pc, #0x80]
	STR      r2, [sp, #8]
	CMP      r1, #0
	STR      r0, [sp, #0xc]
	STR      r3, [sp, #4]
	BEQ      |loc_0801D020|
	ADD      r2, r1, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_0801D020|
	ADD      r1, r2, #0
	ADD      r0, sp, #4
	BL       |inc_0x153f2_0x1a3f2| + 0x5aa
	LDR      r0, [pc, #0x68]
	MOV      r4, #1
	STR      r0, [sp, #4]
	LDR      r0, [sp, #8]
	CMP      r0, #0
	BEQ      |loc_0801D040|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0801D040|
	ADD      r0, r4, #0
	ADD      sp, #0x10
	POP      {r4, pc}
|sub_0801D046|
|unk_0801D046|
	INCBIN	baserom.gba_0x1d046_0x1d04a.extracted
