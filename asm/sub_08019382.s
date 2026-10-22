	CODE16
|sub_08019382|
|unk_08019382|
; cited by 0x0043FC74 (a pool word names 0x08019384)
		LDR r3, [r2]
		CMP r3, #0
		BEQ      |loc_08019392|
|loc_08019388|
		LDR r2, [r2]
		ADD r2, #4
		LDR r3, [r2]
		CMP r3, #0
		BNE      |loc_08019388|
|loc_08019392|
		STR r1, [r2]
		LDR r0, [r0]
		CMP r0, #0
		BNE      |loc_08019380|
		MOV r0, #4
		DCD     0xF90CF024
		CMP r0, #0
		BEQ      |loc_080193A8|
		LDR r1, [pc, #0xc4]
		STR r1, [r0]
|loc_080193A8|
		BL       |inc_0x03d784_0x041118| + 0x11c
		B        |loc_08019380|
