	CODE16
|loc_08009930|
	PUSH     {r0, r1, r2, r4, r5, r6, r7, lr}
	LDR      r3, [r0]
	MOV      r4, #0
	ADD      r1, r4, #0
	CMP      r3, #0
	BLT      |loc_0800993E|
	ASR      r1, r3, #3
|loc_0800993E|
	MOV      lr, r1
	LDR      r1, [r0, #4]
	CMP      r1, #0
	BLT      |loc_08009948|
	ASR      r4, r1, #3
|loc_08009948|
	MOV      r1, #0xff
	ADD      r1, #1
	LDR      r5, [r0, #8]
	ADD      r6, r1, #0
	LSL      r3, r1, #3
	CMP      r5, r3
	BGE      |loc_0800995A|
	ADD      r5, #7
	ASR      r6, r5, #3
|loc_0800995A|
	LDR      r0, [r0, #0xc]
	CMP      r0, r3
	BGE      |loc_08009964|
	ADD      r0, #7
	ASR      r1, r0, #3
|loc_08009964|
	MOV      ip, r1
	CMP      r1, r4
	BLE      |loc_080099A0|
|loc_0800996A|
	LDR      r1, [sp, #4]
	LSL      r0, r4, #5
	ADD      r7, r0, r1
	MOV      r0, lr
	CMP      r6, lr
	BLE      |loc_0800999A|
|loc_08009976|
	LSL      r5, r0, #0x1b
	LSR      r5, r5, #0x1b
	ASR      r1, r0, #5
	MOV      r3, #1
	LSL      r1, r1, #2
	ADD      r1, r1, r7
	LSL      r3, r5
	LDR      r5, [r1]
	CMP      r2, #0
	BEQ      |loc_08009990|
	ORR      r3, r5
	STR      r3, [r1]
	B        |loc_08009994|
|loc_08009990|
	BIC      r5, r3
	STR      r5, [r1]
|loc_08009994|
	ADD      r0, #1
	CMP      r6, r0
	BGT      |loc_08009976|
|loc_0800999A|
	ADD      r4, #1
	CMP      ip, r4
	BGT      |loc_0800996A|
|loc_080099A0|
	ADD      sp, #0xc
	POP      {r4, r5, r6, r7, pc}
	PUSH     {r3, lr}
	ADD      r3, r0, #0
	LDR      r0, [pc, #0x12c]
	ASR      r2, r2, #4
	ADD      r3, #0xb4
	LDR      r0, [r0]
	BL       |loc_080092EA|
	POP      {r3, pc}
