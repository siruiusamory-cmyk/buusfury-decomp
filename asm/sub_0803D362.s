	CODE16
|sub_0803D362|
	LSL      r0, r0, #0xc
	STMIA    r5!, {r2, r3}
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
|unk_0803D370|
	INCBIN	baserom.gba_0x3d370_0x3d372.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0x120]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x3c
	CMP      r1, #0
	BNE      |sub_0803D388|
	MOV      r0, #0
	ADD      sp, #0x3c
	POP      {r4, r5, r6, r7, pc}
