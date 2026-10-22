	CODE16
|unk_08054420|
; cited by 0x08054254 (a pc-relative load targets 0x08054490)
	CODE32
	STMDB    sp!, {r4, r5, r6, lr}
	MOV      ip, #112, 8
	ORR      ip, ip, #0xff00000
	TST      r1, ip
	BEQ      |arm_08054554|
	BICS     lr, ip, r1
	BEQ      |arm_080545E0|
	TST      r1, #128, 8
	BNE      |arm_08054604|
	MOV      ip, r1, LSR #0x14
	BIC      r1, r1, ip, lsl #20
	ORR      r1, r1, #64, 18
|arm_08054450|
	ADD      ip, ip, #0xfd
	MOVS     ip, ip, LSR #1
	ADD      ip, ip, #96, 30
	BLO      |arm_08054468|
	MOVS     r0, r0, LSL #1
	ADC      r1, r1, r1
|arm_08054468|
	MOV      r1, r1, LSL #0xa
	ORR      r1, r1, r0, lsr #22
	MOV      r0, r0, LSL #0xa
	MOV      r2, #64, 8
	MOV      r3, #0
	SUB      r1, r1, #64, 8
	MOV      lr, #64, 10
|arm_08054484|
	SUBS     r4, r1, r2
	SUBHSS   r4, r4, lr
	MOVHS    r1, r4
	ADDHS    r2, r2, lr, lsl #1
	MOVS     r0, r0, LSL #1
	ADC      r1, r1, r1
	MOVS     lr, lr, LSR #1
	BNE      |arm_08054484|
	SBCS     r4, r1, r2
	BLO      |arm_080544C0|
	SUBS     r5, r0, #128, 8
	SBCS     r4, r4, #0
	MOVHS    r1, r4
	MOVHS    r0, r5
	ADDHS    r2, r2, #1
|arm_080544C0|
	MOVS     r0, r0, LSL #1
	ADC      r1, r1, r1
	MOV      lr, #64, 8
|arm_080544CC|
	SUBS     r5, r0, r3
	SBCS     r4, r1, r2
	BLO      |arm_080544EC|
	SUBS     r5, r5, lr
	SBCS     r4, r4, #0
	MOVHS    r1, r4
	MOVHS    r0, r5
	ADDHS    r3, r3, lr, lsl #1
|arm_080544EC|
	MOVS     r0, r0, LSL #1
	ADC      r1, r1, r1
	MOV      lr, lr, LSR #1
	CMP      lr, #0x80
	BNE      |arm_080544CC|
	ORRS     r4, r1, r0
	MOVNE    r4, #2
	MOVS     r0, r3, LSR #0xa
	ORR      r0, r0, r2, lsl #22
	MOV      r1, r2, LSR #0xa
	ADD      r1, r1, ip, lsl #20
	MOVS     r4, r4, RRX
|arm_0805451C|
	DCD     0x08BD4070
	BXEQ     lr
	MOVS     r4, r4, LSL #1
	ADCS     r0, r0, #0
	ADC      r1, r1, #0
	TST      r4, r4
|arm_08054534|
	DCD     0x03C00001
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_08054540|
	DCD     0xE27EE840
	ADCS     r0, r0, #0
	ADC      r1, r1, #0
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
|arm_08054554|
	ORRS     ip, r0, r1, lsl #12
|arm_08054558|
	DCD     0x08BD4070
	BXEQ     lr
	TST      r1, r1
	BMI      |arm_08054604|
	MOV      ip, #1
	ORRS     lr, r1, r0, lsr #12
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    ip, ip, #0x14
	TST      r1, r1
	MOVEQ    r1, r0, LSR #0xc
	MOVEQ    r0, r0, LSL #0x14
	SUBEQ    ip, ip, #0x14
	MOV      r4, #0
	MOVS     lr, r1, LSR #5
	MOVEQ    r1, r1, LSL #0x10
	ADDEQ    r4, r4, #0x10
	MOVS     lr, r1, LSR #0xd
	MOVEQ    r1, r1, LSL #8
	ADDEQ    r4, r4, #8
	MOVS     lr, r1, LSR #0x11
	MOVEQ    r1, r1, LSL #4
	ADDEQ    r4, r4, #4
	MOVS     lr, r1, LSR #0x13
	MOVEQ    r1, r1, LSL #2
	ADDEQ    r4, r4, #2
	MOVS     lr, r1, LSR #0x14
	MOVEQ    r1, r1, LSL #1
	ADDEQ    r4, r4, #1
	SUB      ip, ip, r4
	MOV      r5, r0, LSL r4
	RSB      r4, r4, #0x20
	ORR      r1, r1, r0, lsr r4
	MOV      r0, r5
	B        |arm_08054450|
|arm_080545E0|
	LDMIA    sp!, {r4, r5, r6, lr}
	ORRS     ip, r0, r1, lsl #12
	LDR      ip, [pc, #0x20]
	BNE      |arm_08053998|
	B        |arm_080545F4|
|arm_080545F4|
	TST      r1, r1
	BXPL     lr
	LDR      ip, [pc, #0xc]
	B        |arm_08054850|
|arm_08054604|
	LDMIA    sp!, {r4, r5, r6, lr}
	LDR      ip, [pc]
	CODE16
	CODE16
	EXPORT |sub_0805460C|
