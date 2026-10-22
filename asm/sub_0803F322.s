	CODE16
|sub_0803F322|
|unk_0803F322|
		MOV r1, #1
		LSL r1, r1, #9
		CMP r4, r1
		DCW     0xDA23
		CMP r0, r1
		BLE      |loc_0803F35E|
		SUB r3, r1, r4
		STR r3, [sp, #8]
		SUB r3, r0, r1
		LDR r0, [pc, #0x74]
		STR r3, [sp, #4]
		ADD r1, r4, r0
		MOV r0, #1
		LSL r0, r0, #0x19
		ADD r2, r6, #0
		ADD r0, r4, r0
		LDR r3, [sp, #8]
		BL       |sub_080491B4|
		LDR r3, [sp, #8]
		LDR r1, [pc, #0x80]
		LSL r0, r3, #2
		ADD r0, r0, r7
		ADD r2, r0, r1
		LDR r1, [pc, #0x80]
		LDR r0, [pc, #0x78]
		LDR r3, [sp, #4]
		BL       |sub_080491B4|
		B        |loc_0803F382|
|loc_0803F35E|
		LDR r0, [pc, #0x4c]
		ADD r3, r5, #0
		ADD r1, r4, r0
		MOV r0, #1
		LSL r0, r0, #0x19
		ADD r2, r6, #0
		ADD r0, r4, r0
	INCBIN  baserom.gba_0x3f36c_0x3f36e.extracted
|sub_0803F36E|
|unk_0803F36E|
	INCBIN	baserom.gba_0x3f36e_0x3f372.extracted
	LDR      r0, [pc, #0x5c]
	ADD      r3, r5, #0
	ADD      r1, r4, r0
	LSL      r0, r0, #0x10
	ADD      r2, r6, #0
	ADD      r0, r4, r0
	BL       |inc_0x049120_0x055620| + 0x94
|loc_0803F382|
	LDR      r0, [sp, #0x10]
	LSL      r4, r0, #0x16
	LDR      r0, [sp, #0xc]
	LSR      r4, r4, #0x16
	SUB      r0, r0, r5
	STR      r0, [sp, #0xc]
	BNE      |loc_0803F2C6|
|loc_0803F390|
	MOV      r0, #0
	STR      r0, [r7]
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|loc_0803F398|
	DCW      0x05c4
	DCW      0x0000,0x0080,0x0400,0x9a0e,0x0000,0x00a0,0x0400,0xb660
	DCW      0x0000,0x0600,0x0200,0x00a4,0x0400,0xf660,0x0000,0x6edc
	DCW      0x087b,0x0ae0,0x0300,0x0200,0x0400,0xfbe6,0xffff,0x0100
|loc_0803F3CA|
	LSL      r0, r0, #0x10
	LSR      r4, r0, #7
	LSL      r0, r0, #0
	LSL      r0, r0, #8
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	LSL      r0, r0, #8
	BX       lr
	LDR      r0, [pc, #0x58]
	LDR      r1, [pc, #0x58]
	STR      r0, [r1, #0x3c]
	MOV      r1, #1
	LDR      r0, [pc, #0x58]
	LSL      r1, r1, #0xd
	STRH     r1, [r0]
	MOV      r1, #1
	STRH     r1, [r0, #8]
	MOV      r0, #0x18
	LSL      r1, r1, #0x1a
	STRH     r0, [r1, #4]
	BX       lr
