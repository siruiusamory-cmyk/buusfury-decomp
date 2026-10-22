	CODE16
|unk_080534A8|
; cited by 0x080534C6 (a pc-relative load targets 0x080534C8)
	CODE32
|arm_080534A8|
	STMDB    sp!, {r4, lr}
	LDR      ip, [pc, #0x48c]
|arm_080534B0|
	DCD     0xE1DC4081
|arm_080534B4|
	DCD     0x11DC4083
	BEQ      |arm_08053624|
	TEQ      r1, r3
	EORMI    r3, r3, #128, 8
	BMI      |arm_08053700|
|arm_080534C8|
	SUBS     r4, r0, r2
	SBCS     lr, r1, r3
	BHS      |arm_080534E4|
	ADDS     r2, r2, r4
	ADC      r3, r3, lr
	SUBS     r0, r0, r4
	SBC      r1, r1, lr
|arm_080534E4|
	MOV      r4, r1, LSR #0x14
	SUB      lr, r4, r3, lsr #20
	TST      ip, r3, lsl #1
	BEQ      |arm_080535D8|
	BIC      r1, r1, r4, lsl #20
	BIC      r3, r3, ip
	ORR      r3, r3, #64, 18
|arm_08053500|
	RSBS     ip, lr, #0x20
	BLO      |arm_08053560|
	ADDS     r0, r0, r2, lsr lr
	ADC      r1, r1, r3, lsr lr
	ADDS     r0, r0, r3, lsl ip
	ADCS     r1, r1, #0
	CMP      r1, #64, 18
	BHS      |arm_08053588|
	ADD      r1, r1, r4, lsl #20
|arm_08053524|
	LDMIA    sp!, {r4, lr}
	MOVS     r2, r2, LSL ip
	BXPL     lr
	ADDS     r0, r0, #1
|arm_08053534|
	DCD     0x31B02082
	BXNE     lr
|arm_0805353C|
	CMP      r0, #0
|arm_08053540|
	DCD     0x13C00001
	ADCEQ    r1, r1, #0
|arm_08053548|
	MOV      r3, r1, LSL #1
	CMN      r3, #128, 18
	BXLO     lr
	LDR      ip, [pc, #0x3e8]
	SUBHS    r1, r1, #96, 8
	B        |arm_08054850|
|arm_08053560|
	CMP      r2, #1
	ADC      r2, r3, r3
	SUB      lr, lr, #0x20
	RSBS     ip, lr, #0x1f
	MOVLO    ip, #0
	ADDHSS   r0, r0, r3, lsr lr
	ADC      r1, r1, r4, lsl #20
	CMP      r4, r1, lsr #20
	BEQ      |arm_08053524|
	SUB      r1, r1, r4, lsl #20
|arm_08053588|
	ADD      r1, r1, #64, 18
	MOVS     r1, r1, LSR #1
	ADD      r1, r1, r4, lsl #20
	LDMIA    sp!, {r4, lr}
	MOVS     r0, r0, RRX
	BLO      |arm_080535C0|
	ADCS     r0, r0, #0
|arm_080535A4|
	DCD     0x31B0CC12
	BNE      |arm_080535C0|
	B        |arm_0805353C|
|arm_080535B0|
	DCD     0xE2900001
|arm_080535B4|
	DCD     0x31B02082
	BNE      |arm_08053548|
	B        |arm_0805353C|
|arm_080535C0|
	MOV      r3, r1, LSL #1
	CMN      r3, #128, 18
	BXLO     lr
	LDR      ip, [pc, #0x370]
	SUB      r1, r1, #96, 8
	B        |arm_08054850|
|arm_080535D8|
	ORRS     ip, r2, r3, lsl #1
	BEQ      |arm_08053608|
	MOVS     ip, r4, LSL #0x15
	BIC      r1, r1, r4, lsl #20
|arm_080535E8|
	DCD     0x13C33480
	SUBNE    lr, lr, #1
	BNE      |arm_08053500|
	LDMIA    sp!, {r4, lr}
	ADDS     r0, r0, r2
	ADC      r1, r1, r3
	MOV      ip, #0x11
	B        |arm_080538B8|
|arm_08053608|
	MOVS     ip, r4, LSL #0x15
	LDMIA    sp!, {r4, lr}
	BXNE     lr
	ORRS     ip, r0, r1, lsl #1
	BXEQ     lr
	MOV      ip, #0x11
	B        |arm_080538B8|
|arm_08053624|
	CMP      r0, #1
	ADC      r4, r1, r1
	CMP      r2, #1
	ADC      lr, r3, r3
	CMP      r4, ip
	CMPLS    lr, ip
	LDR      ip, [pc, #0x304]
	LDMIA    sp!, {r4, lr}
	BHI      |arm_08053954|
	B        |arm_0805364C|
|arm_0805364C|
	CMP      r0, #1
	ADC      r0, r1, r1
	CMP      r2, #1
	ADC      r2, r3, r3
	CMP      r0, r2
	BEQ      |arm_0805367C|
	CMN      r0, #128, 18
	MOVEQ    r0, #0
	BXEQ     lr
	MOV      r1, r3
	MOV      r0, #0
	BX       lr
|arm_0805367C|
	MOV      r0, #0
	TEQ      r1, r3
	BXPL     lr
	MOV      r2, #0
	LDR      ip, [pc, #0x2b4]
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08053694|
