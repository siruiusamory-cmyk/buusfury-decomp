	CODE16
|sub_08007638|
|unk_08007638|
		LDRB r0, [r4, #0x10]
		LSR r1, r0, #4
		LSL r1, r1, #0x1c
		BEQ      |loc_08007648|
		LSR r0, r0, #4
		ADD r0, #0xff
		STRB r0, [r5, #0x10]
		B        |loc_0800764A|
|loc_08007648|
		STRB r0, [r5, #0x10]
|loc_0800764A|
		ADD r1, r5, #0
		MOV r0, #0
		BL       |loc_08006DD6|
		BL       |inc_0x03d784_0x041118| + 0x11c
		LDR r0, [sp, #8]
		CMP r0, #0
		BEQ      |loc_08007634|
		MOV r0, #0x11
		LSL r0, r0, #5
		ADD r0, r5, r0
		STRH r7, [r0, #0x10]
		LDR r1, [r5]
		ADD r0, r5, #0
		LDR r2, [r1, #0x28]
		ADD r2, r2, r1
		MOV r1, #2
		BL       |loc_08046AA4|
		B        |loc_08007634|
