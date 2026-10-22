	CODE16
|sub_08000B40|
	MOV      r1, #0xff
	STRB     r1, [r0, #2]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08000B5A|
	LDR      r1, [pc, #0x24]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	STR      r2, [r0, #8]
	STR      r4, [r0, #0xc]
|loc_08000B5A|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1c]
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08000B6A|
	ADD      r2, r0, #0
	ADD      r2, #0xff
	ADD      r2, #0x8d
|loc_08000B6A|
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
	LSL      r0, r0, #0
	LDR      r7, [pc, #0x2f0]
	LSR      r5, r0, #0x20
	LDMIA    r0!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x26c]
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x14]
	ADD      r0, r1, r0
	LDRB     r1, [r0, #2]
	ADD      r1, r1, r2
	MOV      r2, #0xff
	ADD      r2, #1
	CMP      r1, r2
	BGE      |loc_08000BAC|
	STRB     r1, [r0, #2]
	BX       lr
|loc_08000BAC|
	MOV      r1, #0xff
	STRB     r1, [r0, #2]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x244]
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x14]
	ADD      r0, r1, r0
	LDRB     r1, [r0, #2]
	ADD      r1, #0xff
	STRB     r1, [r0, #2]
	BX       lr
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [pc, #0x220]
	LDR      r0, [r0, #4]
	LDR      r1, [r1, #0x14]
	ADD      r0, r1, r0
	LDRB     r1, [r0, #2]
	SUB      r1, r1, r2
	STRB     r1, [r0, #2]
	BX       lr
	PUSH     {r3, lr}
	LDR      r1, [r0]
	ADD      r3, sp, #0
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRH     r1, [r3, #2]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STRH     r1, [r3]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |sub_08000158|
	ADD      r1, r0, #0
	MOV      r0, #0
	MOV      r2, sp
	BL       |sub_0801111C|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1d4]
	LDR      r0, [r0, #0x18]
	BL       |List_Append|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r1, [r0, #4]
	LDR      r0, [pc, #0x1bc]
	LDR      r0, [r0, #0xc]
	BL       |loc_08009108|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0]
	LDR      r5, [pc, #0x1ac]
	SUB      r0, #1
	STR      r0, [r4]
	LSL      r0, r0, #2
	ADD      r0, r0, r4
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BLT      |sub_08000C80|
	BL       |sub_08000158|
	ADD      r2, r0, #0
	LDR      r0, [r5, #0x18]
	MOV      r1, #5
	BL       |loc_08011CCA|
	LDR      r1, [r4]
	ADD      r2, r1, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r4
	STR      r2, [r4]
	STR      r0, [r1, #4]
	POP      {r3, r4, r5, pc}
