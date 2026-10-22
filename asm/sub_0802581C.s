	CODE16
|sub_0802581C|
|unk_0802581C|
		LDR r2, [sp, #0xe4]
		CMP r1, r2
		BGE      |loc_08025824|
		STR r1, [r7]
|loc_08025824|
		LDR r1, [r0, #4]
		LDR r2, [r7, #4]
		CMP r1, r2
		BGE      |loc_0802582E|
		STR r1, [r7, #4]
|loc_0802582E|
		LDR r1, [r0, #8]
		LDR r2, [r7, #8]
		CMP r1, r2
		BLE      |loc_08025838|
		STR r1, [r7, #8]
|loc_08025838|
		LDR r1, [r0, #0xc]
		LDR r2, [r7, #0xc]
		CMP r1, r2
		BLE      |loc_08025842|
		STR r1, [r7, #0xc]
|loc_08025842|
|unk_08025842|
; cited by 0x003FCB34 (a pool word names 0x08025848)
		LDR r3, [pc, #0x29c]
		LDR r1, [r3, #0x10]
		LDRB r1, [r1]
		LDRB r2, [r5]
		CMP r1, r2
		BNE      |loc_0802585A|
		LDR r1, [r3, #0x10]
		LDRB r1, [r1, #1]
		LDRB r2, [r5, #1]
		CMP r1, r2
		BNE      |loc_0802585A|
		STR r5, [sp, #0xe0]
|loc_0802585A|
		LDR r1, [r0, #0xc]
		LDR r2, [r0, #4]
		CMP r1, r2
		DCW     0xDD17
		LDR r1, [r0]
		LDR r3, [r0, #8]
		CMP r3, r1
		DCW     0xDD0F
		LSL r3, r2, #8
		ADD r5, r3, r4
		LDRH r3, [r6]
		ADD r6, #2
		CMP r3, #0
		DCW     0xE001
|loc_08025876|
|unk_08025876|
		B        |loc_08025A9A|
|loc_08025878|
|unk_08025878|
; cited by 0x080256F6 (a pc-relative load targets 0x08025AD4)
		B        |loc_080258A4|
		BEQ      |loc_08025882|
		LSL r7, r1, #1
		ADD r7, r5, r7
		STRH r3, [r7, #0xc]
|loc_08025882|
		LDR r3, [r0, #8]
		ADD r1, #1
		CMP r3, r1
		DCW     0xDCF1
		LDR r1, [r0, #0xc]
		ADD r2, #1
		CMP r1, r2
		DCW     0xDCE7
		LDR r0, [sp, #0xe8]
		MOV r1, ip
		LDR r0, [r0]
		ADD r1, #1
		LDR r0, [r0, #0x14]
		MOV ip, r1
		CMP r0, r1
		BLE      |loc_080258A4|
		DCW     0xE77A
