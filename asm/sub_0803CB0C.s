	CODE16
|sub_0803CB0C|
	MOV      r0, #0
	MOV      r1, #1
	SUB      r0, r1, r0
	BX       lr
	PUSH     {r3, lr}
	MOV      r0, #4
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803CB24|
	LDR      r1, [pc, #0x1c]
	STR      r1, [r0]
|loc_0803CB24|
	POP      {r3, pc}
	LSL      r0, r0, #0
	SUB      r4, r2, r6
	LSL      r0, r0, #0xc
	STRH     r0, [r3, #4]
	LSR      r3, r5, #1
	STMIA    r4!, {r4, r5, r7}
	LSR      r7, r6, #1
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	STMIA    r6!, {r2, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x20
	LSR      r4, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
	PUSH     {r3, lr}
	LDRH     r2, [r1, #0x12]
	MOV      r0, #0
	ADD      r2, #1
	LSL      r2, r2, #0x10
	LSR      r2, r2, #0x10
	STRH     r2, [r1, #0x12]
	CMP      r2, #0x30
	BCC      |loc_0803CB66|
	SUB      r2, #0x30
	ASR      r0, r2, #3
|loc_0803CB66|
	LDR      r2, [r1, #0x50]
	LDR      r2, [r2]
	CMP      r2, r0
	BGT      |sub_0803CB7E|
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
