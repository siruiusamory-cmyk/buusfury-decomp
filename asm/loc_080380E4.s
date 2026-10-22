	CODE16
|loc_080380E4|
		EOR r1, r2
		CMP r0, r1
		BNE      |loc_080380EE|
		STRB r2, [r4, #0x10]
		B        |loc_080380A6|
|loc_080380EE|
		ADD r2, r5, #0
		ADD r2, #0xff
		LDR r0, [pc, #0x88]
		ADD r2, #0x9d
		ADD r1, r6, #0
		LDR r0, [r0, #4]
		BL       |loc_080097C2|
		CMP r0, #0
		BEQ      |loc_0803811E|
		LDR r1, [pc, #0x98]
		ADD r0, r5, #0
		BL       |loc_0800ED18|
		LDR r1, [r4, #0x34]
		MOV r0, #0xff
		ADD r0, #0xa1
		LSL r1, r1, #8
		STR r1, [r0, r5]
		LDR r1, [r4, #0x38]
		ADD r0, #4
		LSL r1, r1, #8
		STR r1, [r0, r5]
		B        |loc_080380A6|
|loc_0803811E|
		MOV r2, #1
		STRB r2, [r4, #0x10]
		B        |loc_080380A6|
|loc_08038124|
|unk_08038124|
		LDR r0, [r4, #0x3c]
		CMP r0, #0x50
		BGE      |loc_08038130|
		ADD r0, #4
		STR r0, [r4, #0x3c]
		B        |loc_080380A6|
|loc_08038130|
		MOV r2, #1
		STRB r2, [r4, #0x10]
		B        |loc_080380A6|
|loc_08038136|
|unk_08038136|
; cited by 0x08037EC4 (a pc-relative load targets 0x08038178)
		MOV r2, #1
		STRB r2, [r4, #0x10]
		B        |loc_080380A6|
		LDR r0, [r7]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
		MOV r2, #1
		STRB r2, [r4, #0x10]
|loc_0803814E|
		LDR r0, [r4, #0x3c]
		SUB r0, #4
		STR r0, [r4, #0x3c]
		CMP r0, #0
		BGT      |loc_080380A6|
		LDRB r0, [r4, #0x10]
		CMP r0, #2
		BNE      |loc_0803816C|
		LDR r0, [r7]
		LDR r1, [r0]
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #0
		BL       |loc_08046AA4|
|loc_0803816C|
		LDR r0, [pc, #0xc]
		ADD r1, r4, #0
		LDR r0, [r0]
		BL       |loc_08011944|
		B        |loc_080380A6|
		DCD     0x08049680
		DCD     0x0876CCE0
	INCBIN  baserom.gba_0x38180_0x38192.extracted
