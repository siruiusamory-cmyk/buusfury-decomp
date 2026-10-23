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
	CODE16
|dat_08054EF8|
	DCW      0x0008
	DCW      0x059f
	DCW      0x1008
	DCW      0x159f
	DCW      0x0000
	DCW      0x13a0
|unk_08054F04|
	INCBIN	baserom.gba_0x54f04_0x54f08.extracted
	LSL      r0, r0, #0
	LDRB     r0, [r0, #0x1f]
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	BX       pc
	LSL      r0, r0, #0

