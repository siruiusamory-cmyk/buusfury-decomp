	CODE16
|sub_0804FD4E|
	PUSH     {r4, lr}
	LDR      r0, [r0]
	ADD      r4, r1, #0
	LDR      r0, [r0]
	LDR      r1, [r0]
	LDR      r2, [r1, #0x1c]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
	ADD      r2, r0, #0
	MOV      r1, #0
	ADD      r0, r4, #0
	BL       |sub_08049168|
	POP      {r4, pc}
|loc_0804FD6C|
	DCW      0x76f0
	DCW      0x087b,0x4770
|loc_0804FD72|
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r1, #0
	LDR      r1, [r0, #4]
	ADD      r5, r2, #0
	STR      r1, [r4, #0xc]
	LDR      r1, [r0, #0xc]
	LDR      r2, [r0, #8]
	STR      r1, [r4, #8]
	STR      r2, [r4, #4]
	MOV      r1, #0
	STR      r1, [r0, #4]
	BL       |GBARam_Free|
	LDR      r0, [r4, #0xc]
	LDR      r1, [r0]
	LDR      r2, [r1, #4]
	ADD      r3, r2, r1
	ADD      r2, r5, #0
	ADD      r1, r4, #0
	BL       |inc_0x046118_0x049114| + 0x98e
	POP      {r3, r4, r5, pc}
|sub_0804FDA0|
|unk_0804FDA0|
		BX       lr
