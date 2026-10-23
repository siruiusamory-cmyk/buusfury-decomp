	CODE16
|sub_08010CA4|
	PUSH     {r3, lr}
	LDR      r0, [r0, #0x24]
	LDR      r2, [r0]
	LDR      r3, [r2, #4]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #1
	LSL      r0, r0, #9
	ADD      r0, r4, r0
	LDR      r0, [r0, #0x24]
	LDR      r2, [r0]
	LDR      r3, [r2]
	ADD      r3, r3, r2
	ADD      r2, r1, #0
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r4, pc}
|sub_08010CD0|
|unk_08010CD0|
		PUSH {r3, r4, r5, lr}
		ADD r4, r0, #0
		ADD r5, r1, #0
		BL       |loc_0800E97E|
		LDR r1, [r4]
		MOV r2, #0x80
		LDR r2, [r2, r1]
		ADD r0, r4, #0
		ADD r1, r2, r1
		BL       |inc_0x042118_0x049114| + 0x498a
		ADD r1, r0, #0
		LDR r3, [pc, #0x244]
		LDR r2, [r5]
		ADD r1, #0x16
		ADD r2, r2, r3
		ASR r2, r2, #0xa
		MOV r3, #0
		LDRSH r4, [r1, r3]
		ADD r4, r4, r2
		MOV r3, #2
		LDRSH r5, [r1, r3]
		CMP r4, r5
		BLE      |sub_08010D08|
		LDRH r2, [r1, #2]
		STRH r2, [r1]
		B        |inc_0x0158_0x143f2| + 0x10bc2
