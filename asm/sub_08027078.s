	CODE16
|sub_08027078|
	CMP      r1, #0
	BEQ      |loc_08027096|
	SUB      r1, #1
	STR      r1, [r4, #0x20]
	LSL      r3, r1, #0x1f
	BMI      |loc_08027096|
	LDRH     r3, [r5, #0xc]
	ASR      r1, r1, #1
	LSL      r1, r1, #0xa
	LSL      r3, r3, #5
	ADD      r0, r3, r0
	ADD      r1, r1, r5
	ADD      r1, #0x10
	BL       |inc_0x049120_0x055620| + 0x18
|loc_08027096|
	LDR      r0, [r7]
	LDRH     r0, [r0, #2]
	LSL      r0, r0, #0x1a
	LSR      r1, r0, #0x1f
	LDR      r0, [pc, #0x120]
	ADD      r0, r5, r0
	CMP      r1, #0
	BEQ      |loc_080270AC|
	LDR      r1, [r0]
	SUB      r1, #0x80
	STR      r1, [r0]
|loc_080270AC|
	LDR      r1, [r7]
	ADD      r3, r7, #0
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x1b
	LSR      r1, r1, #0x1f
	BEQ      |loc_080270BE|
	LDR      r1, [r0]
	ADD      r1, #0x80
	STR      r1, [r0]
|loc_080270BE|
	LDR      r1, [r3]
	LDR      r2, [pc, #0x100]
	LDRH     r1, [r1, #2]
	ADD      r2, r5, r2
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	CMP      r1, #0
	BEQ      |loc_080270D4|
	LDR      r1, [r2]
	SUB      r1, #0x80
	STR      r1, [r2]
|loc_080270D4|
	LDR      r1, [r3]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_080270E4|
	LDR      r1, [r2]
	ADD      r1, #0x80
	STR      r1, [r2]
|loc_080270E4|
	MOV      r1, #0xc1
	LSL      r1, r1, #4
	ADD      r1, r5, r1
	LDR      r3, [r1]
	LDR      r7, [r0]
	ADD      r3, r3, r7
	STR      r3, [r1]
	LDR      r7, [r1, #4]
	LDR      r3, [r0, #4]
	ADD      r3, r7, r3
	STR      r3, [r1, #4]
	LDR      r7, [r4, #0x18]
	LSL      r3, r7, #1
	ADD      r3, r3, r7
	ASR      r7, r3, #0x1f
	LSR      r7, r7, #0x1e
	ADD      r3, r7, r3
	ASR      r3, r3, #2
	STR      r3, [r4, #0x18]
	LDR      r7, [r4, #0x1c]
	LSL      r3, r7, #1
	ADD      r3, r3, r7
	ASR      r7, r3, #0x1f
	LSR      r7, r7, #0x1e
	ADD      r3, r7, r3
	ASR      r3, r3, #2
	STR      r3, [r4, #0x1c]
	MOV      r3, #1
	LDR      r4, [r1]
	LSL      r3, r3, #0xc
	CMP      r4, r3
	BGE      |loc_08027128|
	STR      r3, [r1]
	STR      r6, [r0]
|loc_08027128|
	MOV      r4, #7
	LDR      r7, [r1]
	LSL      r4, r4, #0xd
	CMP      r7, r4
	BLE      |loc_08027136|
	STR      r4, [r1]
	STR      r6, [r0]
|loc_08027136|
	LDR      r0, [pc, #0x90]
	ADD      r0, r5, r0
	LDR      r1, [r0]
	CMP      r1, r3
	BGE      |loc_08027144|
	STR      r3, [r0]
	STR      r6, [r2]
|loc_08027144|
	MOV      r1, #9
	LDR      r3, [r0]
	LSL      r1, r1, #0xc
	CMP      r3, r1
	BLE      |loc_08027152|
	STR      r1, [r0]
	STR      r6, [r2]
|loc_08027152|
	POP      {r3, r4, r5, r6, r7, pc}
	ADD      r2, r1, #0
	LDR      r1, [r1]
	ADD      r3, r1, #0
	ADD      r3, #8
	STR      r3, [r2]
	MOV      r3, #0xc1
	LDR      r2, [pc, #0x68]
	LSL      r3, r3, #4
	ADD      r3, r0, r3
	STR      r2, [r1]
	LDR      r3, [r3]
	ASR      r3, r3, #8
	SUB      r3, #0x10
	LSL      r3, r3, #0x17
	LSR      r3, r3, #7
	ORR      r2, r3
	LDR      r3, [pc, #0x50]
	STR      r2, [r1]
	ADD      r3, r0, r3
	LDR      r3, [r3]
	LSR      r2, r2, #8
	ASR      r3, r3, #8
	ADD      r3, #0xf0
	LSL      r3, r3, #0x18
|loc_08027184|
	LSR      r3, r3, #0x18
	LSL      r2, r2, #8
	ORR      r2, r3
	STR      r2, [r1]
	LDRH     r0, [r0, #0xc]
	LDR      r2, [r1, #4]
	LSR      r2, r2, #0xa
	LSL      r0, r0, #0x16
	LSR      r0, r0, #0x16
	LSL      r2, r2, #0xa
	ORR      r0, r2
	MOV      r2, #3
	LSL      r2, r2, #0xa
	BIC      r0, r2
	MOV      r2, #1
	LSL      r2, r2, #0xa
	ADD      r0, r0, r2
	STR      r0, [r1, #4]
	MOV      r0, #0
	BX       lr
|sub_080271AC|
|unk_080271AC|
	INCBIN	baserom.gba_0x271ac_0x271ae.extracted
