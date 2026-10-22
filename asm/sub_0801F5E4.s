	CODE16
|sub_0801F5E4|
|unk_0801F5E4|
		LDRB r1, [r0, #5]
		LDR r0, [r7, #0xc]
		BL       |Object_AppendEntry1|
		B        |loc_0801F614|
|loc_0801F5EE|
|unk_0801F5EE|
		LDRB r2, [r0, #5]
		LDR r1, [r7, #0xc]
		LDR r0, [r0]
		ADD r1, r1, r2
		LDRB r2, [r1, #2]
		ADD r0, r2, r0
		MOV r2, #0xff
		ADD r2, #1
		CMP r0, r2
		BGE      |loc_0801F606|
		STRB r0, [r1, #2]
		B        |loc_0801F614|
|loc_0801F606|
		MOV r0, #0xff
		STRB r0, [r1, #2]
		B        |loc_0801F614|
