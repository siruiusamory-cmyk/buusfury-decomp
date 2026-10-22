	CODE16
|loc_08020B62|
		LDR r0, [r4, #0x18]
		ADD r0, #1
		ASR r6, r0, #2
		STR r0, [r4, #0x18]
		LDR r0, [r4, #0x1c]
		CMP r0, r6
		BNE      |loc_08020B72|
|loc_08020B70|
		DCW     0xE68F
|loc_08020B72|
		STR r6, [r4, #0x1c]
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #5]
		CMP r0, #0
		BEQ      |loc_08020BD0|
		CMP r0, #1
		BEQ      |loc_08020BD0|
		CMP r0, #2
		BNE      |loc_08020C26|
		LSL r7, r6, #0x1e
		LSR r7, r7, #0x1e
		CMP r7, #3
		BNE      |loc_08020B8E|
		MOV r7, #1
|loc_08020B8E|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x4c]
		LSL r2, r7, #6
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r1, r1, r2
		STR r2, [sp, #0x50]
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		LDRB r0, [r4, #0x11]
		CMP r0, #0
		LDRH r0, [r4, #0xc]
		BEQ      |loc_08020C28|
		LSL r0, r0, #5
		MOV r2, #1
		LSL r2, r2, #9
		ADD r0, r0, r5
		ADD r0, r0, r2
		LSL r2, r7, #0x1f
		LSR r2, r2, #0x1f
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #2
		ADD r1, r1, r2
		ADD r1, #0x80
		LDR r1, [r1]
		MOV r2, #0x80
		BL       |Thunk_VramCopy|
		B        |loc_08020C26|
|loc_08020BD0|
		LDRB r0, [r4, #0x10]
		LSL r7, r6, #0x1f
		LSR r7, r7, #0x1f
		MOV r3, #0
		CMP r0, #1
		BEQ      |loc_08020BDE|
		MOV r3, #0xd
|loc_08020BDE|
		ADD r0, r7, r3
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [r4, #0x4c]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDRB r2, [r1, #2]
		LDRB r0, [r1, #3]
		MUL r2, r0
		LDRH r0, [r4, #0xc]
		LDR r1, [r1, #8]
		LSL r0, r0, #5
		ADD r0, r0, r5
		BL       |Thunk_VramCopy|
		LDRB r1, [r4, #0x11]
		MOV r0, #0xa
		CMP r1, #0
		BNE      |loc_08020C06|
		MOV r0, #7
|loc_08020C06|
		ADD r0, r7, r0
		LSL r3, r0, #1
		ADD r0, r3, r0
		LDR r1, [r4, #0x4c]
		LSL r0, r0, #2
		ADD r1, r0, r1
		LDRH r0, [r4, #0xc]
		MOV r2, #1
		LSL r2, r2, #9
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, r0, r2
		LSR r2, r2, #1
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
|loc_08020C26|
		B        |loc_08020C40|
|loc_08020C28|
		LSL r0, r0, #5
		MOV r2, #1
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #9
		ADD r0, r0, r5
		ADD r0, r0, r2
		LDR r1, [r1, #0x5c]
		LDR r2, [sp, #0x50]
		ADD r1, r1, r2
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
|loc_08020C40|
		LDR r0, [r4, #0x40]
		LDRB r0, [r0, #5]
		CMP r0, #0
		BEQ      |loc_08020C76|
		CMP r0, #1
		BEQ      |loc_08020C9A|
		CMP r0, #2
		BNE      |loc_08020B70|
		LSL r1, r6, #0x1e
		LSR r1, r1, #0x1e
		CMP r1, #3
		BNE      |loc_08020C5A|
		MOV r1, #1
|loc_08020C5A|
		LDRH r0, [r4, #0xc]
		LDR r2, [r4, #0x4c]
		LSL r1, r1, #8
		LDR r2, [r2, #0x44]
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r0, #0xff
		ADD r1, r2, r1
		MOV r2, #0xff
		ADD r0, #1
		ADD r2, #1
		BL       |Thunk_VramCopy|
		DCW     0xE60D
|loc_08020C76|
		LSL r2, r6, #0x1f
		LSR r2, r2, #0x1f
		LDRH r0, [r4, #0xc]
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r4, #0x4c]
		LSL r2, r2, #2
		LSL r0, r0, #5
		ADD r0, r0, r5
		ADD r1, r1, r2
		ADD r0, #0xff
		ADD r0, #1
		MOV r2, #0xff
		ADD r2, #1
		LDR r1, [r1, #0x44]
		BL       |Thunk_VramCopy|
		DCW     0xE5FB
|loc_08020C9A|
		LDRH r0, [r4, #0xc]
		LDR r1, [r4, #0x4c]
		LSL r2, r6, #0x1e
		LDR r1, [r1, #0x44]
		LSL r0, r0, #5
		ADD r0, r0, r5
		LSR r2, r2, #0x18
		ADD r1, r1, r2
		ADD r0, #0xff
		ADD r0, #1
		MOV r2, #0xff
		ADD r2, #1
		BL       |Thunk_VramCopy|
		DCW     0xE5EC
