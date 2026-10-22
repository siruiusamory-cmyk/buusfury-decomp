|Blend_WriteAlpha2|
	CODE16
|unk_08017AFC|
; cited by 0x080179FC (a pc-relative load targets 0x08017BDC)
		LDR r1, [pc, #0x110]
		CMP r0, #0xb0
		BGT      |loc_08017B12|
		MOV r2, #0xb0
		SUB r0, r2, r0
		STRB r0, [r1, #3]
		LDR r0, [r4, #4]
		ADD r0, #0x60
		STRB r0, [r1, #2]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017B12|
		MOV r2, #0xff
		ADD r2, #0x41
		CMP r0, r2
		BGE      |loc_08017B1E|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017B1E|
		ADD r2, r0, #0
		SUB r2, #0xff
		SUB r2, #0x41
		BNE      |loc_08017BA2|
		LDR r0, [pc, #0xec]
		LDR r1, [r4, #0x2c]
		BL       |inc_0x03d784_0x041118| + 0x1bc
		MOV r2, #1
		LSL r2, r2, #0xb
		MOV r1, #2
		LDR r0, [pc, #0xa8]
		BL       |sub_08049168|
		MOV r0, #3
		STR r0, [sp, #4]
		MOV r0, #0xd
		MOV r5, #0
		MOV r6, #0x1e
		STR r0, [sp, #0xc]
		MOV r0, sp
		STR r6, [sp, #8]
		MOV r2, #2
		STR r5, [sp]
		LDR r1, [pc, #0x90]
		BL       |inc_0x03d784_0x041118| + 0x28c
		MOV r0, #0x11
		STR r0, [sp, #4]
		MOV r0, #0x14
		STR r0, [sp, #0xc]
		MOV r2, #0xff
		ADD r2, #0x2f
		MOV r0, sp
		STR r5, [sp]
		STR r6, [sp, #8]
		LDR r1, [pc, #0x78]
		BL       |inc_0x03d784_0x041118| + 0x28c
		MOV r0, #0x18
		STR r0, [sp, #4]
		MOV r0, #0x68
		STR r0, [sp, #0xc]
		ADD r0, r4, #0
		MOV r6, #0xf0
		ADD r0, #8
		ADD r4, r0, #0
		STR r6, [sp, #8]
		STR r5, [sp]
		MOV r2, sp
		LDR r1, [pc, #0x64]
		BL       |sub_0804915C|
		MOV r0, #0x88
		STR r0, [sp, #4]
		MOV r0, #0xa0
		STR r0, [sp, #0xc]
		ADD r0, r4, #0
		STR r5, [sp]
		STR r6, [sp, #8]
		MOV r2, sp
		LDR r1, [pc, #0x7c]
		BL       |sub_0804915C|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017BA2|
		MOV r2, #0xff
		ADD r2, #0x51
		CMP r0, r2
		BGT      |loc_08017BB8|
		ADD r0, #0xc0
		STRB r0, [r1, #3]
		LDR r0, [r4, #4]
		SUB r0, r2, r0
		STRB r0, [r1, #2]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017BB8|
		MOV r2, #0xff
		ADD r2, #0xf5
		CMP r0, r2
		BGT      |loc_08017BC4|
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017BC4|
		MOV r2, #0x81
		LSL r2, r2, #2
		CMP r0, r2
		BGT      |loc_08017BD6|
		SUB r0, r2, r0
		ASR r0, r0, #1
		STRB r0, [r1, #3]
		MOV r0, #0
		B        |inc_0x153f2_0x1a3f2| + 0x2706
|loc_08017BD6|
		MOV r0, #1
		B        |inc_0x153f2_0x1a3f2| + 0x2706
	INCBIN  baserom.gba_0x17bda_0x17be0.extracted
		DCD     VRAM + 0x7800
	INCBIN  baserom.gba_0x17be4_0x17be8.extracted
		DCD     VRAM + 0x80
	INCBIN  baserom.gba_0x17bec_0x17bf2.extracted
