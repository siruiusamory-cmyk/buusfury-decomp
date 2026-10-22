	CODE16
|unk_08053A44|
; cited by 0x080536B6 (a pc-relative load targets 0x08053AB4)
	CODE32
	STMDB    sp!, {r4, r5, r6, lr}
|arm_08053A48|
	LDR      ip, [pc, #0x588]
|arm_08053A4C|
	DCD     0xE1DC4221
|arm_08053A50|
	DCD     0x11DC4223
	BEQ      |arm_08053C88|
	AND      r4, ip, r1, lsr #4
	EOR      r5, r1, r3
	ORR      r4, r4, r5, lsr #31
	ANDS     r5, ip, r3, lsr #4
	TSTNE    r1, ip, lsl #4
	BEQ      |arm_08053B48|
|arm_08053A70|
	SUB      r4, r4, r5
	ADD      r4, r4, #0x3fc0000
	MOV      r1, r1, LSL #0xb
	MOV      r3, r3, LSL #0xb
	ORR      r1, r1, r0, lsr #21
	ORR      r3, r3, r2, lsr #21
	ORR      r1, r1, #128, 8
	ORR      r3, r3, #128, 8
	MOV      r0, r0, LSL #0xb
	MOV      r2, r2, LSL #0xb
	BL       |arm_08053CF8|
	ADD      r3, r3, r4, asr #16
	MOVS     r6, r0, LSL #0x15
	MOV      r0, r0, LSR #0xb
	ORR      r0, r0, r1, lsl #21
	MOV      r1, r1, LSR #0xb
	ADD      r1, r1, r3, lsl #20
	EOR      r1, r1, r4, lsl #31
	BEQ      |arm_08053AE8|
	MOVS     lr, r6, LSL #1
	MOVLO    r6, #192, 8
	BLO      |arm_08053AE8|
	MOVNE    r3, #0
	MOVEQ    r3, #128, 8
	ADCS     r0, r0, #0
	ADC      r1, r1, #0
	MOV      r6, #64, 8
	TST      r0, r3, lsr #31
	BIC      r0, r0, r3, lsr #31
	MOVNE    r6, #192, 8
|arm_08053AE8|
	TEQ      r1, r4, lsl #31
	LDR      lr, [pc, #0x4e8]
	BMI      |arm_08053B28|
	TST      r1, lr
	BICNES   lr, lr, r1
	BEQ      |arm_08053B28|
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_08053B08|
	DCD     0xE1B05F84
	TSTPL    lr, #128, 16
	TSTMI    lr, #64, 16
	MOVEQ    r6, #64, 8
	MOVNE    r6, #192, 8
	ADDEQS   r0, r0, #1
	ADC      r1, r1, #0
	B        |arm_08053AE8|
|arm_08053B28|
	CMP      r4, #64, 12
	ADDLE    r1, r1, #96, 8
	SUBGE    r1, r1, #96, 8
	ORR      ip, r6, #0x14
	ORRGE    ip, ip, #64, 10
	LDMIA    sp!, {r4, r5, r6, lr}
	BLE      |arm_08054618|
	B        |arm_08054850|
|arm_08053B48|
	ORRS     lr, r0, r1, lsl #1
	BEQ      |arm_08053B6C|
	ORRS     lr, r2, r3, lsl #1
	BEQ      |arm_08053B84|
	TST      r5, r5
	BEQ      |arm_08053C0C|
|arm_08053B60|
	DCD     0xE3D4E001
	BEQ      |arm_08053B90|
	B        |arm_08053A70|
|arm_08053B6C|
	ORRS     lr, r2, r3, lsl #1
	BEQ      |arm_08053CE8|
	TST      r3, r3
	EORMI    r1, r1, #128, 8
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_08053B84|
	LDR      ip, [pc, #0x454]
	LDMIA    sp!, {r4, r5, r6, lr}
	B        |arm_08054850|
|arm_08053B90|
	ADD      r4, r4, #64, 22
	BIC      r1, r1, #128, 8
	ORRS     lr, r1, r0, lsr #12
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    r4, r4, #80, 18
	TST      r1, r1
	MOVEQ    r1, r0, LSR #0xc
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    r4, r4, #80, 18
	MOV      r6, #0
	MOVS     lr, r1, LSR #5
	MOVEQ    r1, r1, LSL #0x10
	ADDEQ    r6, r6, #0x10
	MOVS     lr, r1, LSR #0xd
	MOVEQ    r1, r1, LSL #8
	ADDEQ    r6, r6, #8
	MOVS     lr, r1, LSR #0x11
	MOVEQ    r1, r1, LSL #4
	ADDEQ    r6, r6, #4
	MOVS     lr, r1, LSR #0x13
	MOVEQ    r1, r1, LSL #2
	ADDEQ    r6, r6, #2
	MOVS     lr, r1, LSR #0x14
	MOVEQ    r1, r1, LSL #1
	ADDEQ    r6, r6, #1
	SUB      r4, r4, r6, lsl #16
	MOV      lr, r0, LSL r6
	RSB      r6, r6, #0x20
	ORR      r1, r1, r0, lsr r6
	MOV      r0, lr
	B        |arm_08053A70|
|arm_08053C0C|
	ADD      r5, r5, #64, 22
	BIC      r3, r3, #128, 8
	ORRS     lr, r3, r2, lsr #12
	MOVEQ    r2, r2, LSL #0x14
	SUBEQ    r5, r5, #80, 18
	TST      r3, r3
	MOVEQ    r3, r2, LSR #0xc
	MOVEQ    r2, r2, LSL #0x14
	SUBEQ    r5, r5, #80, 18
	MOV      r6, #0
	MOVS     lr, r3, LSR #5
	MOVEQ    r3, r3, LSL #0x10
	ADDEQ    r6, r6, #0x10
	MOVS     lr, r3, LSR #0xd
	MOVEQ    r3, r3, LSL #8
	ADDEQ    r6, r6, #8
	MOVS     lr, r3, LSR #0x11
	MOVEQ    r3, r3, LSL #4
	ADDEQ    r6, r6, #4
	MOVS     lr, r3, LSR #0x13
	MOVEQ    r3, r3, LSL #2
	ADDEQ    r6, r6, #2
	MOVS     lr, r3, LSR #0x14
	MOVEQ    r3, r3, LSL #1
	ADDEQ    r6, r6, #1
	SUB      r5, r5, r6, lsl #16
	MOV      lr, r2, LSL r6
	RSB      r6, r6, #0x20
	ORR      r3, r3, r2, lsr r6
	MOV      r2, lr
	B        |arm_08053B60|
|arm_08053C88|
	MOV      lr, r1, LSL #1
	MOV      r5, r3, LSL #1
	CMP      lr, ip, lsl #5
	CMPEQ    r0, #0
	CMPLS    r5, ip, lsl #5
	CMPEQ    r2, #0
	LDMIA    sp!, {r4, r5, r6, lr}
	LDR      ip, [pc, #0x338]
	BHI      |arm_08053954|
	B        |arm_08053CB0|
|arm_08053CB0|
	LDR      ip, [pc, #0x320]
|arm_08053CB4|
	DCD     0xE1DC0221
	BNE      |arm_08053CD8|
|arm_08053CBC|
	DCD     0xE1DC0223
	MOV      r0, #0
	BEQ      |arm_08053CEC|
	EORS     r3, r1, r3
	BIC      r1, r1, #128, 8
	ORRMI    r1, r1, #128, 8
	BX       lr
|arm_08053CD8|
	EOR      r3, r1, r3
	MOV      r0, #0
	AND      r1, r3, #128, 8
	BX       lr
|arm_08053CE8|
	LDMIA    sp!, {r4, r5, r6, lr}
|arm_08053CEC|
	LDR      ip, [pc, #0x2f0]
	B        |arm_08054850|
	CODE16
	CODE16
	EXPORT |sub_08053CF4|
