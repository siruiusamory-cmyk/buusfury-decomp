	CODE16
|sub_080020BE|
|unk_080020BE|
		MOV r0, #8
		DCD     0xFA7AF03B
		CMP r0, #0
		BEQ      |loc_080020CE|
		LDR r1, [pc, #0xb0]
		STMIA r0!, {r1, r4}
		SUB r0, #8
|loc_080020CE|
		ADD r1, r0, #0
		LDR r0, [r5, #0x20]
		BL       |loc_08021094|
		B        |inc_0x0158_0x143f2| + 0x1f64
|sub_080020D8|
	DCW      0x4822
