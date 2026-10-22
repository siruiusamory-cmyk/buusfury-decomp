	CODE16
|sub_08026B32|
	LSR      r4, r0, #0x20
	LSL      r5, r3, #0x1c
	LSL      r0, r0, #0
	LDMIA    r2!, {r4, r6, r7}
	LSR      r4, r6, #1
	ADD      r4, r6, #0
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x330]
	LSR      r4, r0, #0x20
	ADD      r6, sp, #0x1c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xe0
	LSL      r0, r0, #0xc
|loc_08026B4C|
	PUSH     {r3, r4, r5, r6, r7, lr}
	ADD      r7, r1, #0
	ADD      r5, r2, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	BNE      |sub_08026B66|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08026B66|
	ADD      r0, r4, #0
	POP      {r3, r4, r5, r6, r7, pc}
