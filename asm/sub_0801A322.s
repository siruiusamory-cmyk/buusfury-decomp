	CODE16
|sub_0801A322|
	LSR      r4, r0, #0x20
	CMP      r4, #4
	LSL      r0, r0, #0xc
	STRH     r4, [r5, #0x16]
	LSR      r3, r5, #1
	LDMIA    r7!, {r2, r3, r5, r7}
	LSR      r7, r6, #1
	BGT      |loc_0801A234|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x264]
	PUSH     {r3, lr}
	LDR      r1, [r1, #0x14]
	LDR      r1, [r1, #0xc]
	CMP      r1, #0
	BNE      |sub_0801A344|
	MOV      r0, #0
	POP      {r3, pc}
