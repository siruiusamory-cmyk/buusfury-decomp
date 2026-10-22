	CODE16
|unk_08046C00|
	CODE32
	SUBS     r3, r2, #0x20
	BPL      |arm_08046C1C|
	RSB      r3, r2, #0x20
	MOV      r1, r1, LSL r2
	ORR      r1, r1, r0, lsr r3
	MOV      r0, r0, LSL r2
	BX       lr
|arm_08046C1C|
	MOV      r1, r0, LSL r3
	MOV      r0, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_sshift_r|
