	CODE16
|sub_08035BD6|
	LSL      r0, r0, #0xc
	MOV      r2, #0
	STRH     r2, [r1, #0x12]
	MOV      r0, #0x38
	STRB     r0, [r1, #8]
	STRB     r2, [r1, #0x11]
	BX       lr
|sub_08035BE4|
|unk_08035BE4|
		PUSH {r4, r5, r6, r7, lr}
		LDRH r0, [r1, #0x12]
		SUB sp, #0x2c
		MOV r5, #0
		ADD r0, #1
		LSL r0, r0, #0x10
		LSR r0, r0, #0x10
		ADD r4, r1, #0
		CMP r0, #8
		STRH r0, [r1, #0x12]
		BHS      |loc_08035BFE|
		LSR r5, r0, #2
		B        |loc_08035D92|
|loc_08035BFE|
		ADD r1, r4, #0
		ADD r1, #0xff
		ADD r1, #0x61
		CMP r0, #0x38
		BHS      |loc_08035C18|
		ADD r0, #8
		LSL r0, r0, #0x1c
		LSR r5, r0, #0x1e
		LDRH r0, [r1, #0x16]
		ADD r5, #2
		SUB r0, #8
		STRH r0, [r1, #0x16]
		B        |loc_08035D92|
|loc_08035C18|
		CMP r0, #0xc8
		BHS      |loc_08035CB6|
		ADD r1, r4, #0
		ADD r0, sp, #0x14
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		ADD r1, r0, r1
		LDR r0, [sp, #0x18]
		STR r1, [sp, #0xc]
		ASR r1, r1, #1
		ADD r0, r0, r2
		STR r0, [sp, #0x10]
		ASR r0, r0, #1
		STR r0, [sp, #0x10]
		STR r0, [sp, #0x28]
		LDR r0, [pc, #0x190]
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x24]
		LDR r1, [r0]
		ADD r0, sp, #0xc
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0xc]
		LDR r1, [sp, #0x14]
		LDR r2, [sp, #0x18]
		ADD r1, r0, r1
		LDR r0, [sp, #0x10]
		STR r1, [sp, #4]
		ADD r0, r0, r2
		STR r0, [sp, #8]
		ASR r0, r0, #1
		STR r0, [sp, #8]
		STR r0, [sp, #0x20]
		ASR r1, r1, #1
		STR r1, [sp, #4]
		ADD r0, r4, #0
		ADD r0, #0xff
		LDR r2, [sp, #0x24]
		ADD r0, #0xa1
		CMP r1, r2
		STR r1, [sp, #0x1c]
		BLE      |loc_08035C7C|
		LDR r1, [r0]
		ADD r1, #0xff
		ADD r1, #1
		STR r1, [r0]
		B        |loc_08035C8C|
|loc_08035C7C|
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x24]
		CMP r1, r2
		BGE      |loc_08035C8C|
		LDR r1, [r0]
		SUB r1, #0xff
		SUB r1, #1
		STR r1, [r0]
|loc_08035C8C|
		ADD r0, r4, #0
		ADD r0, #0xff
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x28]
		ADD r0, #0xa5
		CMP r1, r2
		BLE      |loc_08035CA4|
		LDR r1, [r0]
		ADD r1, #0xff
		ADD r1, #1
		STR r1, [r0]
		B        |loc_08035D92|
|loc_08035CA4|
		LDR r1, [sp, #0x20]
		LDR r2, [sp, #0x28]
		CMP r1, r2
		BGE      |loc_08035D92|
		LDR r1, [r0]
		SUB r1, #0xff
		SUB r1, #1
		STR r1, [r0]
		B        |loc_08035D92|
|loc_08035CB6|
		CMP r0, #0xf8
		BHS      |loc_08035CC8|
		LSL r0, r0, #0x1c
		LSR r5, r0, #0x1e
		LDRH r0, [r1, #0x16]
		ADD r5, #2
		ADD r0, #8
		STRH r0, [r1, #0x16]
		B        |loc_08035D92|
|loc_08035CC8|
		ADD r1, r4, #0
		ADD r0, sp, #0x14
		BL       |Object_WriteBounds1|
		LDR r0, [sp, #0x14]
		LDR r1, [sp, #0x1c]
		LDR r2, [sp, #0x20]
		ADD r1, r0, r1
		LDR r0, [sp, #0x18]
		STR r1, [sp, #0xc]
		ASR r1, r1, #1
		ADD r0, r0, r2
		STR r0, [sp, #0x10]
		ASR r0, r0, #1
		STR r0, [sp, #0x10]
		STR r0, [sp, #0x28]
		LDR r0, [pc, #0xe8]
		STR r1, [sp, #0xc]
		STR r1, [sp, #0x24]
		LDR r0, [r0]
		BL       |loc_080116FC|
		MOV r7, #1
		LSL r7, r7, #0xa
		CMP r0, r7
		BLT      |loc_08035D34|
		LSL r6, r7, #2
		ADD r0, r6, #0
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r2, [sp, #0x24]
		LDR r1, [sp, #0x28]
		ADD r2, #0xf
		ADD r0, r0, r6
		ADD r1, #5
		STR r2, [sp, #0x14]
		STR r2, [sp, #0x1c]
		MOV r2, #0x37
		STR r1, [sp, #0x20]
		STR r0, [sp]
		STR r2, [sp, #8]
		STR r1, [sp, #0x18]
		MOV r3, #4
		MOV r0, #0
		ADD r1, sp, #0x1c
		LDR r2, [pc, #0xb4]
		STR r7, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [pc, #0xa4]
		LDR r0, [r0]
		BL       |List_Append|
|loc_08035D34|
		LDR r6, [pc, #0x9c]
		LDR r0, [r6]
		BL       |loc_080116FC|
		CMP r0, r7
		BLT      |loc_08035D7A|
		MOV r0, #1
		LSL r0, r0, #0xc
		BL       |inc_0x03d784_0x041118| + 0x2348
		LDR r2, [sp, #0x24]
		MOV r1, #1
		SUB r2, #0xc
		LSL r1, r1, #0xc
		ADD r0, r0, r1
		LDR r1, [sp, #0x28]
		STR r2, [sp, #0x14]
		ADD r1, #0xa
		STR r2, [sp, #0x1c]
		MOV r2, #0x37
		STR r1, [sp, #0x20]
		STR r0, [sp]
		STR r2, [sp, #8]
		STR r1, [sp, #0x18]
		MOV r3, #4
		MOV r0, #0
		ADD r1, sp, #0x1c
		LDR r2, [pc, #0x6c]
		STR r7, [sp, #4]
		BL       |loc_0802A81C|
		ADD r1, r0, #0
		LDR r0, [r6]
		BL       |List_Append|
|loc_08035D7A|
		LDR r6, [pc, #0x58]
