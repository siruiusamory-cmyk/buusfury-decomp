	CODE16
|unk_08054618|
	CODE32
|arm_08054618|
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
	BNE      |arm_08054844|
	TST      r1, r1
	ORRMI    ip, ip, #64, 22
	MOV      r3, #96, 28
	MOV      r2, r1, LSR #0x14
	ADD      r3, r3, #1
	BIC      r1, r1, r2, lsl #20
	BIC      r2, r2, #128, 28
	SUB      r2, r3, r2
	ORR      r1, r1, #64, 18
	CMP      r2, #0x35
	BHI      |arm_08054704|
	BEQ      |arm_080546EC|
	CMP      r2, #0x15
	BLO      |arm_080546C8|
	SUBS     r2, r2, #0x20
	BLS      |arm_080546A8|
	RSB      r3, r2, #0x20
	CMP      r0, #0
	MOV      r0, r1, LSR r2
	MOV      r2, r1, LSL r3
	ORRNE    r2, r2, #1
	MOV      r1, #0
|arm_080546A4|
	DCD     0xEA000019
|arm_080546A8|
	RSB      r3, r2, #0
	ADD      r2, r2, #0x20
	MOV      r1, r1, LSL r3
	ORR      r1, r1, r0, lsr r2
	MOV      r2, r0, LSL r3
	MOV      r0, r1
	MOV      r1, #0
|arm_080546C4|
	DCD     0xEA000011
|arm_080546C8|
	STMDB    sp!, {r4}
	RSB      r3, r2, #0x20
	MOV      r4, r0, LSL r3
	MOV      r3, r1, LSL r3
	ORR      r0, r3, r0, lsr r2
	MOV      r1, r1, LSR r2
	MOV      r2, r4
	LDMIA    sp!, {r4}
|arm_080546E8|
	DCD     0xEA000008
|arm_080546EC|
	ORRS     r2, r0, r1, lsl #12
	MOV      r0, #0
	MOV      r1, #0
	MOV      r2, #128, 8
	ADDNE    r2, r2, #1
|arm_08054700|
	DCD     0xEA000002
|arm_08054704|
	MOV      r2, #1
	MOV      r1, #0
	MOV      r0, #0
	CODE16
	CODE16
	EXPORT |sub_08054710|
	EXPORT |sub_08054714|
	EXPORT |sub_0805477C|
