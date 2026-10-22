	CODE16
|sub_08034120|
|unk_08034120|
		MOV r0, #0
		B        |inc_0x331c0_0x341c0| + 0xf5e
		PUSH {r4, r5, r6, r7, lr}
		ADD r4, r0, #0
		LDR r1, [r4, #4]
		LDR r2, [pc, #0x154]
		ADD r1, #0xff
		ADD r1, #0xad
		LDR r1, [r1]
		LDR r5, [r2]
		SUB sp, #0xc
		STR r1, [r5, #0xc]
		LDR r0, [r0, #4]
		LDR r1, [r4, #8]
		ADD r0, #0xff
		ADD r0, #0xa9
		LDR r0, [r0]
		CMP r1, r0
		BEQ      |loc_0803418A|
		STR r0, [r4, #8]
		LDR r0, [r4, #4]
		ADD r0, #0xff
		ADD r0, #0x81
		LDR r0, [r0, #0x28]
		ASR r6, r0, #0x1f
		ADD r3, r6, #0
		ADD r7, r0, #0
		ADD r2, r0, #0
		ADD r1, r6, #0
		BL       |__16_ll_mul|
		DCW     0xA249
		LDMIA r2!, {r2, r3}
		BL       |sub_08046BA4|
		STR r1, [sp, #8]
		ADD r1, r6, #0
		STR r0, [sp, #4]
		MOV r2, #0xda
		ADD r0, r7, #0
		BL       |sub_08046B64|
		ADD r3, sp, #4
		LDMIA r3!, {r2, r3}
		ADD r0, r0, r2
		ADC r1, r3
		LDR r2, [pc, #0x10c]
		BL       |inc_0x042118_0x049114| + 0x4a00
		MOV r2, #0xa
		BL       |__16_ll_sshift_r|
		STR r0, [r5, #0x10]
|loc_0803418A|
		LDR r1, [r5, #0x10]
		ASR r2, r1, #0xa
		ADD r3, r2, #0
		LSL r0, r2, #0x18
		LSR r2, r0, #0x16
		LDR r0, [pc, #0xf8]
		LSL r1, r1, #0x16
		LDR r6, [r0, r2]
		ADD r2, r3, #1
		LSL r2, r2, #0x18
		LSR r2, r2, #0x16
		LDR r2, [r0, r2]
		LSR r1, r1, #0x16
		MOV ip, r2
		MOV r2, #1
		LSL r2, r2, #0xa
		SUB r2, r2, r1
		ADD r7, r2, #0
		MUL r7, r6
		MOV r6, ip
		MUL r6, r1
		ADD r6, r7, r6
		ASR r6, r6, #0x10
		MOV ip, r6
		ADD r3, #0x40
		LSL r6, r3, #0x18
		ADD r3, #1