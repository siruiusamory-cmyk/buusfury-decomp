	CODE16
|sub_08005F8E|
	LSL      r0, r0, #0
	STR      r4, [r3, #0x1c]
	LSR      r5, r0, #0x20
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r6, [sp, #0x200]
	LSR      r4, r0, #0x20
|unk_08005FA0|
	INCBIN	baserom.gba_0x5fa0_0x5fa2.extracted
	LSR      r4, r0, #0x20
	LSL      r0, r0, #0
	LSL      r1, r0, #0x18
	LDR      r1, [r0, #4]
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r0, [r1, #8]
	BX       lr
	LDR      r1, [r0, #4]
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #1
	STR      r0, [r1, #8]
	BX       lr
	PUSH     {r4, r5, r6}
	ADD      r6, sp, #0xc
	LDMIA    r6!, {r4, r5, r6}
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0xd0]
	STR      r1, [r0]
	ADD      r0, #8
	STMIA    r0!, {r2, r3, r4, r5, r6}
	SUB      r0, #0x1c
	POP      {r4, r5, r6}
	BX       lr
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	ADD      r0, #0xff
	ADD      r0, #1
	LDR      r0, [r0, #0xc]
	LDR      r1, [r4, #8]
	CMP      r0, r1
	BNE      |loc_0800608A|
	LDR      r0, [pc, #0xb4]
	LDR      r1, [pc, #0xb0]
	LDR      r0, [r0]
	MOV      r5, #0
	LDRH     r2, [r0, #4]
	LDR      r1, [r1, #4]
	LSL      r0, r2, #0x19
	LSR      r3, r0, #0x1f
	LDR      r0, [pc, #0xa8]
	ADD      r0, r1, r0
	LDR      r1, [pc, #0xa8]
	CMP      r3, #0
	BEQ      |sub_0800601E|
	LDR      r3, [r4, #0xc]
	CMP      r3, #0
	BLT      |sub_0800601E|
	ADD      r3, r5, #0
	MOV      r2, #0x40
	BL       |inc_0x03d784_0x041118| + 0xbf4
	LDR      r0, [r4, #4]
	LDR      r1, [r4, #0xc]
	ADD      r0, #0xff
	ADD      r0, #1
	ADD      r0, #0xc
	STMIA    r0!, {r1, r5}
	MOV      r0, #1
	POP      {r3, r4, r5, pc}
