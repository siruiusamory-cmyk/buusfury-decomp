	CODE16
|sub_08041078|
|unk_08041078|
; cited by 0x08040E90 (a pc-relative load targets 0x08041104)
		LDR r0, [r4, #4]
		CMP r0, #0
		BEQ      |loc_08041086|
		SUB r0, #1
		STR r0, [r4, #4]
		MOV r0, #1
		DCW     0xE7F7
|loc_08041086|
		LDR r0, [pc, #0xa4]
		BL       |inc_0x03d784_0x041118| + 0x3638
		LDR r5, [pc, #0x90]
		STR r0, [r5]
		BL       |inc_0x03d784_0x041118| + 0x358c
		LDR r6, [pc, #0x78]
		LDRB r0, [r6]
		CMP r0, #0
		BNE      |loc_080410C6|
		LDR r0, [r5]
		LSL r1, r0, #0x13
		BMI      |loc_080410F0|
		LSL r1, r0, #0x12
		BMI      |loc_080410F0|
		LSL r1, r0, #0x10
		BPL      |loc_080410B6|
		LSL r1, r0, #0x14
		LSR r1, r1, #0x1c
		LSL r0, r0, #0x1c
		LSR r0, r0, #0x1c
		EOR r1, r0
		BNE      |loc_080410F0|
|loc_080410B6|
		LDR r1, [r4]
		ADD r0, r4, #0
		LDR r2, [r1, #4]
		ADD r1, r2, r1
		BL       |inc_0x046118_0x049114| + 0x98a
		STRB r0, [r6]
		B        |loc_080410F0|
|loc_080410C6|
		LDR r0, [pc, #0x54]
		MOV r7, #1
		LDR r1, [r0]
		ADD r0, r7, #0
		LSL r0, r1
		LDR r1, [r5]
		AND r0, r1
		BEQ      |loc_080410DA|
		BL       |inc_0x03d784_0x041118| + 0x29ac
|loc_080410DA|
		LDR r0, [r5]
		LSL r1, r0, #0x1c
		LSR r1, r1, #0x1d
		BEQ      |loc_080410F0|
		LDR r1, [pc, #0x30]
		LDRB r1, [r1]
		LSL r7, r1
		AND r7, r0
		BEQ      |loc_080410F0|
		BL       |inc_0x03d784_0x041118| + 0x2996
|loc_080410F0|
		LDR r0, [pc, #0x3c]
		BL       |inc_0x03d784_0x041118| + 0x3744
		LDRB r0, [r6]
		CMP r0, #0
		BEQ      |loc_08041108|
		ADD r0, r4, #0
		BL       |inc_0x03d784_0x041118| + 0x38a6
		CMP r0, #0
		BNE      |loc_08041108|
		DCW     0xE7B6
|loc_08041108|
		MOV r0, #1
		DCW     0xE7B4
		DCD     0x03004A98
		DCD     0x03004A94
		DCD     0x03004A6C
