	CODE16
|sub_0804F676|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	MOV      r0, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	LDR      r2, [pc, #0xc]
	PUSH     {r3, lr}
	MOV      r1, #0
	STR      r1, [r2]
	BL       |GBARam_Free|
	POP      {r3, pc}
	LSL      r0, r0, #0
	CMP      r7, #0xe4
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	MOV      r2, #0x38
	STRB     r2, [r1, #8]
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r4, lr}
	ADD      r4, r1, #0
	ADD      r0, r1, #0
	LDR      r1, [r1]
	LDR      r2, [r1, #0x28]
	ADD      r2, r2, r1
	MOV      r1, #0
	BL       |inc_0x046118_0x049114| + 0x98c
	MOV      r0, #1
	ADD      r4, #0xff
	ADD      r4, #0xc1
	STR      r0, [r4, #0xc]
	POP      {r4, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	LDR      r2, [r0]
	LDR      r3, [r2, #8]
	ADD      r2, r3, r2
	BL       |inc_0x046118_0x049114| + 0x98c
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r2, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	PUSH     {r3, lr}
	STRH     r2, [r1, #0x16]
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r2, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	PUSH     {r3, lr}
	STR      r2, [r1, #0xc]
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r4, r1, #0
	CMP      r0, #0
	BEQ      |loc_0804F740|
	BL       |inc_0x351c0_0x3d4d0| + 0x1f46
|loc_0804F740|
	LDR      r0, [r4, #0x50]
	LDR      r0, [r0]
	LSL      r0, r0, #3
	STRH     r0, [r4, #0x12]
	ADD      r0, r5, #0
	BL       |GBARam_Free|
	POP      {r3, r4, r5, pc}
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r5, r0, #0
	LDR      r0, [r0, #4]
	ADD      r4, r1, #0
	CMP      r0, #0
	BEQ      |loc_0804F774|
	BL       |inc_0x351c0_0x3d4d0| + 0x1f46
|loc_0804F774|
	LDR      r0, [r4, #0x50]
	LDR      r0, [r0]
	LSL      r0, r0, #3
	STRH     r0, [r4, #0x12]
	ADD      r0, r5, #0
	BL       |GBARam_Free|
	POP      {r3, r4, r5, pc}
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r2, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	PUSH     {r3, lr}
	STR      r2, [r1, #0xc]
	BL       |GBARam_Free|
	POP      {r3, pc}
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r0, #1
	ADD      r1, #0xff
	ADD      r1, #0xc1
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	MOV      r0, #0
	ADD      r1, #0xff
	ADD      r1, #0x61
	STRH     r0, [r1, #0x16]
	BX       lr
	LSL      r0, r0, #0
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x160
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
|sub_0804F7E0|
|unk_0804F7E0|
		BX       lr
