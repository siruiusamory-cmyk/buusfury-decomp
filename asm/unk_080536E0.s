	CODE16
|unk_080536E0|
; cited by 0x0805375A (a pc-relative load targets 0x0805375C)
	CODE32
|arm_080536E0|
	STMDB    sp!, {r4, lr}
	LDR      ip, [pc, #0x254]
|arm_080536E8|
	DCD     0xE1DC4081
|arm_080536EC|
	DCD     0x11DC4083
	BEQ      |arm_080538D0|
	TEQ      r1, r3
	EORMI    r3, r3, #128, 8
	BMI      |arm_080534C8|
|arm_08053700|
	SUBS     r4, r0, r2
	SBCS     lr, r1, r3
	BHS      |arm_08053720|
	EOR      lr, lr, #128, 8
	ADDS     r2, r2, r4
	ADC      r3, r3, lr
	SUBS     r0, r0, r4
	SBC      r1, r1, lr
|arm_08053720|
	MOV      r4, r1, LSR #0x14
	SUB      lr, r4, r3, lsr #20
	TST      ip, r3, lsl #1
	BEQ      |arm_08053868|
	BIC      r1, r1, r4, lsl #20
	BIC      r3, r3, ip, asr #1
	RSBS     r2, r2, #0
	RSC      r3, r3, ip, asr #1
|arm_08053740|
	RSBS     ip, lr, #0x20
	BLO      |arm_0805378C|
	ADDS     r0, r0, r2, lsr lr
	ADC      r1, r1, r3, asr lr
	ADDS     r0, r0, r3, lsl ip
	ADCS     r1, r1, #0
	BMI      |arm_080537B4|
|arm_0805375C|
	ADD      r1, r1, r4, lsl #20
	LDMIA    sp!, {r4, lr}
	MOVS     r2, r2, LSL ip
	MOV      ip, #0x40000012
	BXPL     lr
	ADDS     r0, r0, #1
	CMPNE    r2, #128, 8
	BXNE     lr
	CMP      r0, #0
	ADDEQ    r1, r1, #1
|arm_08053784|
	DCD     0x13C00001
	BX       lr
|arm_0805378C|
	ADDS     ip, r2, r2
	ADC      r2, r3, r3
	MOVNE    ip, #1
	ORR      r2, ip, r2, lsl #1
	SUB      lr, lr, #0x20
	RSBS     ip, lr, #0x1e
	BLS      |arm_08053848|
	ADDS     r0, r0, r3, asr lr
	SBCS     r1, r1, #0
	BPL      |arm_0805375C|
|arm_080537B4|
	ADD      ip, ip, #1
	MOVS     ip, r2, LSL ip
	ADCS     r0, r0, r0
	ADC      r1, r1, r1
	ADD      lr, r1, r4, lsl #21
	MOVS     lr, lr, LSR #0x15
	BLS      |arm_080537F4|
	ADD      r1, r1, r4, lsl #20
	LDMIA    sp!, {r4, lr}
	ADDS     r0, r0, ip, lsr #31
	CMPLO    ip, #128, 8
	BXNE     lr
	CMP      r0, #0
	ADDEQ    r1, r1, #1
|arm_080537EC|
	DCD     0x13C00001
	BX       lr
|arm_080537F4|
	BHS      |arm_08053854|
	ADDS     r1, r1, #128, 18
	CMPEQ    r0, #0
|arm_08053800|
	DCD     0x08BD4010
	BEQ      |arm_080538AC|
	MOV      lr, r4, LSR #0xb
	BIC      r4, r4, #128, 28
	SUB      r4, r4, #2
|arm_08053814|
	ADDS     r0, r0, r0
	ADC      r1, r1, r1
	SUB      r4, r4, #1
	TST      r1, #64, 18
	BEQ      |arm_08053814|
	ADD      r1, r1, lr, lsl #31
	ADD      r1, r1, r4, lsl #20
	CMP      r4, #0
	LDMIA    sp!, {r4, lr}
	BXGT     lr
	ADD      r1, r1, #96, 8
	MOV      ip, #0x12
	B        |arm_08054618|
|arm_08053848|
	ADD      r1, r1, r4, lsl #20
	LDMIA    sp!, {r4, lr}
	BX       lr
|arm_08053854|
	MOVS     r1, r1, ASR #1
	MOV      r0, r0, RRX
	ADD      r1, r1, r4, lsl #20
	LDMIA    sp!, {r4, lr}
	B        |arm_080538B4|
|arm_08053868|
	ORRS     ip, r2, r3, lsl #12
	BEQ      |arm_080538A0|
	MOVS     ip, r4, LSL #0x15
	BIC      r1, r1, r4, lsl #20
	BEQ      |arm_08053890|
	BIC      r3, r3, #128, 8
	SUB      lr, lr, #1
	RSBS     r2, r2, #0
	RSC      r3, r3, #0
	B        |arm_08053740|
|arm_08053890|
	SUBS     r0, r0, r2
	SBC      r1, r1, r3
	LDMIA    sp!, {r4, lr}
	B        |arm_080538B4|
|arm_080538A0|
	LDMIA    sp!, {r4, lr}
	ORRS     ip, r0, r1, lsl #1
	BNE      |arm_080538B4|
|arm_080538AC|
	MOV      r1, #0
	BX       lr
|arm_080538B4|
	MOV      ip, #0x12
|arm_080538B8|
	MOVS     r2, r1, LSL #1
	TSTEQ    r0, r0
	BEQ      |arm_080538AC|
	CMP      r2, #128, 18
	BXHS     lr
	B        |arm_08054780|
|arm_080538D0|
	CMP      r0, #1
	ADC      r4, r1, r1
	CMP      r2, #1
	ADC      lr, r3, r3
	CMP      r4, ip
	CMPLS    lr, ip
	LDR      ip, [pc, #0x5c]
	LDMIA    sp!, {r4, lr}
	BHI      |arm_08053954|
	B        |arm_080538F8|
|arm_080538F8|
	CMP      r0, #1
	ADC      r0, r1, r1
	CMP      r2, #1
	ADC      r2, r3, r3
	CMP      r0, r2
	BEQ      |arm_08053928|
	CMN      r0, #128, 18
	MOVEQ    r0, #0
	BXEQ     lr
	EOR      r1, r3, #128, 8
	MOV      r0, #0
	BX       lr
|arm_08053928|
	MOV      r0, #0
	TEQ      r1, r3
	BXMI     lr
	MOV      r2, #0
	LDR      ip, [pc, #0xc]
	CODE16
	CODE16
	CODE16
|dat_0805393C|
	DCW      0x03c3
	DCW      0xea00
	DCW      0x0000
	DCW      0xffe0
	DCW      0x0011
	DCW      0x1000
	DCW      0x0011
	DCW      0x0400
	DCW      0x0012
	DCW      0x0400
	DCW      0x4778
	DCW      0x0000

