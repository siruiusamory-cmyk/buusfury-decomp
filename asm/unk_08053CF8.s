	CODE16
|unk_08053CF8|
; cited by 0x08053A60 (a pc-relative load targets 0x08053CF8)
	CODE32
|arm_08053CF8|
	STMDB    sp!, {r7, r8, fp, lr}
	STMDB    sp!, {r4, r5, r6}
	MOV      r4, r3, LSR #0x10
	MOV      r6, r2, LSR #0x10
	BIC      r5, r3, r4, lsl #16
	BIC      lr, r2, r6, lsl #16
	ADD      r7, pc, #112, 30
	LDRB     r7, [r7, r4, lsr #8]
	MLA      ip, r4, r7, r7
	RSB      ip, ip, #128, 16
	MUL      r7, ip, r7
	MOV      r7, r7, LSR #0x13
	ADD      r7, r7, #2
	MOV      ip, r3, LSR #0xd
	MLA      r8, ip, r7, r7
	RSB      r8, r8, #128, 10
	MOV      ip, r8, LSR #0x10
	BIC      r8, r8, ip, lsl #16
	MUL      r2, r8, r7
	MUL      r3, ip, r7
	ADD      r7, r3, r2, lsr #16
	MOV      r7, r7, LSR #6
	MOVS     r1, r1, LSR #1
	MOVS     r0, r0, RRX
	MOVLO    fp, #0
	MOVHS    fp, #128, 8
	MOV      ip, r1, LSR #0xf
	MUL      r8, r7, ip
	MOV      r8, r8, LSR #0x10
	MUL      ip, r8, r6
	SUBS     r0, r0, ip
	MUL      ip, r4, r8
	SBC      r1, r1, ip
	MUL      ip, r8, lr
	SUBS     fp, fp, ip, lsl #16
	SBCS     r0, r0, ip, lsr #16
	MUL      ip, r8, r5
	SUBLO    r0, r0, ip, lsl #16
	SUBHSS   r0, r0, ip, lsl #16
	SBC      r1, r1, ip, lsr #16
	MOV      r3, r8, LSL #0x10
	MOV      ip, r1, LSR #2
	MUL      r8, r7, ip
	MOV      r8, r8, LSR #0x10
	MUL      ip, r8, r6
	SUBS     fp, fp, ip, lsl #19
	SBCS     r0, r0, ip, lsr #13
	MUL      ip, r4, r8
	SUBLO    r0, r0, ip, lsl #19
	SUBHSS   r0, r0, ip, lsl #19
	SBC      r1, r1, ip, lsr #13
	MUL      ip, r8, lr
	SUBS     fp, fp, ip, lsl #3
	SBCS     r0, r0, ip, lsr #29
	MUL      ip, r8, r5
	SUBLO    r0, r0, ip, lsl #3
	SUBHSS   r0, r0, ip, lsl #3
	SBC      r1, r1, ip, lsr #29
	MOV      r1, r1, LSL #0x1a
	ORR      r1, r1, r0, lsr #6
	MOV      r0, r0, LSL #0x1a
	ORR      r0, r0, fp, lsr #6
	MOV      fp, fp, LSL #0x1a
	ADD      r3, r3, r8, lsl #3
	MOV      ip, r1, LSR #0xf
	MUL      r8, r7, ip
	MOV      r8, r8, LSR #0x10
	MUL      ip, r8, r6
	SUBS     r0, r0, ip
	MUL      ip, r4, r8
	SBC      r1, r1, ip
	MUL      ip, r8, lr
	SUBS     fp, fp, ip, lsl #16
	SBCS     r0, r0, ip, lsr #16
	MUL      ip, r8, r5
	SUBLO    r0, r0, ip, lsl #16
	SUBHSS   r0, r0, ip, lsl #16
	SBC      r1, r1, ip, lsr #16
	MOV      r2, r8, LSL #0x16
	ADD      r3, r3, r8, lsr #10
	MOV      ip, r1, LSR #2
	MUL      r8, r7, ip
	MOV      r8, r8, LSR #0x10
	MUL      ip, r8, r6
	SUBS     fp, fp, ip, lsl #19
	SBCS     r0, r0, ip, lsr #13
	MUL      ip, r4, r8
	SUBLO    r0, r0, ip, lsl #19
	SUBHSS   r0, r0, ip, lsl #19
	SBC      r1, r1, ip, lsr #13
	MUL      ip, r8, lr
	SUBS     fp, fp, ip, lsl #3
	SBCS     r0, r0, ip, lsr #29
	MUL      ip, r8, r5
	SUBLO    r0, r0, ip, lsl #3
	SUBHSS   r0, r0, ip, lsl #3
	SBC      r1, r1, ip, lsr #29
	MOV      r1, r1, LSL #0x1a
	ORR      r1, r1, r0, lsr #6
	MOV      r0, r0, LSL #0x1a
	ORR      r0, r0, fp, lsr #6
	MOV      fp, fp, LSL #0x1a
	ADDS     r2, r2, r8, lsl #9
	ADC      r3, r3, #0
	ORR      r4, r5, r4, lsl #16
	ORR      r5, lr, r6, lsl #16
	MOV      lr, #0
	ADDS     fp, fp, fp
	ADCS     r0, r0, r0
	ADC      r1, r1, r1
	SUBS     r8, r0, r5
	SBCS     ip, r1, r4
	MOVHS    r0, r8
	MOVHS    r1, ip
	ADC      lr, lr, lr
	MOV      r6, #0
	ADDS     fp, fp, fp
	ADCS     r0, r0, r0
	ADCS     r1, r1, r1
	ADC      r6, r6, r6
	SUBS     r8, r0, r5
	SBCS     ip, r1, r4
	SBCS     r6, r6, #0
	MOVHS    r0, r8
	MOVHS    r1, ip
	ADC      lr, lr, lr
	MOV      r6, #0
	ADDS     fp, fp, fp
	ADCS     r0, r0, r0
	ADCS     r1, r1, r1
	ADC      r6, r6, r6
	SUBS     r8, r0, r5
	SBCS     ip, r1, r4
	SBCS     r6, r6, #0
	MOVHS    r0, r8
	MOVHS    r1, ip
	ADC      lr, lr, lr
	ORRS     r7, r1, r0
	MOVNE    r7, #1
	ADDS     r0, r2, lr, lsl #9
	ADCS     r1, r3, #0
	MOVMI    r3, #2
	MOVPL    r3, #1
	ORR      r0, r0, r7
|arm_08053F38|
	DCD     0x48BD00F0
|arm_08053F3C|
	DCD     0x48BD4900
	BXMI     lr
	ADDS     r0, r0, r0
	ADC      r1, r1, r1
	LDMIA    sp!, {r4, r5, r6, r7}
	LDMIA    sp!, {r8, fp, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08053F58|
	EXPORT |sub_08053FEC|
	EXPORT |sub_08053FF8|
