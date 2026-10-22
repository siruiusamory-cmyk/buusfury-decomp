	CODE16
|unk_08054780|
	CODE32
|arm_08054780|
	STMDB    sp!, {r0, r1}
	STMDB    sp!, {r2, r3, ip, lr}
	BL       |arm_08047A2C|
	LDMIA    sp!, {r2, r3, ip, lr}
	MOV      r3, r0
	LDMIA    sp!, {r0, r1}
	LDR      r3, [r3]
	TST      r3, #64, 14
	ANDNE    r1, r1, #128, 8
	MOVNE    r0, #0
	BXNE     lr
	TST      r3, #128, 28
	BXEQ     lr
	STMDB    sp!, {lr}
	MOV      lr, #96, 12
	ORR      lr, lr, r1, lsr #31
	BIC      r1, r1, #128, 8
	ORRS     r3, r1, r0, lsr #12
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    lr, lr, #80, 18
	TST      r1, r1
	MOVEQ    r1, r0, LSR #0xc
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    lr, lr, #80, 18
	MOV      r2, #0
	MOVS     r3, r1, LSR #5
	MOVEQ    r1, r1, LSL #0x10
	ADDEQ    r2, r2, #0x10
	MOVS     r3, r1, LSR #0xd
	MOVEQ    r1, r1, LSL #8
	ADDEQ    r2, r2, #8
	MOVS     r3, r1, LSR #0x11
	MOVEQ    r1, r1, LSL #4
	ADDEQ    r2, r2, #4
	MOVS     r3, r1, LSR #0x13
	MOVEQ    r1, r1, LSL #2
	ADDEQ    r2, r2, #2
	MOVS     r3, r1, LSR #0x14
	MOVEQ    r1, r1, LSL #1
	ADDEQ    r2, r2, #1
	SUB      lr, lr, r2, lsl #16
	MOV      r3, r0, LSL r2
	RSB      r2, r2, #0x20
	ORR      r1, r1, r0, lsr r2
	MOV      r0, r3
	EOR      r1, r1, lr, lsl #31
	BIC      lr, lr, #1
	ADD      r1, r1, lr, lsl #4
	LDMIA    sp!, {lr}
|arm_08054844|
	ORR      ip, ip, #128, 10
	B        |arm_08054F14|
	CODE16
	CODE16
	EXPORT |sub_0805484C|
