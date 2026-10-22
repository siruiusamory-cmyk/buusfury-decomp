	CODE16
|sub_08024E98|
|unk_08024E98|
		ADR      r1, |loc_08024F34|
|loc_08024E9A|
|unk_08024E9A|
		ADD r0, r4, #0
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x20
		STR r0, [r4, #8]
		LDR r0, [sp, #4]
		ADD r3, r0, #1
		BNE      |loc_08024EB2|
		ADR      r1, |loc_08024F2C|
		B        |loc_08024EB4|
|loc_08024EB2|
		ADR      r1, |loc_08024F34|
|loc_08024EB4|
		ADD r0, r4, #0
		LDR r2, [sp, #4]
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x2a
		STR r0, [r4, #8]
		ADD r3, r6, #1
		BNE      |loc_08024ECC|
		ADR      r1, |loc_08024F2C|
		B        |loc_08024ECE|
|loc_08024ECC|
		ADR      r1, |loc_08024F34|
|loc_08024ECE|
		ADD r2, r6, #0
		ADD r0, r4, #0
		BL       |sub_0803DC96|
		MOV r0, #0xa0
		STR r0, [r4, #4]
		MOV r0, #0x34
		STR r0, [r4, #8]
		ADD r3, r7, #1
		BNE      |sub_08024EE6|
		ADR      r1, |loc_08024F2C|
		DCW     0xE000
