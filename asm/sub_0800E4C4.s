	CODE16
|sub_0800E4C4|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	BL       |loc_0800E1D0|
	LDR      r0, [r5, #0x14]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x18]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	CMP      r0, #0
	BEQ      |loc_0800E54E|
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r0, #0
	ADD      r1, #0x1c
	MOV      r3, #0
	LDRSH    r1, [r1, r3]
	MOV      r3, #0x16
	LDR      r2, [r4, #0x14]
	MUL      r1, r3
	ADD      r1, r1, r2
	LDR      r2, [pc, #0x134]
	ADD      r1, r1, r2
	STR      r1, [r4, #0x14]
	LSR      r2, r1, #0x10
	BEQ      |loc_0800E54E|
	ASR      r2, r1, #0x10
	ADD      r1, r0, #0
	ADD      r1, #0x20
	LDRH     r3, [r1]
	CMP      r3, r2
	BLE      |loc_0800E524|
	LDRH     r0, [r1]
	SUB      r0, r0, r2
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
|loc_0800E51A|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_0800E51A|
	B        |loc_0800E546|
|loc_0800E524|
	ADD      r0, #0x16
	MOV      r3, #0
	LDRSH    r0, [r0, r3]
	CMP      r0, #0
	BEQ      |loc_0800E546|
	MOV      r0, #0
|loc_0800E530|
	STRH     r0, [r1]
	LDRH     r2, [r1]
	CMP      r2, r0
	BNE      |loc_0800E530|
	LDR      r1, [r5]
	ADD      r0, r5, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0x18
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800E546|
	LDR      r0, [r4, #0x14]
	LSL      r0, r0, #0x10
	LSR      r0, r0, #0x10
	STR      r0, [r4, #0x14]
|loc_0800E54E|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0800E074|
	MOV      r0, #0x47
	LSL      r0, r0, #3
	ADD      r5, r4, r0
	LDR      r1, [r5]
	MOV      r0, #4
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r5]
	MOV      r0, #0x8f
	LSL      r0, r0, #2
	ADD      r4, r4, r0
	LDR      r1, [r4]
	MOV      r0, #4
	BL       |inc_0x046118_0x049114| + 0xd40
	STR      r0, [r4]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #0xc]
	SUB      r1, #1
	STR      r1, [r0, #0xc]
	BPL      |loc_0800E5BE|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0x17
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800E5BE|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0x17
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800E5BE|
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r5, r0, #0
	BL       |loc_08013C66|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |sub_0800E074|
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r1, [r0, #0x38]
	ADD      r1, #0x40
	STR      r1, [r0, #0x38]
	LDR      r1, [r0, #0x3c]
	ADD      r1, #0x40
	STR      r1, [r0, #0x3c]
	POP      {r3, r4, r5, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #0xc]
	SUB      r1, #1
	STR      r1, [r0, #0xc]
	BPL      |loc_0800E620|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x34]
	ADD      r2, r2, r1
	MOV      r1, #0x18
	BL       |inc_0x046118_0x049114| + 0x98c
	CMP      r0, #0
	BNE      |loc_0800E620|
	LDR      r1, [r4]
	ADD      r0, r4, #0
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0x18
	BL       |inc_0x046118_0x049114| + 0x98c
|loc_0800E620|
	POP      {r4, pc}
	LSL      r0, r0, #0
	MOV      r5, #0xe0
	LSR      r7, r0, #0x20
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	LSR      r5, r1, #0x13
	LSL      r0, r0, #0
	ADD      r3, #0x33
	LSL      r0, r0, #0
	PUSH     {r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	SUB      sp, #0x7c
	BL       |loc_0800E1D0|
	LDR      r0, [r4, #0x10]
	SUB      r0, #1
	STR      r0, [r4, #0x10]
	BPL      |loc_0800E66A|
	LDR      r1, [r5]
	MOV      r2, #0x80
	LDR      r2, [r2, r1]
	ADD      r0, r5, #0
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	LDRH     r0, [r0, #2]
	ADD      r2, sp, #0x6c
	LDR      r1, [pc, #0x50]
	LSR      r0, r0, #8
	STR      r0, [sp, #0x6c]
	MOV      r0, sp
	BL       |loc_08004098|
|loc_0800E66A|
	ADD      sp, #0x7c
	POP      {r4, r5, pc}
|sub_0800E66E|
|unk_0800E66E|
		LDR r0, [pc, #0x44]
		BX       lr
