	CODE16
|sub_08037BB6|
	LSL      r0, r0, #0xc
	SUB      sp, #0x1e0
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r0, #3
	SUB      sp, #0x1c
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x14]
	MOV      r0, #3
	BL       |inc_0x03d784_0x041118| + 0x2348
	SUB      r0, #1
	LSL      r0, r0, #8
	STR      r0, [sp, #0x18]
	LDR      r2, [r4, #4]
	LDR      r3, [sp, #0x14]
	LDR      r1, [r4, #8]
	ADD      r2, r2, r3
	LDR      r3, [sp, #0x18]
	ADD      r0, r5, #0
	ADD      r0, #0xff
	ADD      r1, r1, r3
	STR      r1, [sp, #8]
	ADD      r0, #0xa1
	ADD      r1, r2, #0
	STR      r2, [sp, #4]
	LDR      r2, [sp, #8]
	STR      r1, [sp, #0xc]
	STR      r2, [sp, #0x10]
	STMIA    r0!, {r1}
	LDR      r1, [sp, #0x10]
	STR      r1, [r0]
	ADD      sp, #0x1c
	MOV      r0, #0
	POP      {r4, r5, pc}
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08037C16|
	LDR      r1, [pc, #4]
	STR      r1, [r0]
|loc_08037C16|
	POP      {r3, pc}
|sub_08037C18|
|unk_08037C18|
	INCBIN	baserom.gba_0x37c18_0x37c1a.extracted
