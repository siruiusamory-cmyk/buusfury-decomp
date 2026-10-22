	CODE16
|unk_08054E78|
	CODE32
|arm_08054E78|
	AND      r3, ip, #0xf
	CMP      r3, #9
	MOVEQ    r0, #8
	BEQ      |arm_08054F3C|
	CMP      r3, #8
	BXNE     lr
	TSTEQ    ip, #0x40
	BEQ      |arm_08054EF4|
	TST      ip, #64, 22
	BNE      |arm_08054ED0|
	TST      ip, #0x20
	BNE      |arm_08054EDC|
	TST      ip, #0x10
	MOVEQ    r2, r0
	MOVNE    r2, r1
	MVNEQ    r0, #128, 8
	MVNNE    r1, #128, 8
	MVNNE    r0, #0
	TST      r2, #128, 8
	MVNNE    r0, r0
	MVNNE    r1, r1
	BX       lr
|arm_08054ED0|
	MOV      r0, #0
	MOV      r1, #0
	BX       lr
|arm_08054EDC|
	MVN      r0, #0
	MVN      r1, #0
	TST      r2, #128, 8
	MVNNE    r0, r0
	MVNNE    r1, r1
	BX       lr
|arm_08054EF4|
	TST      ip, #0x10
	CODE16
	CODE16
	EXPORT |sub_08054EF8|
