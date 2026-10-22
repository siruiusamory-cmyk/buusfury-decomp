	CODE16
|unk_08046B74|
	CODE32
	MOV      r3, r1, ASR #0x1f
	MOV      r2, r1
	MOV      r1, r0, ASR #0x1f
	B        |arm_08046B3C|
	CODE16
	CODE16
	EXPORT |__16_ll_neg|
