	CODE16
|loc_0801124C|
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r4, r0, #0
	LDRB     r5, [r4]
	ASR      r0, r1, #6
	MOV      r7, #0xff
	CMP      r5, #0xff
	LDR      r1, [pc, #0x2fc]
	BEQ      |loc_080112A2|
	LDR      r2, [pc, #0x2f4]
|loc_0801125E|
	LSL      r3, r5, #2
	ADD      r3, r3, r5
	LSL      r3, r3, #1
	ADD      r3, r3, r4
	ADD      r6, r3, r2
	LDRH     r3, [r6, #4]
	CMP      r3, r1
	BGE      |loc_08011298|
	CMP      r3, r0
	BNE      |loc_08011290|
	MOV      r2, #1
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	STRB     r2, [r6]
	BL       |sub_08011200|
	LDRH     r0, [r6, #2]
	MOV      r1, #3
	LSL      r1, r1, #0xa
	ADD      r0, r0, r4
	ADD      r0, r0, r1
	STRB     r5, [r0]
	LDRH     r0, [r6, #2]
	LSL      r0, r0, #1
	POP      {r4, r5, r6, r7, pc}
|loc_08011290|
	CMP      r3, r0
	BLE      |loc_08011298|
	ADD      r7, r5, #0
	ADD      r1, r3, #0
|loc_08011298|
	LDRB     r5, [r6, #8]
	CMP      r5, #0xff
	BNE      |loc_0801125E|
	CMP      r7, #0xff
	BNE      |loc_080112A8|
|loc_080112A2|
	MOV      r0, #0
	MVN      r0, r0
	POP      {r4, r5, r6, r7, pc}
|loc_080112A8|
	LSL      r1, r7, #2
	ADD      r1, r1, r7
	LSL      r1, r1, #1
	ADD      r1, r1, r4
	ADD      r5, r1, r2
	LDRB     r1, [r4, #1]
	CMP      r1, #0xff
	BNE      |loc_080112D6|
	MOV      r2, #1
	ADD      r1, r7, #0
	ADD      r0, r4, #0
	STRB     r2, [r5]
	BL       |sub_08011200|
	LDRH     r0, [r5, #2]
	MOV      r1, #3
	LSL      r1, r1, #0xa
	ADD      r0, r0, r4
	ADD      r0, r0, r1
	STRB     r7, [r0]
	LDRH     r0, [r5, #2]
	LSL      r0, r0, #1
	POP      {r4, r5, r6, r7, pc}
|loc_080112D6|
	MOV      ip, r1
	LSL      r3, r1, #2
	ADD      r1, r3, r1
	LSL      r1, r1, #1
	ADD      r1, r1, r4
	ADD      r1, r1, r2
	LDRB     r3, [r1, #6]
	STRB     r3, [r4, #1]
	CMP      r3, #0xff
	BEQ      |loc_080112FE|
	ADD      r6, r3, #0
	LSL      r3, r6, #2
	ADD      r3, r3, r6
	LSL      r3, r3, #1
	MOV      r6, #0x69
	LSL      r6, r6, #4
	ADD      r3, r3, r4
	MOV      r2, #0xff
	ADD      r3, r3, r6
	STRB     r2, [r3, #0xb]
|loc_080112FE|
	STRB     r7, [r1, #7]
	LDRB     r2, [r5, #6]
	STRB     r2, [r1, #6]
	LDRB     r2, [r5, #6]
	CMP      r2, #0xff
	BEQ      |loc_0801131C|
	LSL      r3, r2, #2
	ADD      r2, r3, r2
	LSL      r2, r2, #1
	MOV      r3, #0x69
	LSL      r3, r3, #4
	ADD      r2, r2, r4
	ADD      r2, r2, r3
	MOV      r6, ip
	STRB     r6, [r2, #0xb]
|loc_0801131C|
	MOV      r6, ip
	STRB     r6, [r5, #6]
	LDRH     r2, [r5, #4]
	SUB      r2, r2, r0
	STRH     r2, [r5, #4]
	MOV      r2, #1
	STRB     r2, [r1]
	LDRH     r2, [r5, #2]
	LDRH     r3, [r5, #4]
	ADD      r2, r2, r3
	STRH     r2, [r1, #2]
	STRH     r0, [r1, #4]
	LDRH     r0, [r1, #2]
	MOV      r2, #3
	LSL      r2, r2, #0xa
	ADD      r0, r0, r4
	ADD      r0, r0, r2
	STRB     r6, [r0]
	LDRH     r0, [r1, #2]
	LSL      r0, r0, #1
	POP      {r4, r5, r6, r7, pc}
	LSL      r2, r1, #2
	ADD      r2, r2, r1
	LSL      r2, r2, #1
	LDR      r3, [pc, #0x204]
	ADD      r2, r2, r0
	ADD      r2, r2, r3
	MOV      r3, #0
	STRB     r3, [r2]
	MOV      r3, #0xff
	STRB     r3, [r2, #9]
	LDRB     r3, [r0]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x18
	CMP      r3, #0xff
	STRB     r3, [r2, #8]
	BEQ      |loc_08011378|
	ADD      r2, r3, #0
	LSL      r3, r2, #2
	ADD      r2, r3, r2
	LSL      r2, r2, #1
	MOV      r3, #0x69
	LSL      r3, r3, #4
	ADD      r2, r2, r0
	ADD      r2, r2, r3
	STRB     r1, [r2, #0xd]
|loc_08011378|
	STRB     r1, [r0]
	BX       lr
