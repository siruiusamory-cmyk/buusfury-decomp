	CODE16
|sub_0804EF1E|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EF40|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #0xc]
	STR      r1, [r0]
	MOV      r1, #0xff
	ADD      r1, #0x2d
	STR      r1, [r0, #0x10]
|loc_0804EF40|
	POP      {r4, pc}
	LSL      r0, r0, #0
|unk_0804EF44|
	INCBIN	baserom.gba_0x4ef44_0x4ef46.extracted
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	MOV      r0, #0x18
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_0804EF66|
	MOV      r1, #0
	STR      r1, [r0, #8]
	STR      r4, [r0, #4]
	STR      r1, [r0, #0xc]
	LDR      r2, [pc, #8]
	STR      r1, [r0, #0x10]
	STR      r2, [r0]
	STR      r1, [r0, #0x14]
|loc_0804EF66|
	POP      {r4, pc}
|sub_0804EF68|
|unk_0804EF68|
	INCBIN	baserom.gba_0x4ef68_0x4ef6a.extracted
