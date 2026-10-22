	CODE16
|Blend_WriteControl5|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r5, r0, #0
	LDR      r0, [pc, #0x2b0]
	LDR      r2, [pc, #0x2b0]
	LDR      r0, [r0]
	LDR      r1, [pc, #0x2bc]
	LDRH     r0, [r0, #4]
	LDR      r2, [r2, #4]
	LDR      r7, [pc, #0x2b8]
	ADD      r1, r2, r1
	STR      r1, [sp]
	MOV      r1, #0xb
	MOV      r2, #0xed
	LSL      r2, r2, #2
	LSL      r1, r1, #8
	LSL      r0, r0, #0x19
	LSR      r0, r0, #0x1f
	ADD      r4, r5, r1
	ADD      r6, r5, r2
	CMP      r0, #0
	BEQ      |loc_08025452|
	LDR      r0, [r4, #0x10]
	CMP      r0, #0
	BEQ      |loc_08025452|
	SUB      r0, #1
	STR      r0, [r4, #0x10]
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	STR      r0, [r4, #0x14]
	ADD      r0, r5, #0
	BL       |loc_08025056|
	ADD      r1, r7, #0
	MOV      r3, #0
	MOV      r2, #0x40
	LDR      r0, [sp]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025452|
	LDR      r0, [pc, #0x268]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x18
	LSR      r0, r0, #0x1f
	BEQ      |loc_08025486|
	LDR      r1, [r6]
	LDR      r0, [r4, #0x10]
	SUB      r1, #1
	CMP      r1, r0
	BLE      |loc_08025486|
	ADD      r0, #1
	STR      r0, [r4, #0x10]
	LSL      r0, r0, #3
	ADD      r0, r0, r6
	LDR      r0, [r0, #4]
	STR      r0, [r4, #0x14]
	ADD      r0, r5, #0
	BL       |loc_08025056|
	ADD      r1, r7, #0
	MOV      r3, #0
	MOV      r2, #0x40
	LDR      r0, [sp]
	BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025486|
	LDR      r0, [r6]
	CMP      r0, #0
	BEQ      |loc_080254A6|
	LDR      r0, [pc, #0x22c]
	LDR      r0, [r0]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_080254A6|
	ADD      r0, r5, #0
	BL       |loc_08024BE6|
	LDR      r0, [pc, #0x224]
	LDR      r1, [pc, #0x228]
	STRH     r0, [r1, #0x10]
	MOV      r0, #1
	STRB     r0, [r5, #0xd]
|loc_080254A6|
	POP      {r3, r4, r5, r6, r7, pc}
|loc_080254A8|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x210]
	ADD      r4, r0, #0
	LDR      r1, [r6]
	MOV      r2, #0xb
	LDRH     r1, [r1, #2]
	LSL      r2, r2, #8
	ADD      r5, r4, r2
	LSL      r1, r1, #0x19
	LSR      r1, r1, #0x1f
	MOV      r0, #0
	CMP      r1, #0
	BEQ      |loc_080254D4|
	LDR      r1, [r5, #0x18]
	CMP      r1, #0
	BEQ      |loc_080254D4|
	SUB      r1, #1
	STR      r1, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |sub_08025004|
	MOV      r0, #1
|loc_080254D4|
	LDR      r1, [r6]
	LDRH     r1, [r1, #2]
	LSL      r1, r1, #0x18
	LSR      r1, r1, #0x1f
	BEQ      |loc_080254F2|
	LDR      r1, [r5, #0x18]
	LDR      r2, [r5, #0x1c]
	CMP      r1, r2
	BGE      |loc_080254F2|
	ADD      r1, #1
	STR      r1, [r5, #0x18]
	ADD      r0, r4, #0
	BL       |sub_08025004|
	MOV      r0, #1
|loc_080254F2|
	LDRB     r1, [r4, #0xc]
	CMP      r1, r0
	BEQ      |loc_080254FA|
	STRB     r0, [r4, #0xc]
|loc_080254FA|
	LDR      r0, [r6]
	LDRH     r0, [r0, #4]
	LSL      r0, r0, #0x1f
	BEQ      |loc_0802550E|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0802550E|
	POP      {r4, r5, r6, pc}
|sub_08025510|
|unk_08025510|
		PUSH {r3, r4, r5, r6, r7, lr}
		ADD r5, r0, #0
		MOV r0, #0xed
		LSL r0, r0, #2
		ADD r0, r5, r0
		LDR r7, [pc, #0x1a0]
		STR r0, [sp]
		LDR r1, [r7]
		LDR r0, [r0]
		LDRH r1, [r1, #4]
		LSL r1, r1, #0x1a
		LSR r2, r1, #0x1f
		CMP r0, #0
		DCW     0xD040
		MOV r0, #0xb
		LSL r0, r0, #8
		ADD r4, r5, r0
		LDR r1, [sp]
		LDR r0, [r4, #0x10]
		LSL r0, r0, #3
		ADD r0, r0, r1
		ADD r0, #4
		LDR r3, [r0]
		LDR r6, [r0, #4]
		ADD r1, r3, #0
		CMP r3, r6
		DCW     0xD033
		ADD r6, r7, #0
		LDR r6, [r6, #4]
		LDR r3, [pc, #0x180]
		ADD r7, r6, r3
		LDR r6, [pc, #0x180]
		CMP r2, #0
		BEQ      |loc_08025574|
		LDR r2, [r4, #0x14]
		SUB r2, #1
		STR r2, [r4, #0x14]
		CMP r1, r2
		BLE      |loc_08025562|
		LDR r0, [r0, #4]
		STR r0, [r4, #0x14]
|loc_08025562|
		ADD r0, r5, #0
		BL       |loc_08025056|
		ADD r1, r6, #0
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
		BL       |inc_0x03d784_0x041118| + 0xbf4
|loc_08025574|
		LDR r0, [pc, #0x144]
		LDR r0, [r0]
		LDRH r0, [r0, #4]
		LSL r0, r0, #0x1b
		LSR r0, r0, #0x1f
		DCW     0xD016
		LDR r0, [sp]
		LDR r1, [r4, #0x10]
		LSL r1, r1, #3
		ADD r1, r1, r0
		LDR r0, [r4, #0x14]
		ADD r1, #4
		LDR r2, [r1, #4]
		ADD r0, #1
		STR r0, [r4, #0x14]
		CMP r2, r0
		BGE      |loc_0802559A|
		LDR r0, [r1]
		STR r0, [r4, #0x14]
|loc_0802559A|
		ADD r0, r5, #0
		BL       |loc_08025056|
		ADD r1, r6, #0
		MOV r3, #0
		MOV r2, #0x40
		ADD r0, r7, #0
	INCBIN  baserom.gba_0x255a8_0x255aa.extracted
|sub_080255AA|
|unk_080255AA|
	INCBIN	baserom.gba_0x255aa_0x255ae.extracted
	LDRB     r0, [r5, #0xe]
	CMP      r0, #0
	BEQ      |sub_080255BC|
	ADD      r0, r5, #0
	BL       |loc_080254A8|
	POP      {r3, r4, r5, r6, r7, pc}
