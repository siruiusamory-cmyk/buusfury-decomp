	CODE16
|sub_0803A908|
|unk_0803A908|
; cited by 0x0803A872 (a pc-relative load targets 0x0803AC4C)
		CMP r6, lr
		BGT      |loc_0803A940|
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r6, [r3, #0x2c]
		CMP r6, r0
		BGT      |loc_0803A940|
		LDR r0, [r3, #0x30]
		CMP r0, ip
		BLT      |loc_0803A940|
		CMP r1, r2
		BLT      |loc_0803A940|
		LDRB r0, [r4, #8]
		CMP r0, #2
		BEQ      |loc_0803A902|
		MOV r0, #2
		STRB r0, [r4, #8]
		LDRB r0, [r4, #4]
		LDR r1, [pc, #0x324]
		ADD r2, r5, #0
		LSL r0, r0, #0xb
		ADD r0, r0, r1
		ADD r1, r4, #0
		ADD r1, #0x30
		BL       |Thunk_VramCopy|
		B        |loc_0803A902|
|loc_0803A940|
		MOV r0, #1
		STRB r0, [r4, #8]
		ADD r6, r4, #0
		ADD r6, #0x18
		ADD r0, r7, #0
		LDR r7, [pc, #0x310]
		LDMIA r6!, {r1, r2, r3, r6}
		ADD r7, sp
		STMIA r7!, {r1, r2, r3, r6}
		MOV r3, #0xf
		LSL r3, r3, #7
		ADD r3, sp
		LDR r2, [r3, #0x7c]
		LDR r1, [r0]
		SUB r7, #0x10
		CMP r2, r1
		BGE      |loc_0803A964|
		STR r1, [r3, #0x7c]
|loc_0803A964|
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r2, [r3]
		LDR r1, [r0, #4]
		CMP r2, r1
		BGE      |loc_0803A974|
		STR r1, [r3]
|loc_0803A974|
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r2, [r3, #4]
		LDR r1, [r0, #8]
		CMP r2, r1
		BLE      |loc_0803A984|
		STR r1, [r3, #4]
|loc_0803A984|
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r1, [r3, #8]
		LDR r0, [r0, #0xc]
		CMP r1, r0
		BLE      |loc_0803A994|
		STR r0, [r3, #8]
|loc_0803A994|
		LDR r0, [pc, #0x2c8]
		LDMIA r7!, {r1, r2, r3, r7}
		ADD r0, sp
		STMIA r0!, {r1, r2, r3, r7}
		MOV r3, #1
		LSL r3, r3, #0xb
		ADD r3, sp
		LDR r0, [r3, #0xc]
		LDR r1, [r4, #0x10]
		LDR r2, [r4, #0x14]
		SUB r0, r0, r1
		LDR r1, [r3, #0x10]
		SUB r3, #0x80
		SUB r1, r1, r2
		ADD r3, #0x74
		STMIA r3!, {r0, r1}
		ADD r3, #4
		ADD r6, r1, #0
		ADD r2, r0, #0
		LDR r0, [r3, #0x14]
		LDR r1, [r4, #0x10]
		SUB r0, r0, r1
		LDR r1, [r3, #0x18]
		LDR r3, [r4, #0x14]
		SUB r1, r1, r3
		MOV r3, #0xf
		LSL r3, r3, #7
		ADD r3, sp
		ADD r3, #0x74
		STMIA r3!, {r0, r1, r2}
		STR r0, [r3, #4]
		STR r1, [r3, #8]
		STR r6, [r3]
		SUB r0, r3, #4
		ADD r6, r0, #0
		ADD r6, #0x20
		LDMIA r0!, {r0, r1, r2, r3}
		STMIA r6!, {r0, r1, r2, r3}
		MOV r2, #1
		LSL r2, r2, #0xb
		MOV r1, #0
		ADD r0, sp, #0x1c
		BL       |sub_0804912C|
		ADD r3, r6, #0
		SUB r3, #0x2c
		LDR r0, [r3, #0x1c]
		ASR r1, r0, #3
		LDR r0, [r3, #0x20]
		STR r1, [sp, #4]
		ASR r0, r0, #3
		STR r0, [sp, #8]
		STR r0, [sp, #0x10]
		STR r1, [sp, #0xc]
		LDR r0, [r3, #0x24]
		ADD r0, #7
		ASR r0, r0, #3
		STR r0, [sp, #0x14]
		LDR r0, [r3, #0x28]
		LDR r2, [sp, #0x10]
		ADD r0, #7
		ASR r0, r0, #3
		STR r0, [sp, #0x18]
		CMP r0, r2
		BLE      |loc_0803AA44|
|loc_0803AA16|
		LSL r1, r2, #0x1b
		LDR r0, [sp, #0xc]
		LDR r5, [sp, #0x14]
		LSR r1, r1, #0x1b
		CMP r5, r0
		BLE      |loc_0803AA3C|
		ADD r5, sp, #0x1c
		LSL r1, r1, #6
		ADD r6, r1, r5
		ADD r5, r1, r4
|loc_0803AA2A|
		LSL r1, r0, #0x1b
		LSR r1, r1, #0x1a
		ADD r3, r5, r1
		LDRH r7, [r3, #0x30]
		ADD r0, #1
		STRH r7, [r6, r1]
		LDR r1, [sp, #0x14]
		CMP r1, r0
		BGT      |loc_0803AA2A|
|loc_0803AA3C|
		LDR r0, [sp, #0x18]
		ADD r2, #1
		CMP r0, r2
		BGT      |loc_0803AA16|
|loc_0803AA44|
		LDRB r0, [r4, #4]
		LDR r1, [pc, #0x20c]
		MOV r2, #1
		LSL r0, r0, #0xb
		ADD r0, r0, r1
		ADD r1, sp, #0x1c
		LSL r2, r2, #0xb
		BL       |Thunk_VramCopy|
		B        |loc_0803A902|
		PUSH {r0, r1, r4, r5, r6, r7, lr}
		SUB sp, #0x1fc
		LDRB r2, [r0, #0xd]
		LDRB r1, [r0, #0xb]
		SUB sp, #0x1fc
		ADD r5, r0, #0
		SUB sp, #0x1fc
		SUB sp, #0x70
		LDRB r0, [r0, #0xa]
		CMP r2, r1
		BNE      |loc_0803AA7A|
		LDRB r2, [r5, #0xc]
		CMP r2, r0
		BNE      |loc_0803AA7A|
		LDRB r2, [r5, #9]
		CMP r2, #0
		BEQ      |loc_0803AB60|
|loc_0803AA7A|
		STRB r1, [r5, #0xd]
		LDR r1, [pc, #0x1e4]
		STRB r0, [r5, #0xc]
		LDRB r0, [r1]
		MOV r1, #1
		ADD r6, sp, #0x3fc
		EOR r0, r1
		LDR r1, [pc, #0x1d8]
		ADD r6, #0x5c
		STRB r0, [r1]
		MOV r0, #1
		LSL r0, r0, #0x1f
		STR r0, [r5, #0x28]
		STR r0, [r5, #0x2c]
		LDRB r1, [r5, #0xb]
		ADD r0, r6, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x5c50
		LDRB r0, [r5, #9]
		CMP r0, #0
		BEQ      |loc_0803AAF4|
		LDRB r0, [r5, #0xb]
		CMP r0, #3
		BLS      |loc_0803AAF4|
		SUB r1, r0, #3
		ADD r7, sp, #0x58
		ADD r0, r7, #0
		BL       |inc_0x351c0_0x3d4d0| + 0x5c50
		LDRB r0, [r5, #0xb]
		MOV r4, #0
		SUB r0, #3
		CMP r0, #0
		BLE      |loc_0803AADC|
|loc_0803AABE|
		MOV r0, #4
		BL       |inc_0x03d784_0x041118| + 0x2348
		LSL r2, r4, #2
		LDR r1, [r6, r2]
		LDR r3, [r7, r2]
		ADD r4, #1
		SUB r1, r1, r3
		ADD r0, r0, r1
		ADD r1, sp, #0x258
		STR r0, [r1, r2]
		LDRB r0, [r5, #0xb]
		SUB r0, #3
		CMP r0, r4
		BGT      |loc_0803AABE|
|loc_0803AADC|
		LDRB r0, [r5, #0xb]
		CMP r0, r4
		BLE      |loc_0803AB0C|
		ADD r2, sp, #0x258
|loc_0803AAE4|
		LSL r0, r4, #2
		LDR r1, [r6, r0]
		ADD r4, #1
		STR r1, [r2, r0]
		LDRB r0, [r5, #0xb]
		CMP r0, r4
		BGT      |loc_0803AAE4|
		B        |loc_0803AB0C|
|loc_0803AAF4|
		MOV r2, #1
		LSL r2, r2, #9
		MOV r1, #0
		ADD r0, sp, #0x258
		BL       |sub_0804912C|
		MOV r2, #1
		LSL r2, r2, #9
		ADD r1, r6, #0
		ADD r0, sp, #0x58
		BL       |Thunk_VramCopy|
|loc_0803AB0C|
		LDR r0, [pc, #0x158]
		LDR r1, [pc, #0x154]
		LDR r0, [r0]
		LDRH r0, [r0]
		LDRB r1, [r1]
		LSL r3, r1, #4
		SUB r1, r3, r1
		LSL r1, r1, #2
		ADD r4, r0, r1
		ADD r1, r4, #1
		STR r1, [sp, #0x54]
		LDRB r0, [r5, #0xa]
		LDR r3, [pc, #0x144]
		MOV r1, #3
		MUL r0, r3
		STR r0, [sp, #0x50]
		LSL r0, r4, #6
		LSL r1, r1, #0x19
		ADD r0, r0, r1
		LDR r1, [sp, #0x50]
		MOV r2, #0x40
		BL       |sub_0804912C|
		LDRB r0, [r5, #0xb]
		MOV r3, #3
		LSL r3, r3, #9
		ADD r0, #7
		LSR r1, r0, #3
		MOV r0, #0
		STR r1, [sp, #0x4c]
		ADD r3, sp
		STR r0, [r3, #0x58]
		CMP r1, #0
		BLE      |loc_0803AC34|
		LSL r2, r4, #0x10
		LSR r2, r2, #0x10
		STR r2, [r3, #0x60]
|loc_0803AB56|
		MOV r3, #3
		LSL r3, r3, #9
		ADD r3, sp
		LDR r0, [r3, #0x58]
		B        |loc_0803AB62|
|loc_0803AB60|
		B        |inc_0x351c0_0x3d4d0| + 0x5b90
|loc_0803AB62|
		LSL r0, r0, #3
		STR r0, [sp, #0x48]
		ADD r0, #7
		STR r0, [sp, #0x44]
		LSL r0, r0, #2
		ADD r1, sp, #0x58
		LDR r0, [r1, r0]
		LDR r1, [sp, #0x48]
		ADD r6, sp, #0x3fc
		ADD r6, #0x5c
		LSL r1, r1, #2
		LDR r1, [r6, r1]
		SUB r0, #3
		ADD r1, #7
		ASR r1, r1, #3
		ASR r0, r0, #3
		MOV r4, #0
		CMP r0, #0
		STR r1, [sp, #0x40]
		BLE      |loc_0803ABA4|
		LDR r1, [r3, #0x58]
		LSL r1, r1, #6
		ADD r1, r1, r5
|loc_0803AB90|
		MOV r3, #3
		LSL r3, r3, #9
		ADD r3, sp
		LDR r2, [r3, #0x60]
		LSL r3, r4, #1
		ADD r3, r1, r3
		ADD r4, #1
		CMP r4, r0
		STRH r2, [r3, #0x30]
		BLT      |loc_0803AB90|
|loc_0803ABA4|
		LDR r0, [sp, #0x40]
		CMP r4, r0
		BGE      |inc_0x351c0_0x3d4d0| + 0x5ace
		MOV r3, #3
		LSL r3, r3, #9
		ADD r3, sp
		LDR r0, [r3, #0x58]
		LSL r0, r0, #6
		ADD r1, r0, r5
		STR r1, [r3, #0x5c]
|loc_0803ABB8|
		LDR r0, [sp, #0x48]
		LDR r2, [sp, #0x44]
		MOV r1, sp
		MOV lr, r0
		CMP r0, r2
		BGT      |loc_0803AC42|
		LSL r0, r4, #3
		MOV ip, r0
|loc_0803ABC8|
		MOV r0, lr
		ADD r2, sp, #0x3fc
		ADD r2, #0x5c
		LSL r0, r0, #2
		LDR r2, [r2, r0]
		MOV r3, ip
		SUB r2, r2, r3
		ADD r3, sp, #0x258
		LDR r0, [r3, r0]
		SUB r6, r2, r0
		CMP r2, #0
		BGT      |loc_0803ABEA|
		MOV r0, #0
		STR r0, [r1]
		STR r0, [r1, #4]
		ADD r1, #8
		B        |loc_0803AC36|
|loc_0803ABEA|
		CMP r6, #8
		BLT      |loc_0803ABFA|
		LDR r0, [sp, #0x50]
		STR r0, [r1]
		LDR r0, [sp, #0x50]
		STR r0, [r1, #4]
		ADD r1, #8
		B        |loc_0803AC36|
|loc_0803ABFA|
		CMP r2, #8
		BLE      |loc_0803AC00|
		MOV r2, #8
|loc_0803AC00|
		MOV r0, #0
		CMP r6, #0
		BLE      |loc_0803AC12|
|loc_0803AC06|
		LDRB r7, [r5, #0xa]
		ADD r0, #1
		STRB r7, [r1]
		ADD r1, #1
		CMP r0, r6
		BLT      |loc_0803AC06|
|loc_0803AC12|
		CMP r0, r2
		BGE      |loc_0803AC22|
		MOV r6, #2
|loc_0803AC18|
		STRB r6, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r0, r2
		BLT      |loc_0803AC18|
|loc_0803AC22|
		CMP r0, #8
		BGE      |loc_0803AC36|
		MOV r2, #0
|loc_0803AC28|
		STRB r2, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r0, #8
		BLT      |loc_0803AC28|
		B        |loc_0803AC36|
|loc_0803AC34|
		B        |loc_0803ACD2|
|loc_0803AC36|
		MOV r0, lr
		ADD r0, #1
		LDR r2, [sp, #0x44]
		MOV lr, r0
		CMP r0, r2
		BLE      |loc_0803ABC8|
|loc_0803AC42|
		LDR r1, [sp, #0x54]
		LSL r0, r1, #6
		MOV r1, #3
		LSL r1, r1, #0x19
		B        |loc_0803AC70|
	INCBIN  baserom.gba_0x3ac4c_0x3ac54.extracted
		DCD     VRAM + 0xE000
	INCBIN  baserom.gba_0x3ac58_0x3ac5c.extracted
		DCD     0x000007FC
		DCD     0x0000080C
		DCD     0x030032DC
		DCD     0x0877B124
		DCD     0x01010101
|loc_0803AC70|
		ADD r0, r0, r1
		MOV r1, sp
		MOV r2, #0x40
		BL       |Thunk_VramCopy|
		LDR r0, [sp, #0x54]
		MOV r3, #3
		LSL r3, r3, #9
		ADD r1, r0, #1
		STR r1, [sp, #0x54]
		ADD r3, sp
		LDR r1, [r3, #0x5c]
		LSL r2, r4, #1
		ADD r1, r1, r2
		B        |loc_0803AC90|
		B        |inc_0x351c0_0x3d4d0| + 0x5ada
|loc_0803AC90|
		STRH r0, [r1, #0x30]
		LDR r0, [sp, #0x40]
		ADD r4, #1
		CMP r4, r0
		BLT      |loc_0803ABB8|
		CMP r4, #0x10
		BGE      |loc_0803ACB8|
		MOV r3, #3
		LSL r3, r3, #9
		ADD r3, sp
		LDR r1, [r3, #0x58]
		MOV r0, #0
		LSL r1, r1, #6
		ADD r1, r1, r5
|loc_0803ACAC|
		LSL r2, r4, #1
		ADD r2, r1, r2
		ADD r4, #1
		CMP r4, #0x10
		STRH r0, [r2, #0x30]
		BLT      |loc_0803ACAC|
|loc_0803ACB8|
		MOV r3, #3
		LSL r3, r3, #9
		ADD r3, sp
		LDR r0, [r3, #0x58]
		ADD r0, #1
		STR r0, [r3, #0x58]
		LDR r1, [sp, #0x4c]
		CMP r0, r1
		BGE      |sub_0803ACCC|
		B        |loc_0803AB56|
