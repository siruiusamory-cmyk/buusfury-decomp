	CODE16
|sub_08050D6E|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	STR      r1, [r0]
	BX       lr
	LSL      r0, r0, #0
	LDR      r2, [sp, #0x3c0]
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050D92|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050D92|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050DAA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050DAA|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08050DC2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08050DC2|
	POP      {r3, r4, r5, pc}
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	STR      r2, [r0]
	CMP      r1, #0
	BEQ      |loc_08050DD2|
	BL       |GBARam_Free|
|loc_08050DD2|
	POP      {r3, pc}
|sub_08050DD4|
|unk_08050DD4|
	INCBIN	baserom.gba_0x50dd4_0x50dd6.extracted
|sub_08050DD6|
	DCW      0x0804
