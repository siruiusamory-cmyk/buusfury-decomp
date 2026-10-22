	CODE16
|sub_080387AC|
|unk_080387AC|
		LDRH r0, [r2, #0xc]
		LDR r1, [pc, #0x28]
		LSL r0, r0, #5
		ADD r0, r0, r1
		LDR r1, [r2, #0x44]
		MOV r2, #0xc0
		LDR r1, [r1, #8]
		BL       |Thunk_VramCopy|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x35ea
|loc_080387C2|
|unk_080387C2|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x35ea
