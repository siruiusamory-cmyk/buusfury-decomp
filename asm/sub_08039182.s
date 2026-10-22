	CODE16
|sub_08039182|
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x84]
	ADD      r5, r1, #0
	STR      r0, [r4]
	MOV      r0, #0x45
	LSL      r0, r0, #3
	MOV      r1, #0
	ADD      r0, r4, r0
	BL       |inc_0x0158_0x143f2| + 0xa8a6
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |inc_0x0158_0x143f2| + 0xe5a0
	CMP      r5, #0
	BEQ      |loc_080391AA|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080391AA|
	POP      {r3, r4, r5, pc}
	MOV      r2, #0x45
	LSL      r2, r2, #3
	PUSH     {r3, lr}
	ADD      r0, r0, r2
	BL       |inc_0x0158_0x143f2| + 0xa8f2
	POP      {r3, pc}
|sub_080391BA|
|unk_080391BA|
		MOV r0, #0
		BX       lr
		BX       lr
