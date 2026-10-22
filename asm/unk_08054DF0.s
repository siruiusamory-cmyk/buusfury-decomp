	CODE16
|unk_08054DF0|
	CODE32
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
	BXEQ     lr
	AND      r1, r0, #128, 8
	ORR      r1, r1, #96, 8
	TST      r0, #0xff0000
	MOVEQ    r0, r0, LSL #8
	SUBEQ    r1, r1, #64, 12
	TST      r0, #0xff0000
	MOVEQ    r0, r0, LSL #8
	SUBEQ    r1, r1, #64, 12
	TST      r0, #240, 16
	MOVEQ    r0, r0, LSL #4
	SUBEQ    r1, r1, #128, 14
	TST      r0, #192, 16
	MOVEQ    r0, r0, LSL #2
	SUBEQ    r1, r1, #64, 14
	TST      r0, #128, 16
	MOVEQ    r0, r0, LSL #1
	ADDNE    r1, r1, #128, 16
	BIC      r0, r0, #128, 16
	ORR      r0, r0, r1
|arm_08054E6C|
	ORR      ip, r2, #128, 10
	B        |arm_08054F14|
	CODE16
	CODE16
	EXPORT |sub_08054E74|
