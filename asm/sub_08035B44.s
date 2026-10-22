	CODE16
|sub_08035B44|
|unk_08035B44|
		LDR r1, [r2, #0x1c]
		LDRB r1, [r1]
		CMP r1, #1
		BNE      |loc_08035B76|
		ADD r1, r2, #4
		LDR r2, [r2, #4]
		LDR r3, [r0, #0x30]
		CMP r2, r3
		BGE      |loc_08035B76|
		LDR r2, [r0, #0x28]
		LDR r3, [r1, #8]
		CMP r2, r3
		BGE      |loc_08035B76|
		LDR r2, [r1, #4]
		LDR r3, [r0, #0x34]
		CMP r2, r3
		BGE      |loc_08035B76|
		LDR r2, [r0, #0x2c]
		LDR r1, [r1, #0xc]
		CMP r2, r1
		BGE      |loc_08035B76|
		BL       |sub_08035A34|
		MOV r0, #1
		B        |inc_0x351c0_0x3d4d0| + 0x982
|loc_08035B76|
		MOV r0, #0
		B        |inc_0x351c0_0x3d4d0| + 0x982
|loc_08035B7A|
|unk_08035B7A|
; cited by 0x080359FC (a pc-relative load targets 0x08035B80)
		BL       |inc_0x153f2_0x1a3f2| + 0x48d2
		B        |inc_0x351c0_0x3d4d0| + 0x982
		DCD     0x0804B9B4
		DCD     0x0875A6A8
		DCD     0x08759688
		DCD     0x08712FDC
		DCD     0x086B8090
		PUSH {r3, r4, r5, r6, r7, lr}
		LDR r5, [r0, #0xc]
		MOV r1, #0
		CMP r5, #0
		BEQ      |inc_0x351c0_0x3d4d0| + 0xa04
		LDR r2, [pc, #0x2c]
		LDR r2, [r2]
		ADD r3, r2, #4
		LDR r6, [r3]
		MOV r2, #0
		CMP r6, #0
		BLE      |inc_0x351c0_0x3d4d0| + 0xa04
|loc_08035BAC|
		LSL r4, r2, #2
		ADD r4, r4, r3
		LDR r4, [r4, #4]
		CMP r4, r5
		BEQ      |sub_08035BBE|
		ADD r2, #1
		CMP r6, r2
		BGT      |loc_08035BAC|
		B        |inc_0x351c0_0x3d4d0| + 0xa04
