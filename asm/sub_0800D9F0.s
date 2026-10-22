	CODE16
|sub_0800D9F0|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x2c8]
	ADD      r5, r1, #0
	LDR      r1, [pc, #0x2c8]
	STR      r0, [r4]
	LDR      r0, [r1]
	SUB      r0, #1
	STR      r0, [r1]
	LDR      r0, [pc, #0x2b4]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x2bc]
	CMP      r1, r0
	BEQ      |loc_0800DA16|
	LDR      r0, [pc, #0x2ac]
	LDR      r0, [r0]
	BL       |loc_0801142A|
|loc_0800DA16|
	LDR      r0, [pc, #0x2b4]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_0800DA24|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0800DA24|
	POP      {r3, r4, r5, pc}
	PUSH     {r4}
	LDR      r4, [r1]
	LDR      r3, [r2]
	LDR      r2, [r2, #4]
	LDR      r1, [r1, #4]
	ASR      r4, r4, #1
	SUB      r3, r3, r4
	SUB      r1, r2, r1
	STR      r1, [r0, #4]
	STR      r3, [r0]
	POP      {r4}
	BX       lr
	PUSH     {r4, r5}
	LDR      r5, [pc, #0x278]
	LDR      r3, [r0, #0x18]
	LDR      r1, [r5, #4]
	SUB      sp, #8
	ADD      r1, #0x28
	LDR      r4, [r1]
	ADD      r2, r0, #0
	SUB      r3, r3, r4
	LDR      r4, [r0, #0x1c]
	LDR      r1, [r1, #4]
	STR      r3, [sp]
	SUB      r1, r4, r1
	STR      r1, [sp, #4]
	ADD      r1, r3, #0
	LDR      r3, [sp, #4]
	ADD      r2, #0x28
	STMIA    r2!, {r1, r3}
	LDR      r1, [r5, #4]
	LDR      r2, [r0, #0x18]
	ADD      r1, #0x18
	LDR      r3, [r1, #8]
	CMP      r2, r3
	BGE      |sub_0800DA8E|
	LDR      r2, [r1]
	LDR      r3, [r0, #0x20]
	CMP      r2, r3
	BGE      |sub_0800DA8E|
	LDR      r2, [r0, #0x1c]
	LDR      r3, [r1, #0xc]
	CMP      r2, r3
	BGE      |sub_0800DA8E|
	LDR      r1, [r1, #4]
	LDR      r0, [r0, #0x24]
	CMP      r1, r0
	BGE      |sub_0800DA8E|
	MOV      r0, #1
	ADD      sp, #8
	POP      {r4, r5}
	BX       lr
