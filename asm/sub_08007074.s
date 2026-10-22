	CODE16
|sub_08007074|
	PUSH     {r4, r5, r6, r7, lr}
	MOV      r5, #0xff
	ADD      r5, #1
	CMP      r3, r5
	LDR      r4, [pc, #0xe4]
	BLE      |loc_08007084|
	ADD      r3, r5, #0
	B        |loc_0800708A|
|loc_08007084|
	CMP      r3, #0
	BGE      |loc_0800708A|
	MOV      r3, #0
|loc_0800708A|
	MUL      r2, r3
	ADD      r7, r2, #0
	MUL      r0, r3
	MUL      r1, r3
	MOV      lr, r1
	MOV      ip, r0
	MOV      r2, #5
	LSL      r2, r2, #0x18
	MOV      r0, #1
	SUB      r1, r5, r3
	LSL      r0, r0, #9
|loc_080070A0|
	LDRB     r5, [r4, #1]
	LDRB     r3, [r4]
	LDRB     r6, [r4, #2]
	MUL      r5, r1
	ADD      r5, lr
	MUL      r3, r1
	ADD      r3, ip
	ASR      r5, r5, #0xb
	MUL      r6, r1
	ADD      r6, r6, r7
	LSL      r5, r5, #5
	ASR      r3, r3, #0xb
	ORR      r3, r5
	ASR      r6, r6, #0xb
	LSL      r5, r6, #0xa
	ORR      r3, r5
	STRH     r3, [r2]
	ADD      r2, #2
	ADD      r4, #3
	SUB      r0, #1
	BNE      |loc_080070A0|
	POP      {r4, r5, r6, r7, pc}
	MOV      r1, #0xff
	ADD      r1, #1
	SUB      r3, r1, r0
	MOV      r1, #0
	MOV      r2, #0
	MOV      r0, #0
	B        |sub_08007074|
	ADD      r3, r0, #0
	MOV      r2, #0xff
	MOV      r1, #0xff
	MOV      r0, #0xff
	B        |sub_08007074|
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	MOV      r5, #0xff
	ADD      r0, r0, r1
	ADD      r5, #1
	SUB      r3, r5, r0
	STR      r0, [r4, #4]
	MOV      r1, #0
	MOV      r2, #0
	MOV      r0, #0
	BL       |sub_08007074|
	LDR      r1, [r4, #4]
	MOV      r0, #1
	CMP      r1, r5
	BGE      |loc_08007114|
	MOV      r0, #0
|loc_08007114|
	POP      {r3, r4, r5, pc}
	LDR      r0, [pc, #0x4c]
	PUSH     {r3, lr}
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |sub_08011A1E|
	POP      {r3, pc}
	LDR      r0, [pc, #0x3c]
	PUSH     {r3, lr}
	SUB      r0, #4
	LDR      r0, [r0]
	BL       |sub_08011A1E|
	POP      {r3, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	ADD      r4, r0, #0
	LDR      r2, [r1, #0x2c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r1, r4, #4
	LDMIA    r1!, {r0, r1}
	MOV      r2, #0
	SUB      r0, r0, r1
	MOV      r1, #0xff
	ADD      r1, #1
	SUB      r3, r1, r0
	MOV      r1, #0
	STR      r0, [r4, #4]
	MOV      r0, #0
	BL       |sub_08007074|
	LDR      r1, [r4, #4]
	MOV      r0, #1
	CMP      r1, #0
	BLE      |loc_08007162|
	MOV      r0, #0
|loc_08007162|
	POP      {r4, pc}
|sub_08007164|
|unk_08007164|
	INCBIN	baserom.gba_0x7164_0x7166.extracted
