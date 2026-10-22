	CODE16
|sub_08037A04|
	PUSH     {r4, lr}
	LDR      r0, [r0, #0xc]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08037A20|
	LDR      r1, [pc, #0xc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08037A20|
	POP      {r4, pc}
	LSL      r0, r0, #0
|unk_08037A24|
	INCBIN	baserom.gba_0x37a24_0x37a26.extracted
	LSR      r6, r6, #1
	LDR      r6, [sp, #0x20]
	LSR      r4, r0, #0x20
	LDRH     r0, [r1, #0x12]
	SUB      r0, #1
	BPL      |loc_08037A3A|
	LDR      r0, [r1, #0x50]
	LDR      r0, [r0]
	LSL      r0, r0, #3
	SUB      r0, #1
|loc_08037A3A|
	STRH     r0, [r1, #0x12]
	ASR      r0, r0, #3
	STRB     r0, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x30]
	ADD      r3, r2, r1
	MOV      r2, #0
	MOV      r1, #4
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, pc}
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r0, [pc, #0xd8]
	ADD      r4, r1, #0
	LDR      r0, [r0]
	SUB      sp, #0x2c
	CMP      r0, #0
	BNE      |sub_08037A6A|
	MOV      r0, #1
	ADD      sp, #0x2c
	POP      {r4, r5, r6, r7, pc}
