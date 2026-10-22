	CODE16
|sub_08042F4C|
|unk_08042F4C|
; cited by 0x08042BFA (a pc-relative load targets 0x08042FAC)
		LDRB r0, [r7, #4]
		AND r0, r6
		BEQ      |loc_08042FFE|
		LDR r1, [pc, #0x60]
		LSL r0, r4, #2
		LDR r0, [r1, r0]
		LDRH r1, [r0, #0x34]
		CMP r1, #0x46
		BNE      |sub_08042FC2|
		ADD r0, #0x60
		LDRB r0, [r0, #1]
		CMP r0, #1
		BNE      |loc_08042FD6|
		LDR r1, [pc, #0x44]
		LDR r2, [pc, #0x44]
		LDR r0, [r1, #0x20]
		LDR r2, [r2]
		LSL r1, r4, #5
		MOV r5, #2
		ADD r3, r1, r2
		B        |loc_08042F98|
|loc_08042F76|
		LDRH r2, [r3, #0x18]
		CMP r2, r1
		BNE      |loc_08042F96|
		LDR r1, [pc, #0x2c]
		LDRB r0, [r1]
		ORR r0, r6
		STRB r0, [r1]
		LDRB r0, [r1, #1]
		ADD r0, #1
		STRB r0, [r1, #1]
		LDR r0, [sp, #4]
		ORR r0, r6
		STR r0, [sp, #4]
		MOV r0, #1
		ORR r5, r0
		B        |loc_08042FA0|
|loc_08042F96|
		ADD r0, #2
|loc_08042F98|
		LDRH r1, [r0]
		LDR r2, [pc, #0x20]
		CMP r1, r2
		BNE      |loc_08042F76|
|loc_08042FA0|
		LSL r0, r5, #0x1f
		BMI      |loc_08042FD6|
		MOV r0, #4
		ORR r5, r0
		B        |loc_08042FD6|
	INCBIN  baserom.gba_0x42faa_0x42fac.extracted
		DCD     0x03004CC8
		DCD     0x0300525C
		DCD     0x03005268
	INCBIN  baserom.gba_0x42fb8_0x42fbc.extracted
		DCD     0x0000FFFF
|loc_08042FC0|
|unk_08042FC0|
		B        |loc_0804306C|
