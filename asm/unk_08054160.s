	CODE16
|unk_08054160|
; cited by 0x08053F3A (a pc-relative load targets 0x08054230)
	CODE32
|arm_08054160|
	STMDB    sp!, {r4, r5, r6, lr}
	LDR      ip, [pc, #0x2a4]
|arm_08054168|
	DCD     0xE1DCE221
|arm_0805416C|
	DCD     0x11DCE223
	BEQ      |arm_080543BC|
	AND      lr, ip, r1, lsr #4
	EOR      r5, r1, r3
	ORR      lr, lr, r5, lsr #31
	ANDS     r5, ip, r3, lsr #4
	TSTNE    r1, ip, lsl #4
	BEQ      |arm_08054294|
|arm_0805418C|
	ADD      lr, lr, r5
	SUB      lr, lr, #0x3fc0000
	BIC      r1, r1, ip, lsl #5
	BIC      r3, r3, ip, lsl #5
	ORR      r1, r1, #64, 18
	ORR      r3, r3, #64, 18
	UMULL    r4, ip, r1, r2
	UMULL    r6, r5, r0, r3
	ADDS     r6, r6, r4
	ADCS     r5, r5, ip
	UMULL    r4, ip, r1, r3
	ADC      r3, ip, #0
	UMULL    r1, ip, r0, r2
	ADDS     r6, r6, ip
	ADCS     r5, r5, r4
	ADCS     r3, r3, #0
	TST      r1, r1
	ORRNE    r6, r6, #1
	MVN      r2, #3
	MOV      ip, #0x14
	CMP      r3, #128, 30
	ADC      ip, ip, #0
	ADC      r2, r2, lr, asr #16
	RSB      r4, ip, #0x20
	MOV      r1, r3, LSL r4
	MOV      r0, r5, LSL r4
	ORR      r1, r1, r5, lsr ip
	ORR      r0, r0, r6, lsr ip
	ADD      r1, r1, r2, lsl #20
	EOR      r1, r1, lr, lsl #31
	MOVS     r4, r6, LSL r4
	BEQ      |arm_08054234|
	MOVS     ip, r4, LSL #1
	MOVLO    r4, #192, 8
	BLO      |arm_08054234|
	ORREQ    r3, r3, #128, 8
	ADCS     r0, r0, #0
	ADC      r1, r1, #0
	MOV      r4, #64, 8
	TST      r0, r3, lsr #31
	BIC      r0, r0, r3, lsr #31
	MOVNE    r4, #192, 8
|arm_08054234|
	TEQ      r1, lr, lsl #31
	LDR      ip, [pc, #0x1d4]
	BMI      |arm_08054274|
	TST      r1, ip
	BICNES   ip, ip, r1
	BEQ      |arm_08054274|
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_08054254|
	DCD     0xE1B04F8E
	TSTPL    ip, #128, 16
	TSTMI    ip, #64, 16
	MOVEQ    r4, #64, 8
	MOVNE    r4, #192, 8
	ADDEQS   r0, r0, #1
	ADC      r1, r1, #0
	B        |arm_08054234|
|arm_08054274|
	CMP      lr, #64, 12
	ADDLE    r1, r1, #96, 8
	SUBGE    r1, r1, #96, 8
	ORR      ip, r4, #0x13
	ORRGE    ip, ip, #64, 10
	LDMIA    sp!, {r4, r5, r6, lr}
	BLE      |arm_08054618|
	B        |arm_08054850|
|arm_08054294|
	ORRS     r4, r0, r1, lsl #1
	ORRNES   r4, r2, r3, lsl #1
	BEQ      |arm_080542B4|
	TST      r5, r5
	BEQ      |arm_08054340|
|arm_080542A8|
	DCD     0xE3DE4001
	BEQ      |arm_080542C4|
	B        |arm_0805418C|
|arm_080542B4|
	MOV      r0, #0
	MOV      r1, lr, LSL #0x1f
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_080542C4|
	ADD      lr, lr, #64, 22
	BIC      r1, r1, #128, 8
	ORRS     r6, r1, r0, lsr #12
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    lr, lr, #80, 18
	TST      r1, r1
	MOVEQ    r1, r0, LSR #0xc
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    lr, lr, #80, 18
	MOV      r4, #0
	MOVS     r6, r1, LSR #5
	MOVEQ    r1, r1, LSL #0x10
	ADDEQ    r4, r4, #0x10
	MOVS     r6, r1, LSR #0xd
	MOVEQ    r1, r1, LSL #8
	ADDEQ    r4, r4, #8
	MOVS     r6, r1, LSR #0x11
	MOVEQ    r1, r1, LSL #4
	ADDEQ    r4, r4, #4
	MOVS     r6, r1, LSR #0x13
	MOVEQ    r1, r1, LSL #2
	ADDEQ    r4, r4, #2
	MOVS     r6, r1, LSR #0x14
	MOVEQ    r1, r1, LSL #1
	ADDEQ    r4, r4, #1
	SUB      lr, lr, r4, lsl #16
	MOV      r6, r0, LSL r4
	RSB      r4, r4, #0x20
	ORR      r1, r1, r0, lsr r4
	MOV      r0, r6
	B        |arm_0805418C|
|arm_08054340|
	ADD      r5, r5, #64, 22
	BIC      r3, r3, #128, 8
	ORRS     r6, r3, r2, lsr #12
	MOVEQ    r2, r2, LSL #0x14
	SUBEQ    r5, r5, #80, 18
	TST      r3, r3
	MOVEQ    r3, r2, LSR #0xc
	MOVEQ    r2, r2, LSL #0x14
	SUBEQ    r5, r5, #80, 18
	MOV      r4, #0
	MOVS     r6, r3, LSR #5
	MOVEQ    r3, r3, LSL #0x10
	ADDEQ    r4, r4, #0x10
	MOVS     r6, r3, LSR #0xd
	MOVEQ    r3, r3, LSL #8
	ADDEQ    r4, r4, #8
	MOVS     r6, r3, LSR #0x11
	MOVEQ    r3, r3, LSL #4
	ADDEQ    r4, r4, #4
	MOVS     r6, r3, LSR #0x13
	MOVEQ    r3, r3, LSL #2
	ADDEQ    r4, r4, #2
	MOVS     r6, r3, LSR #0x14
	MOVEQ    r3, r3, LSL #1
	ADDEQ    r4, r4, #1
	SUB      r5, r5, r4, lsl #16
	MOV      r6, r2, LSL r4
	RSB      r4, r4, #0x20
	ORR      r3, r3, r2, lsr r4
	MOV      r2, r6
	B        |arm_080542A8|
|arm_080543BC|
	MOV      r5, r1, LSL #1
	MOV      r6, r3, LSL #1
	CMP      r5, ip, lsl #5
	CMPEQ    r0, #0
	CMPLS    r6, ip, lsl #5
	CMPEQ    r2, #0
	LDMIA    sp!, {r4, r5, r6, lr}
	LDR      ip, [pc, #0x38]
	BHI      |arm_08053954|
	B        |arm_080543E4|
|arm_080543E4|
	ORRS     ip, r0, r1, lsl #1
	ORRNES   ip, r2, r3, lsl #1
	BEQ      |arm_08054408|
	EOR      r1, r1, r3
	MOV      r0, #0
	AND      r1, r1, #128, 8
	ORR      r1, r1, #0x7f000000
	ORR      r1, r1, #240, 16
	BX       lr
|arm_08054408|
	LDR      ip, [pc, #8]
	CODE16
	CODE16
	EXPORT |sub_0805440C|
