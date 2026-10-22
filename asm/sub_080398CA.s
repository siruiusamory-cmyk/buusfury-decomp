	CODE16
|sub_080398CA|
	LSR      r7, r6, #1
	ADD      r2, #0xb4
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
|sub_080398DC|
|unk_080398DC|
		PUSH {r4}
		LDRH r2, [r1, #0x12]
		SUB sp, #8
		MOV r3, #2
		LSR r0, r2, #3
		STR r0, [sp, #4]
		CMP r0, #2
		STR r3, [sp]
		BGE      |loc_080398F2|
		ADD r0, sp, #4
		B        |loc_080398F4|
|loc_080398F2|
		MOV r0, sp
|loc_080398F4|
		LDR r0, [r0]
		LSL r3, r0, #0x18
		ADD r0, r1, #0
		ADD r0, #0xff
		LSR r3, r3, #0x18
		ADD r0, #0x61
		CMP r3, #0
		STRB r3, [r1, #0x11]
		BEQ      |inc_0x351c0_0x3d4d0| + 0x4764
		LSL r3, r2, #2
		SUB r2, r2, r3
		ADD r2, #0x18
		STR r2, [sp, #4]
		MOV r2, #0xc7
		MVN r2, r2
		LDR r3, [sp, #4]
		STR r2, [sp]
		CMP r3, r2
		BLE      |sub_0803991E|
		ADD r2, sp, #4
		B        |inc_0x351c0_0x3d4d0| + 0x4760
