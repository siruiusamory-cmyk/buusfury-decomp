	CODE16
|unk_08046BA8|
	CODE32
	STMDB    sp!, {r4, lr}
	MOVS     r4, r1, ASR #1
	EOR      r4, r4, r3, lsr #1
	BPL      |arm_08046BC0|
	RSBS     r0, r0, #0
	RSC      r1, r1, #0
|arm_08046BC0|
	TST      r3, r3
	BPL      |arm_08046BD0|
	RSBS     r2, r2, #0
	RSC      r3, r3, #0
|arm_08046BD0|
	BL       |arm_080476AC|
	TST      r4, #64, 8
	BEQ      |arm_08046BE4|
	RSBS     r0, r0, #0
	RSC      r1, r1, #0
|arm_08046BE4|
	TST      r4, #128, 8
	BEQ      |arm_08046BF4|
	RSBS     r2, r2, #0
	RSC      r3, r3, #0
|arm_08046BF4|
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_shift_l|
