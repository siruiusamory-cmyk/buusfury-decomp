|Bios_CpuSet2|
	CODE16
|unk_08042AB8|
		MOV r0, #0
		ADD r3, sp, #0
		STRH r0, [r3]
		SWI 0xb
		MOV r1, #0xff
		LDR r0, [pc, #0xec]
		STRB r1, [r0, #6]
		ADD r0, #0x40
		STMIA r0!, {r4, r5}
		LDR r0, [pc, #0xe8]
		BL       |inc_0x042118_0x049114| + 0x1748
		LDR r0, [pc, #0xe4]
		BL       |inc_0x042118_0x049114| + 0x1772
		MOV r0, #0
		B        |inc_0x042118_0x049114| + 0x99e
