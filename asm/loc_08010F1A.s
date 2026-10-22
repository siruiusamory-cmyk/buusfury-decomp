	CODE16
|loc_08010F1A|
		ADD r2, r5, #0
		ADD r1, r7, #0
		ADD r0, r4, #0
		BL       |inc_0x0158_0x143f2| + 0x10180
		B        |inc_0x0158_0x143f2| + 0x10cbe
|unk_08010F26|
	INCBIN  baserom.gba_0x10f26_0x10f40.extracted
		LDRB r1, [r5]
		CMP r1, #0
		BEQ      |loc_08010F4A|
		CMP r1, #2
		BNE      |loc_08010F9A|
|loc_08010F4A|
		ADD r5, r0, #0
		MOV r0, sp
		ADD r1, r4, #0
		BL       |loc_0800FE78|
		LDR r0, [r5]
		LDR r1, [sp, #8]
		CMP r0, r1
		BGE      |loc_08010F9A|
		LDR r0, [sp]
		LDR r1, [r5, #8]
		CMP r0, r1
		BGE      |loc_08010F9A|
		LDR r0, [r5, #4]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_08010F9A|
		LDR r0, [sp, #4]
		LDR r1, [r5, #0xc]
		CMP r0, r1
		BGE      |loc_08010F9A|
		LDR r0, [sp, #0x10]
		LDR r0, [r0, #0xc]
		CMP r0, #0
		BEQ      |loc_08010F96|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |sub_0800E9D8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x58]
		B        |loc_08010F8E|
		B        |loc_08010FF8|
|loc_08010F8E|
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |loc_08046AA4|
|loc_08010F96|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10cbe
|loc_08010F9A|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10cbe
		LDRB r1, [r5]
		CMP r1, #0
		BEQ      |loc_08010FA8|
		CMP r1, #2
		BNE      |loc_08010FF4|
|loc_08010FA8|
		ADD r5, r0, #0
		MOV r0, sp
		ADD r1, r4, #0
		BL       |sub_0800FDFA|
		LDR r0, [r5]
		LDR r1, [sp, #8]
		CMP r0, r1
		BGE      |loc_08010FF4|
		LDR r0, [sp]
		LDR r1, [r5, #8]
		CMP r0, r1
		BGE      |loc_08010FF4|
		LDR r0, [r5, #4]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_08010FF4|
		LDR r0, [sp, #4]
		LDR r1, [r5, #0xc]
		CMP r0, r1
		BGE      |loc_08010FF4|
		LDR r0, [sp, #0x10]
		LDR r0, [r0, #0xc]
		CMP r0, #0
		BEQ      |loc_08010FF0|
		ADD r1, r6, #0
		ADD r0, r4, #0
		BL       |sub_0800E9D8|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #0x58]
		ADD r2, r2, r1
		ADD r1, r6, #0
		BL       |loc_08046AA4|
|loc_08010FF0|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10cbe
|loc_08010FF4|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10cbe
|loc_08010FF8|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10cbe
|unk_08010FFC|
	INCBIN  baserom.gba_0x10ffc_0x11014.extracted
		LDRB r1, [r5]
		CMP r1, #0
		BEQ      |loc_0801101E|
		CMP r1, #2
		BNE      |loc_0801104C|
|loc_0801101E|
		ADD r5, r0, #0
		MOV r0, sp
		ADD r1, r4, #0
		BL       |loc_0800FE78|
		LDR r0, [r5]
		LDR r1, [sp, #8]
		CMP r0, r1
		BGE      |loc_0801104C|
		LDR r0, [sp]
		LDR r1, [r5, #8]
		CMP r0, r1
		BGE      |loc_0801104C|
		LDR r0, [r5, #4]
		LDR r1, [sp, #0xc]
		CMP r0, r1
		BGE      |loc_0801104C|
		LDR r0, [sp, #4]
		LDR r1, [r5, #0xc]
		CMP r0, r1
		BGE      |loc_0801104C|
		MOV r0, #1
		B        |inc_0x0158_0x143f2| + 0x10cbe
|loc_0801104C|
		MOV r0, #0
		B        |inc_0x0158_0x143f2| + 0x10cbe
