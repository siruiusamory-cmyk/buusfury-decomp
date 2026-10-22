	CODE16
|loc_08009324|
	PUSH     {r4, r5, r6, r7, lr}
	LDR      r3, [r0]
	MOV      lr, r1
	CMP      r3, #0
	BLT      |loc_08009344|
	LDR      r2, [r0, #4]
	CMP      r2, #0
	BLT      |loc_08009344|
	MOV      r4, #1
	LDR      r1, [r0, #8]
	LSL      r4, r4, #0xb
	CMP      r1, r4
	BGT      |loc_08009344|
	LDR      r0, [r0, #0xc]
	CMP      r0, r4
	BLE      |loc_08009348|
|loc_08009344|
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_08009348|
	ASR      r3, r3, #3
	ADD      r1, #7
	ADD      r0, #7
	ASR      r6, r0, #3
	ASR      r4, r1, #3
	ASR      r2, r2, #3
	CMP      r6, r2
	MOV      ip, r3
	BLE      |loc_08009388|
|loc_0800935A|
	LSL      r0, r2, #5
	ADD      r5, r0, #0
	ADD      r5, lr
	MOV      r0, ip
	CMP      r4, ip
	BLE      |loc_08009382|
|loc_08009366|
	ASR      r1, r0, #5
	LSL      r1, r1, #2
	LDR      r3, [r5, r1]
	LSL      r7, r0, #0x1b
	LSR      r7, r7, #0x1b
	MOV      r1, #1
	LSL      r1, r7
	AND      r3, r1
	BNE      |loc_0800937C|
	MOV      r0, #0
	POP      {r4, r5, r6, r7, pc}
|loc_0800937C|
	ADD      r0, #1
	CMP      r4, r0
	BGT      |loc_08009366|
|loc_08009382|
	ADD      r2, #1
	CMP      r6, r2
	BGT      |loc_0800935A|
|loc_08009388|
	MOV      r0, #1
	POP      {r4, r5, r6, r7, pc}
