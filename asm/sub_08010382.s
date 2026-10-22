	CODE16
|sub_08010382|
	LSL      r0, r0, #0
	MOV      r7, #0x14
	LSR      r7, r0, #0x20
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	MOV      r0, #1
	STRB     r0, [r1, #0x10]
	BX       lr
	LDRH     r0, [r1, #0x12]
	ADD      r0, #1
	STRH     r0, [r1, #0x12]
	LSL      r0, r0, #0x1b
	LSR      r0, r0, #0x1e
	STRB     r0, [r1, #0x11]
	BX       lr
|sub_080103A6|
|unk_080103A6|
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r2, [pc, #0x1cc]
		ADD r5, r1, #0
		LDR r2, [r2]
		ADD r3, r5, #0
		LDRH r2, [r2, #2]
		ADD r4, r0, #0
		ADD r0, r1, #0
		ADD r3, #0xff
		MOV r6, #1
		LSL r7, r2, #0x1f
		LSR r7, r7, #0x1f
		LSL r6, r6, #0xa
		ADD r3, #0xa9
		MOV r1, #0
		CMP r7, #0
		BEQ      |loc_080103D8|
		MOV r7, #5
		LDR r2, [r3]
		LSL r7, r7, #0xa
		CMP r2, r7
		BLE      |loc_080103EC|
		SUB r2, r2, r6
		STR r2, [r3]
		B        |loc_080103EC|
|loc_080103D8|
		LSL r2, r2, #0x1e
		LSR r2, r2, #0x1f
		BEQ      |loc_080103EC|
		MOV r7, #0xf
		LDR r2, [r3]
		LSL r7, r7, #0xd
		CMP r2, r7
		BGE      |loc_080103EC|
		ADD r2, r2, r6
		STR r2, [r3]
|loc_080103EC|
		LDR r2, [pc, #0x188]
		LDR r2, [r2]
		LDRH r2, [r2, #2]
		LSL r3, r2, #0x1b
		LSR r3, r3, #0x1f
		BEQ      |loc_080103FC|
		MOV r1, #0x80
		B        |loc_08010406|
|loc_080103FC|
		LSL r3, r2, #0x1a
		LSR r3, r3, #0x1f
		BEQ      |loc_08010406|
		MOV r1, #0x7f
		MVN r1, r1
|loc_08010406|
		LSL r3, r2, #0x19
		LSR r3, r3, #0x1f
		BEQ      |loc_08010414|
		LDR r2, [r4, #8]
		ADD r2, #0xc0
		STR r2, [r4, #8]
		B        |loc_08010420|
|loc_08010414|
		LSL r2, r2, #0x18
		LSR r2, r2, #0x1f
		BEQ      |loc_08010420|
		LDR r2, [r4, #8]
		SUB r2, #0xc0
		STR r2, [r4, #8]
|loc_08010420|
		LDR r2, [r4, #8]
		LSL r3, r2, #4
		SUB r2, r3, r2
		ASR r3, r2, #0x1f
		LSR r3, r3, #0x1c
		ADD r2, r3, r2
		ASR r2, r2, #4
		STR r2, [r4, #8]
		CMP r2, #0
		BLE      |sub_0801043A|
		MOV r2, #0
		STR r2, [r4, #4]
		B        |loc_08010442|
