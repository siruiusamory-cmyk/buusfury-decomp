	CODE16
|sub_0801DF82|
	LSL      r0, r0, #0
	DCW      0xe9d8,0x0871
	STRH     r4, [r5, #0x16]
	LSR      r7, r5, #1
	STR      r4, [sp, #0x220]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STR      r2, [sp, #0x30]
	LSR      r4, r0, #0x20
	ADD      r0, sp, #0x320
	LSR      r4, r0, #0x20
	STR      r5, [sp, #0x220]
	LSR      r4, r0, #0x20
|unk_0801DFA0|
	INCBIN	baserom.gba_0x1dfa0_0x1dfa2.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	ADD      r4, r2, r4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x24]
	PUSH     {r4, lr}
	LDR      r1, [r0]
	LDRH     r1, [r1, #4]
	LSL      r1, r1, #0x1c
	LSR      r1, r1, #0x1f
	BEQ      |sub_0801DFCE|
	LDR      r0, [r0, #4]
	LDR      r4, [pc, #0x1c]
	MOV      r3, #0
	MOV      r2, #0x40
	ADD      r0, r0, r4
	LDR      r1, [pc, #0x10]
	BL       |inc_0x03d784_0x041118| + 0xbf4
	MOV      r0, #1
	POP      {r4, pc}
