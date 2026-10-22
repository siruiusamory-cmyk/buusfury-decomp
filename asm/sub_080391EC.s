	CODE16
|sub_080391EC|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x0158_0x143f2| + 0xedb0
	MOV      r0, #0x45
	LSL      r0, r0, #3
	ADD      r0, r4, r0
	BL       |inc_0x0158_0x143f2| + 0xa9b4
	POP      {r4, pc}
	PUSH     {r3, lr}
	BL       |inc_0x0158_0x143f2| + 0x10180
	POP      {r3, pc}
	SUB      r4, r1, r4
	LSL      r0, r0, #0xc
	BPL      |loc_08039238|
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x360
	LSR      r7, r6, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r1, [r1, #0x30]
	MOV      r2, #0
	CMP      r1, #0
	BEQ      |loc_0803922C|
|loc_08039220|
	ADD      r1, #0xff
	ADD      r1, #0xc1
	LDR      r1, [r1, #0x38]
	ADD      r2, #1
	CMP      r1, #0
	BNE      |loc_08039220|
|loc_0803922C|
	LDR      r0, [r0, #0xc]
	MOV      r1, #1
	CMP      r0, r2
	BEQ      |loc_08039236|
	MOV      r1, #0
|loc_08039236|
	ADD      r0, r1, #0
|loc_08039238|
	BX       lr
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [r0, #0xc]
	LDR      r0, [r0, #0x10]
	LDR      r2, [r0]
	BL       |inc_0x046118_0x049114| + 0x98c
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0803925A|
	LDR      r1, [pc, #8]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	STR      r5, [r0, #0xc]
|loc_0803925A|
	POP      {r3, r4, r5, pc}
|sub_0803925C|
|unk_0803925C|
	INCBIN	baserom.gba_0x3925c_0x3925e.extracted
