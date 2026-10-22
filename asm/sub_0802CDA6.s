	CODE16
|sub_0802CDA6|
|unk_0802CDA6|
		MOV r0, #0xb2
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CDC4|
		MOV r0, #0xff
		ADD r0, #2
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CDA4|
|loc_0802CDC4|
		MOV r0, #0xac
		LDR r5, [r4, #0x58]
		BL       |inc_0x0158_0x143f2|
		CMP r5, r0
		BNE      |loc_0802CDA4|
		MOV r0, #0x56
		BL       |inc_0x0158_0x143f2|
		ADD r1, r0, #0
		ADD r0, r4, #0
		BL       |loc_0800EDF8|
		B        |loc_0802CDA4|
	INCBIN  baserom.gba_0x2cde0_0x2cde4.extracted
