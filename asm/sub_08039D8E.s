	CODE16
|sub_08039D8E|
	LSR      r7, r6, #1
	ASR      r4, r6, #9
	LSR      r1, r6, #1
	ADD      r2, #0xc4
	LSL      r0, r0, #0xc
	PUSH     {r4, r5, r6, r7, lr}
	ADD      r6, r2, #0
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	CMP      r0, #0
	SUB      sp, #0x1c
	BNE      |sub_08039DB6|
	MOV      r0, #0x1c
	BL       |GBARam_Malloc|
	ADD      r4, r0, #0
	BNE      |sub_08039DB6|
	ADD      r0, r4, #0
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
