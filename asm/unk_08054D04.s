	CODE16
|unk_08054D04|
	CODE32
|arm_08054D04|
	STMDB    sp!, {r0, r1}
	STMDB    sp!, {r2, r3, ip, lr}
	BL       |arm_08047A2C|
	LDMIA    sp!, {r2, r3, ip, lr}
	MOV      ip, r0
	LDMIA    sp!, {r0, r1}
	LDR      r1, [ip]
	TST      r1, #64, 14
	ANDNE    r0, r0, #128, 8
	BXNE     lr
	TST      r1, #128, 28
	BNE      |arm_08054E6C|
	AND      r3, r0, #128, 8
	ORR      r3, r3, r0, lsr #23
	BIC      r3, r3, #64, 30
	RSB      r3, r3, #0xc1
	BIC      r1, r3, #128, 8
	CMP      r1, #0x17
	BGT      |arm_08054DB8|
	RSB      r3, r3, #0x20
	MOVS     r1, r0, LSL r3
	RSB      r3, r3, #0x20
	BIC      r0, r0, #0xff000000
	ORR      r0, r0, #128, 16
	MOV      r0, r0, LSR r3
	AND      r3, r3, #128, 8
	ORR      r0, r0, r3
	BEQ      |arm_08054DA8|
	MOV      r3, r1
	LDR      r1, [ip]
	ORR      r1, r1, #8
	STR      r1, [ip]
	MOVS     r1, r3, LSL #1
	BLO      |arm_08054DA0|
	ADDNE    r0, r0, #1
	BNE      |arm_08054DA0|
	MVNS     r3, r2, asr #31
	ADDLS    r0, r0, #1
|arm_08054D9C|
	DCD     0x33C00001
|arm_08054DA0|
	ORR      ip, r2, #64, 8
	B        |arm_08054850|
|arm_08054DA8|
	MOV      ip, r2
	TST      r2, #64, 8
	BNE      |arm_08054850|
	BX       lr
|arm_08054DB8|
	CMP      r1, #0x80000019
	LDR      r1, [ip]
	ORR      r1, r1, #8
	STR      r1, [ip]
	ANDVS    r0, r3, #128, 8
	BVS      |arm_08054DE4|
	MOVS     r0, r0, LSL #9
	AND      r0, r3, #128, 8
	ADD      r0, r0, #1
	TSTEQ    r2, #128, 8
|arm_08054DE0|
	DCD     0x03C00001
|arm_08054DE4|
	MOV      ip, #64, 8
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08054DEC|
