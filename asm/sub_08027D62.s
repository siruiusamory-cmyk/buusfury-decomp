	CODE16
|sub_08027D62|
|unk_08027D62|
		LDR r2, [r0, #0x20]
		LDR r3, [r0, #0x40]
		ADD r2, r2, r3
		STR r2, [r0, #0x20]
		LDR r1, [r0, #0x44]
		LDR r2, [r0, #0x24]
		ADD r1, r2, r1
		STR r1, [r0, #0x24]
		LDR r1, [r0, #0x50]
		ADD r1, #1
		ASR r2, r1, #3
		CMP r2, #3
		STR r1, [r0, #0x50]
		BLE      |loc_08027D84|
		LSL r2, r2, #0x1f
		LSR r2, r2, #0x1f
		ADD r2, #2
|loc_08027D84|
		LSL r3, r2, #1
		ADD r2, r3, r2
		LDR r1, [r0, #0x48]
		LSL r2, r2, #2
		ADD r1, r1, r2
		STR r1, [r0, #0x18]
	INCBIN  baserom.gba_0x27d90_0x27d92.extracted
|sub_08027D92|
|unk_08027D92|
	INCBIN	baserom.gba_0x27d92_0x27d96.extracted
	LSL      r0, r0, #0
	BCS      |loc_08027E04|
	LSR      r4, r0, #0x20
	ADD      r7, #0xc
	LSR      r1, r6, #1
	DCW      0xea48,0x0874
	STR      r2, [sp, #0x2a0]
	LSR      r1, r6, #0x20
	LSL      r4, r0, #0x17
	LSL      r0, r0, #0
	ADD      r7, #0xcc
	LSR      r1, r6, #1
	PUSH     {r4, r5, r6, lr}
	ADD      r6, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |loc_08027DC8|
	MOV      r0, #8
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |loc_08027DC8|
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|loc_08027DC8|
	LDR      r0, [pc, #0x74]
	LDR      r5, [pc, #0x78]
	MOV      r1, #5
	STR      r0, [r4]
	LDR      r0, [r5]
	LSL      r1, r1, #0xb
	BL       |inc_0x0158_0x143f2| + 0x115da
	ADD      r1, r6, #0
	MOV      r0, #0
	BL       |loc_08028144|
	ADD      r1, r0, #0
	STR      r0, [r4, #4]
	LDR      r0, [r5]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      r0, r4, #0
	POP      {r4, r5, r6, pc}
|sub_08027DEE|
|unk_08027DEE|
		BX       lr
