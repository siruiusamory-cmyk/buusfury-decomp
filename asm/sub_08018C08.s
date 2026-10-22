	CODE16
|sub_08018C08|
	PUSH     {r4, lr}
	LDR      r4, [r0, #0xc]
	MOV      r0, #8
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08018C1C|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
|loc_08018C1C|
	POP      {r4, pc}
	LSL      r0, r0, #0
	STR      r7, [sp, #0x350]
	LSR      r4, r0, #0x20
	LDRH     r0, [r1, #0x12]
	SUB      r0, #1
	BPL      |loc_08018C32|
	LDR      r0, [r1, #0x50]
	LDR      r0, [r0]
	LSL      r0, r0, #3
	SUB      r0, #1
|loc_08018C32|
	STRH     r0, [r1, #0x12]
	ASR      r0, r0, #3
	STRB     r0, [r1, #0x11]
	BX       lr
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r0, #0
	LDR      r0, [pc, #0x200]
	ADD      r4, r1, #0
	LDR      r1, [r0]
	SUB      sp, #0x4c
	CMP      r1, #0
	BNE      |sub_08018C50|
	MOV      r0, #1
	ADD      sp, #0x4c
	POP      {r4, r5, r6, r7, pc}
