	CODE16
|sub_08007CCC|
|unk_08007CCC|
		MOV r1, #0
|loc_08007CCE|
		ADD r3, r4, r1
		ADD r3, #0x20
		LDRB r7, [r3]
		CMP r7, ip
		BNE      |loc_08007CF0|
		MOV r7, #1
		LSL r7, r1
		ORR r6, r7
		MOV r7, #1
		LSL r1, r1, #0xb
		ADD r1, r1, r4
		LSL r7, r0
		ORR r5, r7
		ADD r1, #0x4c
		ADD r2, r2, r4
		STR r1, [r2, #0x10]
		B        |loc_08007CFE|
|loc_08007CF0|
		ADD r1, #1
		CMP r1, #4
		BLT      |loc_08007CCE|
		B        |loc_08007CFE|
|loc_08007CF8|
|unk_08007CF8|
		LDR r1, [pc, #0x170]
		ADD r2, r2, r4
		STR r1, [r2, #0x10]
|loc_08007CFE|
|unk_08007CFE|
		ADD r0, #1
		CMP r0, #4
		BLT      |inc_0x0158_0x143f2| + 0x7b4a
		MOV r7, #0
|loc_08007D06|
|unk_08007D06|
		MOV r2, #1
		ADD r0, r2, #0
		LSL r0, r7
		AND r0, r5
		BNE      |inc_0x0158_0x143f2| + 0x7c10
		MOV r1, #0
|loc_08007D12|
|unk_08007D12|
		ADD r0, r2, #0
		LSL r0, r1
		AND r0, r6
		BNE      |inc_0x0158_0x143f2| + 0x7c0a
		LDR r3, [pc, #0x15c]
		LSL r2, r1
		ORR r6, r2
		LSL r0, r7, #2
		MOV ip, r0
		ADD r2, r4, r1
		ADD r3, sp
		LDR r0, [r3, r0]
		ADD r2, #0x20
		STRB r0, [r2]
		MOV r3, #1
		LSL r1, r1, #0xb
		ADD r1, r1, r4
		LSL r3, r3, #0xb
		ADD r3, sp
		ADD r1, #0x4c
		MOV r2, ip
		ADD r2, r2, r4
		STR r1, [r3, #0x14]
		STR r1, [r2, #0x10]
		LDR r1, [r4, #8]
		LSL r0, r0, #2
		ADD r0, r1, r0
		LDR r0, [r0, #0x18]
		ADD r1, sp, #4
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r2, #1
		LSL r2, r2, #0xb
		ADD r3, r2, #0
		ADD r3, sp
		LDR r0, [r3, #0x14]
		ADD r1, sp, #4
	INCBIN  baserom.gba_0x7d5c_0x7d5e.extracted
|sub_08007D5E|
|unk_08007D5E|
	INCBIN	baserom.gba_0x7d5e_0x7d62.extracted
	ADD      r1, #1
	CMP      r1, #4
	BLT      |loc_08007D12|
	ADD      r7, #1
	CMP      r7, #4
	BLT      |loc_08007D06|
	MOV      r3, #1
	LSL      r3, r3, #0xb
	ADD      r3, sp
	LDR      r2, [r3, #0x20]
	LDMIA    r2!, {r1, r2}
	STR      r1, [r4, #0x24]
	STR      r2, [r4, #0x28]
	LDR      r2, [r3, #0x20]
	SUB      r3, #0x80
	LDR      r1, [r2]
	LDR      r2, [r2, #4]
	LSL      r1, r1, #8
	STR      r1, [r3, #0x7c]
	ADD      r3, #0x80
	LSL      r2, r2, #8
	STR      r2, [r3]
	ADD      r4, #0x2c
	LDR      r3, [pc, #0xe8]
	STMIA    r4!, {r1, r2}
	ADD      sp, r3
	POP      {r4, r5, r6, r7, pc}
