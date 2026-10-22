	CODE16
	EXPORT |sub_08046118|
	EXPORT |sub_08046A7A|
	EXPORT |loc_08046AA0|
	EXPORT |loc_08046AA4|
	EXPORT |sub_08046AA8|
	EXPORT |sub_08046AAE|
	EXPORT |loc_08046AB6|
	EXPORT |loc_08046AC0|
	EXPORT |loc_08046ACE|
	EXPORT |loc_08046ADC|
	EXPORT |loc_08046AFA|
	EXPORT |loc_08046B08|
|sub_08046118|
	STRB     r0, [r1, #4]
	BL       |loc_08045b40|
	POP      {r7}
	POP      {r3}
	BX       r3
	AREA UnusedGBARam8, CODE, READONLY
	CODE16
|unk_080462AC|
; cited by 0x080462B0 (a pc-relative load targets 0x08046A64)
	INCBIN	baserom.gba_0x462ac_0x46a7a.extracted
|sub_08046A7A|
	LSL      r0, r0, #0
	DCW      0xf996,0x0000
	STR      r2, [r1, r0]
	LSL      r0, r0, #0
	LSL      r6, r5, #7
	LDR      r1, [sp, #0x198]
	STR      r2, [r0, r0]
	LSL      r0, r0, #0
	LSL      r6, r5, #7
	LSL      r0, r0, #0
	STR      r3, [r0, r0]
	LSL      r0, r0, #0
	LSL      r0, r0, #8
	LSL      r0, r0, #0x10
	STR      r3, [r1, r0]
	LSL      r0, r0, #0
	STR      r3, [r0, r2]
	LSL      r0, r0, #0
|loc_08046AA0|
	BX       r0
	BX       r1
|loc_08046AA4|
	BX       r2
	BX       r3
|sub_08046AA8|
|unk_08046AA8|
	INCBIN	baserom.gba_0x46aa8_0x46aae.extracted
|sub_08046AAE|
	BX       r7
	PUSH     {r3, lr}
	BL       |loc_08046AB6|
|loc_08046AB6|
	BL       |loc_08046AC0|
	ADD      sp, #4
	POP      {r3}
	BX       r3
|loc_08046AC0|
	PUSH     {r3, r4, r5, lr}
	LDR      r5, [pc, #0x20]
	ADD      r5, pc
	LDR      r4, [pc, #0x20]
	ADD      r4, pc
	CMP      r5, r4
	BEQ      |loc_08046ADC|
|loc_08046ACE|
	SUB      r4, #4
	LDR      r0, [r4]
	ADD      r0, r4, r0
	BL       |loc_08046AA0|
	CMP      r5, r4
	BNE      |loc_08046ACE|
|loc_08046ADC|
	POP      {r3, r4, r5}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	MOV      r6, #0x30
	LSL      r0, r0, #0
	MOV      r6, #0x48
	LSL      r0, r0, #0
	PUSH     {r3, r4, r5, lr}
	LDR      r4, [pc, #0x20]
	ADD      r4, pc
	LDR      r5, [pc, #0x20]
	ADD      r5, pc
	CMP      r4, r5
	BEQ      |loc_08046B08|
|loc_08046AFA|
	LDR      r0, [r4]
	ADD      r0, r0, r4
	BL       |loc_08046AA0|
	ADD      r4, #4
	CMP      r4, r5
	BNE      |loc_08046AFA|
|loc_08046B08|
	POP      {r3, r4, r5}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	MOV      r3, #0xe4
	LSL      r0, r0, #0
	MOV      r6, #0
	LSL      r0, r0, #0
	BX       pc
	LSL      r0, r0, #0
|unk_08046B1C|
	CODE32
	ADDS     r0, r0, r2
	ADC      r1, r1, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_cmpu|
|__16_ll_cmpu|
	BX       pc
	LSL      r0, r0, #0
|unk_08046B2C|
	CODE32
	CMP      r1, r3
	CMPEQ    r0, r2
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_mul|
|__16_ll_mul|
	BX       pc
	LSL      r0, r0, #0
|unk_08046B3C|
	CODE32
|arm_08046B3C|
	STMDB    sp!, {r4, r5, r6, lr}
	MOV      lr, r0
	UMULL    r0, ip, r2, lr
	MLA      r1, r2, r1, ip
	MLA      r1, r3, lr, r1
	LDMIA    sp!, {r4, r5, r6, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046B58|
	EXPORT |sub_08046B5C|
	EXPORT |sub_08046B64|
	EXPORT |sub_08046B68|
	EXPORT |sub_08046B70|
|sub_08046B58|
	BX       pc
	LSL      r0, r0, #0
|sub_08046B5C|
|unk_08046B5C|
	CODE32
	MOV      r3, r2, ASR #0x20
	B        |arm_08046B3C|
	CODE16
|sub_08046B64|
	BX       pc
	LSL      r0, r0, #0
|sub_08046B68|
|unk_08046B68|
	CODE32
	MOV      r3, #0
	B        |arm_08046B3C|
	CODE16
|sub_08046B70|
	BX       pc
	LSL      r0, r0, #0
|unk_08046B74|
	CODE32
	MOV      r3, r1, ASR #0x1f
	MOV      r2, r1
	MOV      r1, r0, ASR #0x1f
	B        |arm_08046B3C|
	CODE16
	CODE16
	EXPORT |__16_ll_neg|
|__16_ll_neg|
	BX       pc
	LSL      r0, r0, #0
|unk_08046B88|
	CODE32
	RSBS     r0, r0, #0
	RSC      r1, r1, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_rsb|
|__16_ll_rsb|
	BX       pc
	LSL      r0, r0, #0
|unk_08046B98|
	CODE32
	RSBS     r0, r0, r2
	RSC      r1, r1, r3
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046BA4|
|sub_08046BA4|
	BX       pc
	LSL      r0, r0, #0
|unk_08046BA8|
	CODE32
	STMDB    sp!, {r4, lr}
	MOVS     r4, r1, ASR #1
	EOR      r4, r4, r3, lsr #1
	BPL      |arm_08046BC0|
	RSBS     r0, r0, #0
	RSC      r1, r1, #0
|arm_08046BC0|
	TST      r3, r3
	BPL      |arm_08046BD0|
	RSBS     r2, r2, #0
	RSC      r3, r3, #0
|arm_08046BD0|
	BL       |arm_080476AC|
	TST      r4, #64, 8
	BEQ      |arm_08046BE4|
	RSBS     r0, r0, #0
	RSC      r1, r1, #0
|arm_08046BE4|
	TST      r4, #128, 8
	BEQ      |arm_08046BF4|
	RSBS     r2, r2, #0
	RSC      r3, r3, #0
|arm_08046BF4|
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_shift_l|
|__16_ll_shift_l|
	BX       pc
	LSL      r0, r0, #0
|unk_08046C00|
	CODE32
	SUBS     r3, r2, #0x20
	BPL      |arm_08046C1C|
	RSB      r3, r2, #0x20
	MOV      r1, r1, LSL r2
	ORR      r1, r1, r0, lsr r3
	MOV      r0, r0, LSL r2
	BX       lr
|arm_08046C1C|
	MOV      r1, r0, LSL r3
	MOV      r0, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |__16_ll_sshift_r|
|__16_ll_sshift_r|
	BX       pc
	LSL      r0, r0, #0
|unk_08046C2C|
	CODE32
	SUBS     r3, r2, #0x20
	BPL      |arm_08046C48|
	RSB      r3, r2, #0x20
	MOV      r0, r0, LSR r2
	ORR      r0, r0, r1, lsl r3
	MOV      r1, r1, ASR r2
	BX       lr
|arm_08046C48|
	MOV      r0, r1, ASR r3
	MOV      r1, r1, ASR #0x1f
	CODE16
	CODE16
	EXPORT |sub_08046C50|
	EXPORT |loc_08046C62|
	EXPORT |loc_08046C70|
	EXPORT |loc_08046C78|
	EXPORT |sub_08046C82|
	EXPORT |sub_08046CAA|
	EXPORT |sub_08046CBA|
	EXPORT |sub_08046CBC|
|sub_08046C50|
|unk_08046C50|
	INCBIN	baserom.gba_0x46c50_0x46c54.extracted
	PUSH     {r4}
	CMP      r2, #4
	BCC      |loc_08046C78|
	ADD      r3, r0, #0
	ORR      r3, r1
	LSL      r3, r3, #0x1e
	BNE      |loc_08046C78|
|loc_08046C62|
	LDMIA    r0!, {r3}
	LDMIA    r1!, {r4}
	CMP      r3, r4
	BNE      |loc_08046C70|
	SUB      r2, #4
	CMP      r2, #4
	BCS      |loc_08046C62|
|loc_08046C70|
	CMP      r3, r4
	BEQ      |loc_08046C78|
	SUB      r0, #4
	SUB      r1, #4
|loc_08046C78|
	CMP      r2, #0
	BNE      |sub_08046C82|
	MOV      r0, #0
	POP      {r4}
	BX       lr
|sub_08046C82|
|unk_08046C82|
		LSL r3, r2, #0x1f
		BPL      |loc_08046C8A|
		ADD r2, #1
		B        |loc_08046C96|
|loc_08046C8A|
		LDRB r3, [r0]
		LDRB r4, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r3, r4
		BNE      |loc_08046CA6|
|loc_08046C96|
		LDRB r3, [r0]
		LDRB r4, [r1]
		ADD r1, #1
		ADD r0, #1
		CMP r3, r4
		BNE      |loc_08046CA6|
		SUB r2, #2
		BNE      |loc_08046C8A|
|loc_08046CA6|
		SUB r0, r3, r4
		DCW     0xE7E9
|sub_08046CAA|
	LSL      r0, r0, #0
	PUSH     {r3, lr}
	MOV      r0, #0xc
	BL       |loc_08047A08|
	ADD      sp, #4
	POP      {r3}
	BX       r3
|sub_08046CBA|
|unk_08046CBA|
	INCBIN	baserom.gba_0x46cba_0x46cbc.extracted
|sub_08046CBC|
	BX       pc
	LSL      r0, r0, #0
|unk_08046CC0|
	CODE32
	MOV      r2, #0
|arm_08046CC4|
	STMDB    sp!, {lr}
	MOV      r3, r2
	MOV      ip, r2
	MOV      lr, r2
	SUBS     r1, r1, #0x20
|arm_08046CD8|
	DCD     0x28A0500C
|arm_08046CDC|
	DCD     0x28A0500C
	SUBHSS   r1, r1, #0x20
	BHS      |arm_08046CD8|
	MOVS     r1, r1, LSL #0x1c
|arm_08046CEC|
	DCD     0x28A0500C
|arm_08046CF0|
	DCD     0x48A0000C
	LDMIA    sp!, {lr}
	MOVS     r1, r1, LSL #2
	STRHS    r2, [r0], #4
	BXEQ     lr
|arm_08046D04|
	DCD     0x44C02001
|arm_08046D08|
	DCD     0x44C02001
	TST      r1, #64, 8
|arm_08046D10|
	DCD     0x14C02001
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046D18|
|sub_08046D18|
	BX       pc
	LSL      r0, r0, #0
|unk_08046D1C|
	CODE32
	CMP      r2, #3
	BLS      |arm_08046E20|
	ANDS     ip, r0, #3
	BEQ      |arm_08046D50|
	LDRB     r3, [r1], #1
	CMP      ip, #2
	ADD      r2, r2, ip
|arm_08046D38|
	DCD     0x94D1C001
	STRB     r3, [r0], #1
|arm_08046D40|
	DCD     0x34D13001
	SUB      r2, r2, #4
|arm_08046D48|
	DCD     0x94C0C001
|arm_08046D4C|
	DCD     0x34C03001
|arm_08046D50|
	ANDS     r3, r1, #3
	BEQ      |arm_08046DD4|
	SUBS     r2, r2, #4
	BLO      |arm_08046E20|
	LDR      ip, [r1, -r3]!
	CMP      r3, #2
	BEQ      |arm_08046D90|
	BHI      |arm_08046DB0|
|arm_08046D70|
	MOV      r3, ip, LSR #8
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #24
	STR      r3, [r0], #4
	BHS      |arm_08046D70|
	ADD      r1, r1, #1
	B        |arm_08046E20|
|arm_08046D90|
	MOV      r3, ip, LSR #0x10
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #16
	STR      r3, [r0], #4
	BHS      |arm_08046D90|
	ADD      r1, r1, #2
	B        |arm_08046E20|
|arm_08046DB0|
	MOV      r3, ip, LSR #0x18
	LDR      ip, [r1, #4]!
	SUBS     r2, r2, #4
	ORR      r3, r3, ip, lsl #8
	STR      r3, [r0], #4
	BHS      |arm_08046DB0|
	ADD      r1, r1, #3
	B        |arm_08046E20|
	CODE16
	CODE16
	EXPORT |sub_08046DD0|
|sub_08046DD0|
	BX       pc
	LSL      r0, r0, #0
|unk_08046DD4|
	CODE32
|arm_08046DD4|
	STMDB    sp!, {r4, lr}
	SUBS     r2, r2, #0x20
	BLO      |arm_08046DF8|
|arm_08046DE0|
	DCD     0x28B15018
|arm_08046DE4|
	DCD     0x28A05018
|arm_08046DE8|
	DCD     0x28B15018
|arm_08046DEC|
	DCD     0x28A05018
	SUBHSS   r2, r2, #0x20
	BHS      |arm_08046DE0|
|arm_08046DF8|
	MOVS     ip, r2, LSL #0x1c
|arm_08046DFC|
	DCD     0x28B15018
|arm_08046E00|
	DCD     0x28A05018
|arm_08046E04|
	DCD     0x48B10018
|arm_08046E08|
	DCD     0x48A00018
	LDMIA    sp!, {r4, lr}
	MOVS     ip, r2, LSL #0x1e
	LDRHS    r3, [r1], #4
	STRHS    r3, [r0], #4
	BXEQ     lr
|arm_08046E20|
	MOVS     r2, r2, LSL #0x1f
|arm_08046E24|
	DCD     0x44D12001
|arm_08046E28|
	DCD     0x24D13001
|arm_08046E2C|
	DCD     0x24D1C001
|arm_08046E30|
	DCD     0x44C02001
|arm_08046E34|
	DCD     0x24C03001
|arm_08046E38|
	DCD     0x24C0C001
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046E40|
|sub_08046E40|
	BX       pc
	LSL      r0, r0, #0
|unk_08046E44|
	CODE32
	AND      r3, r1, #0xff
	MOV      r1, r2
	ORR      r2, r3, r3, lsl #8
	ORR      r2, r2, r2, lsl #16
	B        |arm_08047A48|
	CODE16
	CODE16
	EXPORT |sub_08046E58|
|sub_08046E58|
	BX       pc
	LSL      r0, r0, #0
|unk_08046E5C|
	CODE32
	ANDS     r2, r0, #128, 8
	RSBMI    r0, r0, #0
	EORS     r3, r2, r1, asr #32
	RSBHS    r1, r1, #0
	RSBS     ip, r0, r1, lsr #3
	BLO      |arm_08046EF8|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046EBC|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff000000
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046EEC|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046EBC|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff0000
	RSBS     ip, r0, r1, lsr #8
	MOVHS    r0, r0, LSL #8
	ORRHS    r2, r2, #0xff00
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046EEC|
	RSBS     ip, r0, #0
	BHS      |arm_08047A1C|
|arm_08046EB8|
	MOVHS    r0, r0, LSR #8
|arm_08046EBC|
	RSBS     ip, r0, r1, lsr #7
	SUBHS    r1, r1, r0, lsl #7
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #6
	SUBHS    r1, r1, r0, lsl #6
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #5
	SUBHS    r1, r1, r0, lsl #5
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #4
	SUBHS    r1, r1, r0, lsl #4
	ADC      r2, r2, r2
|arm_08046EEC|
	RSBS     ip, r0, r1, lsr #3
	SUBHS    r1, r1, r0, lsl #3
	ADC      r2, r2, r2
|arm_08046EF8|
	RSBS     ip, r0, r1, lsr #2
	SUBHS    r1, r1, r0, lsl #2
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #1
	SUBHS    r1, r1, r0, lsl #1
	ADC      r2, r2, r2
	RSBS     ip, r0, r1
	SUBHS    r1, r1, r0
	ADCS     r2, r2, r2
	BHS      |arm_08046EB8|
	EORS     r0, r2, r3, asr #31
	ADD      r0, r0, r3, lsr #31
	RSBHS    r1, r1, #0
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08046F30|
|sub_08046F30|
	BX       pc
	LSL      r0, r0, #0
|unk_08046F34|
; cited by 0x08046CF2 (a pc-relative load targets 0x08046F74)
	CODE32
	MOV      r2, #0
	RSBS     ip, r0, r1, lsr #3
	BLO      |arm_08046FC4|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046F88|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff000000
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046FB8|
	RSBS     ip, r0, r1, lsr #8
	BLO      |arm_08046F88|
	MOV      r0, r0, LSL #8
	ORR      r2, r2, #0xff0000
	RSBS     ip, r0, r1, lsr #8
	MOVHS    r0, r0, LSL #8
	ORRHS    r2, r2, #0xff00
	RSBS     ip, r0, r1, lsr #4
	BLO      |arm_08046FB8|
	RSBS     ip, r0, #0
	BHS      |arm_08047A1C|
|arm_08046F84|
	MOVHS    r0, r0, LSR #8
|arm_08046F88|
	RSBS     ip, r0, r1, lsr #7
	SUBHS    r1, r1, r0, lsl #7
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #6
	SUBHS    r1, r1, r0, lsl #6
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #5
	SUBHS    r1, r1, r0, lsl #5
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #4
	SUBHS    r1, r1, r0, lsl #4
	ADC      r2, r2, r2
|arm_08046FB8|
	RSBS     ip, r0, r1, lsr #3
	SUBHS    r1, r1, r0, lsl #3
	ADC      r2, r2, r2
|arm_08046FC4|
	RSBS     ip, r0, r1, lsr #2
	SUBHS    r1, r1, r0, lsl #2
	ADC      r2, r2, r2
	RSBS     ip, r0, r1, lsr #1
	SUBHS    r1, r1, r0, lsl #1
	ADC      r2, r2, r2
	RSBS     ip, r0, r1
	SUBHS    r1, r1, r0
	ADCS     r2, r2, r2
	BHS      |arm_08046F84|
	MOV      r0, r2
	BX       lr
	CODE16
	CODE16
	EXPORT |__vecmap1c__FPvT1iPFPv_v|
	EXPORT |loc_08047004|
	EXPORT |loc_08047010|
	EXPORT |loc_08047028|
	EXPORT |loc_0804703A|
	EXPORT |sub_08047040|
	EXPORT |sub_08047648|
	EXPORT |sub_080476A6|
	EXPORT |sub_080476A8|
|__vecmap1c__FPvT1iPFPv_v|
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r1, #0
	ADD      r4, r0, #0
	ADD      r7, r3, #0
	ADD      r6, r2, #0
	CMP      r0, r1
	BEQ      |loc_08047010|
|loc_08047004|
	ADD      r0, r4, #0
	BL       |sub_08046AAE|
	ADD      r4, r4, r6
	CMP      r4, r5
	BNE      |loc_08047004|
|loc_08047010|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
	LSL      r0, r0, #0
	PUSH     {r6, r7, lr}
	PUSH     {r3, r4, r5}
	ADD      r5, r0, #0
	ADD      r4, r1, #0
	ADD      r7, r2, #0
	ADD      r6, r3, #0
	CMP      r1, r2
	BCS      |loc_0804703A|
|loc_08047028|
	ADD      r1, r4, #0
	ADD      r0, r5, #0
	LDR      r2, [sp, #0x18]
	BL       |loc_08046AA4|
	ADD      r4, r4, r6
	ADD      r5, r5, r6
	CMP      r4, r7
	BCC      |loc_08047028|
|loc_0804703A|
	POP      {r3, r4, r5, r6, r7}
	POP      {r3}
	BX       r3
|sub_08047040|
|unk_08047040|
; cited by 0x08046E0A (a pc-relative load targets 0x0804708C)
	INCBIN	baserom.gba_0x47040_0x47648.extracted
|sub_08047648|
	LSL      r0, r0, #0
	LDRB     r0, [r6, #0x1f]
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
|unk_08047652|
	INCBIN	baserom.gba_0x47652_0x47654.extracted
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	SUB      r7, #0xf9
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	STMIA    r0!, {r0, r3}
	CMP      r5, #0x18
	STRB     r4, [r0, r1]
	MOV      r1, #0xfb
	AND      r1, r1
	LSL      r1, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	LSL      r4, r0, #0xb
	LSL      r7, r6, #1
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r7, [r0, r0]
	ADD      r3, #0x14
|unk_08047684|
	INCBIN	baserom.gba_0x47684_0x47686.extracted
	SUB      r4, #0xa1
	PUSH     {r3, lr}
	BL       |loc_08047FC0|
	LDR      r0, [r0]
	ADD      sp, #4
	POP      {r3}
	BX       r3
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	BL       |loc_08047FC0|
	STR      r4, [r0]
	POP      {r4}
	POP      {r3}
	BX       r3
|sub_080476A6|
|unk_080476A6|
	INCBIN	baserom.gba_0x476a6_0x476a8.extracted
|sub_080476A8|
	BX       pc
	LSL      r0, r0, #0
|unk_080476AC|
; cited by 0x0804746C (a pc-relative load targets 0x08047720)
	CODE32
|arm_080476AC|
	STMDB    sp!, {r4, r5, r6, lr}
	MOV      r4, r1
	MOV      r5, r0
	MOV      r6, #0
	ORRS     ip, r3, r2, lsr #31
	BNE      |arm_0804770C|
	TST      r2, r2
|arm_080476C8|
	DCD     0x0A0000CC
	MOVS     ip, r2, LSR #0xf
	ADDEQ    r6, r6, #0x10
	MOV      ip, r2, LSL r6
	MOVS     lr, ip, LSR #0x17
	MOVEQ    ip, ip, LSL #8
	ADDEQ    r6, r6, #8
	MOVS     lr, ip, LSR #0x1b
	MOVEQ    ip, ip, LSL #4
	ADDEQ    r6, r6, #4
	MOVS     lr, ip, LSR #0x1d
	MOVEQ    ip, ip, LSL #2
	ADDEQ    r6, r6, #2
	MOVS     lr, ip, LSR #0x1e
	MOVEQ    ip, ip, LSL #1
	ADDEQ    r6, r6, #1
|arm_08047708|
	DCD     0xEA000017
|arm_0804770C|
	TST      r3, #128, 8
	BNE      |arm_08047760|
	MOVS     ip, r3, LSR #0xf
	ADDEQ    r6, r6, #0x10
	MOV      ip, r3, LSL r6
	MOVS     lr, ip, LSR #0x17
	MOVEQ    ip, ip, LSL #8
	ADDEQ    r6, r6, #8
	MOVS     lr, ip, LSR #0x1b
	MOVEQ    ip, ip, LSL #4
	ADDEQ    r6, r6, #4
	MOVS     lr, ip, LSR #0x1d
	MOVEQ    ip, ip, LSL #2
	ADDEQ    r6, r6, #2
	MOVS     lr, ip, LSR #0x1e
	MOVEQ    ip, ip, LSL #1
	ADDEQ    r6, r6, #1
	RSB      r3, r6, #0x20
	ORR      ip, ip, r2, lsr r3
	MOV      lr, r2, LSL r6
|arm_0804775C|
	DCD     0xEA00004C
|arm_08047760|
	MOV      ip, r3
	MOV      lr, r2
|arm_08047768|
	DCD     0xEA00009C
	CODE16
	CODE16
	EXPORT |sub_0804776C|
	EXPORT |sub_08047770|
	EXPORT |sub_080479FC|
	EXPORT |loc_08047A00|
	EXPORT |loc_08047A08|
	EXPORT |sub_08047A1C|
	EXPORT |sub_08047A28|
|sub_0804776C|
	ADD      r0, #0
|unk_0804776E|
	INCBIN	baserom.gba_0x4776e_0x47770.extracted
|sub_08047770|
|unk_08047770|
; cited by 0x080477B8 (a pc-relative load targets 0x080477CC)
	INCBIN	baserom.gba_0x47770_0x479fc.extracted
|sub_080479FC|
|unk_080479FC|
	INCBIN	baserom.gba_0x479fc_0x47a00.extracted
|loc_08047A00|
	EOR      r0, r6
|unk_08047A02|
	INCBIN	baserom.gba_0x47a02_0x47a08.extracted
|loc_08047A08|
|unk_08047A08|
		PUSH {r3, lr}
	MOV      r1, #0
	BL       |sub_08047FD4|
	ADD      sp, #4
	POP      {r3}
	MOV      r0, #0
	BX       r3
	BX       pc
	LSL      r0, r0, #0
|sub_08047A1C|
|unk_08047A1C|
	CODE32
|arm_08047A1C|
	MOV      r0, #2
	MOV      r1, #2
	B        |arm_08047FD8|
	CODE16
|sub_08047A28|
	BX       pc
	LSL      r0, r0, #0
|unk_08047A2C|
	CODE32
|arm_08047A2C|
	STMDB    sp!, {r4, lr}
	BL       |arm_08047FB4|
	ADD      r0, r0, #4
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08047A40|
|sub_08047A40|
	BX       pc
	LSL      r0, r0, #0
|unk_08047A44|
; cited by 0x08047A88 (a pc-relative load targets 0x08047C8C)
	CODE32
	MOV      r2, #0
|arm_08047A48|
	CMP      r1, #4
	BLO      |arm_08047A74|
	ANDS     ip, r0, #3
	BEQ      |arm_08046CC4|
	RSB      ip, ip, #4
	CMP      ip, #2
	STRB     r2, [r0], #1
|arm_08047A64|
	DCD     0xA4C02001
|arm_08047A68|
	DCD     0xC4C02001
	SUB      r1, r1, ip
	B        |arm_08046CC4|
|arm_08047A74|
	MOVS     ip, r1, LSL #0x1f
|arm_08047A78|
	DCD     0x24C02001
|arm_08047A7C|
	DCD     0x24C02001
|arm_08047A80|
	DCD     0x44C02001
	BX       lr
|arm_08047A88|
	DCD     0xE92D4D80
	STMDB    sp!, {r2, r3, r4, r5, r6}
	BIC      r6, r1, #128, 8
	ADDS     ip, r6, #192, 8
	SUBGES   ip, ip, #0x4100000
	MOV      r5, r0
	MOV      r4, r1
	MOV      fp, r1
	BLT      |arm_08047AF8|
	ADDS     ip, r6, #144, 8
	SUBGES   ip, ip, #0xff00000
	BGT      |arm_08047AC4|
	BNE      |arm_08047AE4|
	CMP      r5, #0
	BEQ      |arm_08047AE4|
|arm_08047AC4|
	MOV      r3, r4
	MOV      r2, r5
	MOV      r1, r4
	MOV      r0, r5
	BL       |arm_080534A8|
|arm_08047AD8|
	LDMIA    sp!, {r2, r3, r4, r5, r6}
	LDMIA    sp!, {r7, r8, sl, fp, lr}
	BX       lr
|arm_08047AE4|
	ADD      r1, pc, #0x268
	CMP      fp, #0
	ADDLE    r1, pc, #0x268
	LDMIA    r1, {r0, r1}
	B        |arm_08047AD8|
|arm_08047AF8|
	ADDS     ip, r6, #196, 8
	SUBGES   ip, ip, #0x3dc0000
	ADD      r7, pc, #0x25c
	BGE      |arm_08047B44|
	ADDS     ip, r6, #208, 8
	SUBGES   ip, ip, #0xe200000
	BGE      |arm_08047B3C|
	ADD      r0, pc, #148, 30
	LDMIA    r0, {r2, r3}
	MOV      r0, r5
	MOV      r1, r4
	BL       |arm_080534A8|
	LDMIA    r7, {r2, r3}
	BL       |arm_08054058|
	MOVHI    r0, r5
	MOVHI    r1, r4
	BHI      |arm_08047AD8|
|arm_08047B3C|
	MVN      r6, #0
	B        |arm_08047C48|
|arm_08047B44|
	BIC      r1, r4, #128, 8
	MOV      r4, r5
	ADDS     ip, r6, #0xc1000000
	SUBGES   ip, ip, #0xf30000
	MOV      r5, r1
	BGE      |arm_08047BD8|
	ADDS     ip, r6, #0xc1000000
	SUBGES   ip, ip, #0xe60000
	BGE      |arm_08047BAC|
	ADD      r8, pc, #0x204
	LDMIA    r8, {r2, r3}
	MOV      r6, #0
	MOV      r1, r5
	MOV      r0, r4
	BL       |arm_08054160|
	LDMIA    r7, {r2, r3}
	BL       |arm_080536E0|
	MOV      r7, r0
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r8, {r2, r3}
	BL       |arm_080534A8|
	MOV      r3, sl
	MOV      r2, r7
	B        |arm_08047C3C|
|arm_08047BAC|
	MOV      r6, #1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r7, {r2, r3}
	BL       |arm_080536E0|
	MOV      r8, r0
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r7, {r2, r3}
	B        |arm_08047C30|
|arm_08047BD8|
	ADDS     ip, r6, #192, 8
	SUBGES   ip, ip, #224, 22
	ADDGE    r0, pc, #0x194
|arm_08047BE4|
	DCD     0xA890000C
	MOVGE    r0, r4
	MOVGE    r6, #3
	MOVGE    r1, r5
	BGE      |arm_08047C3C|
	ADD      r0, pc, #0x184
	LDMIA    r0, {r2, r3}
	MOV      r0, r4
	MOV      r6, #2
	MOV      r1, r5
	BL       |arm_080536E0|
	MOV      r8, r0
	ADD      r0, pc, #0x168
	LDMIA    r0, {r2, r3}
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	BL       |arm_08054160|
	LDMIA    r7, {r2, r3}
|arm_08047C30|
	BL       |arm_080534A8|
	MOV      r3, sl
	MOV      r2, r8
|arm_08047C3C|
	BL       |arm_08053A20|
	MOV      r5, r0
	MOV      r4, r1
|arm_08047C48|
	MOV      r3, r4
	MOV      r2, r5
	MOV      r1, r4
	MOV      r0, r5
	BL       |arm_08054160|
	MOV      sl, r0
	STR      r1, [sp]
	MOV      r3, r1
	MOV      r2, r0
	BL       |arm_08054160|
	MOV      r7, r0
	MOV      r2, r0
	LDR      r0, [pc, #0x10c]
	MOV      r8, r1
	MOV      r3, r1
	MOV      r1, #6
	ADD      r0, pc, r0
	BL       |arm_08047D9C|
	MOV      r2, sl
	LDR      r3, [sp]
	BL       |arm_08054160|
	MOV      sl, r0
	LDR      r0, [pc, #0xe8]
	STR      r1, [sp, #4]
	MOV      r1, #5
	MOV      r3, r8
	MOV      r2, r7
	ADD      r0, pc, r0
	BL       |arm_08047D9C|
	MOV      r3, r8
	MOV      r2, r7
	BL       |arm_08054160|
	MOV      r3, r1
	MOV      r2, r0
	MOV      r0, sl
	LDR      r1, [sp, #4]
	CMP      r6, #0
	BGE      |arm_08047D00|
	BL       |arm_080534A8|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08054160|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08053698|
	B        |arm_08047AD8|
|arm_08047D00|
	BL       |arm_080534A8|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08054160|
	LDR      r2, [pc, #0x7c]
	ADD      r2, pc, r2
	ADD      r2, r2, r6, lsl #3
	LDMIA    r2, {r2, r3}
	BL       |arm_080536E0|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_080536E0|
	LDR      r2, [pc, #0x60]
	ADD      r2, pc, r2
	ADD      r2, r2, r6, lsl #3
	LDMIA    r2, {r2, r3}
	BL       |arm_08053698|
	CMP      fp, #0
	EORLT    r1, r1, #128, 8
	BLT      |arm_08047AD8|
	B        |arm_08047AD8|
|arm_08047D54|
	DCD     0x54442D18
|arm_08047D58|
	DCD     0x3FF921FB
|arm_08047D5C|
	DCD     0x54442D18
|arm_08047D60|
	DCD     0xBFF921FB
	ANDEQ    r0, r0, r0
|arm_08047D68|
	DCD     0x3FF00000
|arm_08047D6C|
	DCD     0x8800759C
|arm_08047D70|
	DCD     0x7E37E43C
	ANDEQ    r0, r0, r0
	ANDMI    r0, r0, r0
	ANDEQ    r0, r0, r0
|arm_08047D80|
	DCD     0xBFF00000
	ANDEQ    r0, r0, r0
|arm_08047D88|
	DCD     0x3FF80000
	RSBEQS   pc, r6, r0, ror fp
	RSBEQS   pc, r6, ip, lsl fp
|arm_08047D94|
	DCD     0x0076FA9C
|arm_08047D98|
	DCD     0x0076FA5C
|arm_08047D9C|
	DCD     0xE92D40F0
|arm_08047DA0|
	DCD     0xE2414001
|arm_08047DA4|
	DCD     0xE0801184
|arm_08047DA8|
	DCD     0xE52D3004
|arm_08047DAC|
	DCD     0xE1A05000
|arm_08047DB0|
	DCD     0xE8910003
|arm_08047DB4|
	DCD     0xE3540008
|arm_08047DB8|
	DCD     0xE1A07003
|arm_08047DBC|
	DCD     0xE1A06002
|arm_08047DC0|
	DCD     0x908FF104
|arm_08047DC4|
	DCD     0xEA00000F
|arm_08047DC8|
	DCD     0xEA00000E
|arm_08047DCC|
	DCD     0xEA000040
|arm_08047DD0|
	DCD     0xEA000038
|arm_08047DD4|
	DCD     0xEA000030
|arm_08047DD8|
	DCD     0xEA000028
|arm_08047DDC|
	DCD     0xEA000020
|arm_08047DE0|
	DCD     0xEA000018
|arm_08047DE4|
	DCD     0xEA000010
|arm_08047DE8|
	DCD     0xEA000008
|arm_08047DEC|
	DCD     0xE1A03007
|arm_08047DF0|
	DCD     0xE1A02006
|arm_08047DF4|
	DCD     0xEB0030D9
|arm_08047DF8|
	DCD     0xE2444001
|arm_08047DFC|
	DCD     0xE0852184
|arm_08047E00|
	DCD     0xE892000C
|arm_08047E04|
	DCD     0xEB002DA7
|arm_08047E08|
	DCD     0xE3540008
|arm_08047E0C|
	DCD     0xCAFFFFF6
|arm_08047E10|
	DCD     0xE1A03007
|arm_08047E14|
	DCD     0xE1A02006
|arm_08047E18|
	DCD     0xEB0030D0
|arm_08047E1C|
	DCD     0xE2444001
|arm_08047E20|
	DCD     0xE0852184
|arm_08047E24|
	DCD     0xE892000C
|arm_08047E28|
	DCD     0xEB002D9E
|arm_08047E2C|
	DCD     0xE1A03007
|arm_08047E30|
	DCD     0xE1A02006
|arm_08047E34|
	DCD     0xEB0030C9
|arm_08047E38|
	DCD     0xE2444001
|arm_08047E3C|
	DCD     0xE0852184
|arm_08047E40|
	DCD     0xE892000C
|arm_08047E44|
	DCD     0xEB002D97
|arm_08047E48|
	DCD     0xE1A03007
|arm_08047E4C|
	DCD     0xE1A02006
|arm_08047E50|
	DCD     0xEB0030C2
|arm_08047E54|
	DCD     0xE2444001
|arm_08047E58|
	DCD     0xE0852184
|arm_08047E5C|
	DCD     0xE892000C
|arm_08047E60|
	DCD     0xEB002D90
|arm_08047E64|
	DCD     0xE1A03007
|arm_08047E68|
	DCD     0xE1A02006
|arm_08047E6C|
	DCD     0xEB0030BB
|arm_08047E70|
	DCD     0xE2444001
|arm_08047E74|
	DCD     0xE0852184
|arm_08047E78|
	DCD     0xE892000C
|arm_08047E7C|
	DCD     0xEB002D89
|arm_08047E80|
	DCD     0xE1A03007
|arm_08047E84|
	DCD     0xE1A02006
|arm_08047E88|
	DCD     0xEB0030B4
|arm_08047E8C|
	DCD     0xE2444001
|arm_08047E90|
	DCD     0xE0852184
|arm_08047E94|
	DCD     0xE892000C
|arm_08047E98|
	DCD     0xEB002D82
|arm_08047E9C|
	DCD     0xE1A03007
|arm_08047EA0|
	DCD     0xE1A02006
|arm_08047EA4|
	DCD     0xEB0030AD
|arm_08047EA8|
	DCD     0xE2444001
|arm_08047EAC|
	DCD     0xE0852184
|arm_08047EB0|
	DCD     0xE892000C
|arm_08047EB4|
	DCD     0xEB002D7B
|arm_08047EB8|
	DCD     0xE1A03007
|arm_08047EBC|
	DCD     0xE1A02006
|arm_08047EC0|
	DCD     0xEB0030A6
|arm_08047EC4|
	DCD     0xE2444001
|arm_08047EC8|
	DCD     0xE0852184
|arm_08047ECC|
	DCD     0xE892000C
|arm_08047ED0|
	DCD     0xEB002D74
|arm_08047ED4|
	DCD     0xE1A03007
|arm_08047ED8|
	DCD     0xE1A02006
|arm_08047EDC|
	DCD     0xEB00309F
|arm_08047EE0|
	DCD     0xE2442001
|arm_08047EE4|
	DCD     0xE0852182
|arm_08047EE8|
	DCD     0xE892000C
|arm_08047EEC|
	DCD     0xE28DD004
|arm_08047EF0|
	DCD     0xE8BD40F0
|arm_08047EF4|
	DCD     0xEA002D6B
|arm_08047EF8|
	DCD     0xE92D4038
|arm_08047EFC|
	DCD     0xE2603000
|arm_08047F00|
	DCD     0xE1803003
|arm_08047F04|
	DCD     0xE3C12480
|arm_08047F08|
	DCD     0xE1822FA3
|arm_08047F0C|
	DCD     0xE26226FF
|arm_08047F10|
	DCD     0xE2822470
|arm_08047F14|
	DCD     0xE1B02FA2
|arm_08047F18|
	DCD     0xE1A05001
|arm_08047F1C|
	DCD     0xE1A04000
|arm_08047F20|
	DCD     0x1A000009
|arm_08047F24|
	DCD     0xE28F2030
|arm_08047F28|
	DCD     0xE892000C
|arm_08047F2C|
	DCD     0xEB00306A
|arm_08047F30|
	DCD     0x2A000005
|arm_08047F34|
	DCD     0xE3A00001
|arm_08047F38|
	DCD     0xEB0004A3
|arm_08047F3C|
	DCD     0xE28F1020
|arm_08047F40|
	DCD     0xE8910003
|arm_08047F44|
	DCD     0xE8BD4038
|arm_08047F48|
	DCD     0xE12FFF1E
|arm_08047F4C|
	DCD     0xE1A01005
|arm_08047F50|
	DCD     0xE1A00004
|arm_08047F54|
	DCD     0xEB003131
|arm_08047F58|
	DCD     0xEAFFFFF9
	CODE16
	CODE16
	EXPORT |sub_08047F5C|
	EXPORT |loc_08047F84|
	EXPORT |sub_08047F94|
	EXPORT |__16__user_libspace|
|sub_08047F5C|
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LSL      r1, r0, #0
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDRB     r0, [r7, #0x1f]
	PUSH     {r3, r4, r5, lr}
	PUSH     {r0, r1, r2}
	SUB      sp, #0xc
	LDR      r4, [sp, #0x28]
	ADD      r5, sp, #4
	ADD      r1, r5, #0
	MOV      r0, #0
	ADD      r3, sp, #0x14
	ADD      r2, sp, #0xc
	STR      r4, [sp]
	BL       |loc_08047F84|
|loc_08047F84|
	CMP      r0, #0
	BEQ      |sub_08047F94|
	ADD      r1, sp, #4
	LDMIA    r1!, {r0, r1}
	ADD      sp, #0x1c
	POP      {r4, r5}
	POP      {r3}
	BX       r3
|sub_08047F94|
|unk_08047F94|
		MOV r0, #0x1f
		LSL r0, r0, #0x1a
		AND r4, r0
		ADD r1, r4, #0
		MOV r0, #2
		BL       |sub_08047FD4|
		MOV r0, #0
		MOV r1, #0
		STMIA r5!, {r0, r1}
		ADD r1, sp, #4
		LDMIA r1!, {r0, r1}
		DCW     0xE7EE
	INCBIN  baserom.gba_0x47fae_0x47fb0.extracted
|__16__user_libspace|
	BX       pc
	LSL      r0, r0, #0
|unk_08047FB4|
	CODE32
|arm_08047FB4|
	LDR      r0, [pc]
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08047FBC|
	EXPORT |loc_08047FC0|
|sub_08047FBC|
	STRH     r0, [r3, r2]
	LSL      r0, r0, #0xc
|loc_08047FC0|
	BX       pc
	LSL      r0, r0, #0
|unk_08047FC4|
	CODE32
	STMDB    sp!, {r4, lr}
	BL       |arm_08047FB4|
	LDMIA    sp!, {r4, lr}
	BX       lr
	CODE16
	CODE16
	EXPORT |sub_08047FD4|
|sub_08047FD4|
	BX       pc
	LSL      r0, r0, #0
|unk_08047FD8|
	CODE32
|arm_08047FD8|
	STMDB    sp!, {r4, lr}
|arm_08047FDC|
	DCD     0xEB00047D
	CMP      r0, #0
|arm_08047FE4|
	DCD     0x08BD4010
	BXEQ     lr
	LDMIA    sp!, {r4, lr}
	B        |arm_0804803C|
	CODE16
	CODE16
	EXPORT |__raise|
	EXPORT |loc_08048006|
	EXPORT |sub_0804801A|
	EXPORT |__16_sys_exit|
|__raise|
	PUSH     {r4, r5, r6, lr}
	LDR      r6, [pc, #0x38]
	ADD      r5, r1, #0
	ADD      r1, r0, #0
	ADD      r4, r0, #0
	ADD      r6, pc
	ADD      r0, r6, #0
	BL       |loc_08048006|
|loc_08048006|
	ADD      r2, r0, #0
	CMP      r0, r6
	BNE      |sub_0804801A|
	ADD      r1, r5, #0
	ADD      r0, r4, #0
	BL       |__default_signal_handler|
	POP      {r4, r5, r6}
	POP      {r3}
	BX       r3
|sub_0804801A|
|unk_0804801A|
; cited by 0x08047FF6 (a pc-relative load targets 0x08048030)
		LDR r0, [pc, #0x18]
		ADD r0, pc
		CMP r2, r0
		BEQ      |loc_0804802A|
		ADD r1, r5, #0
		ADD r0, r4, #0
		BL       |loc_08046AA4|
|loc_0804802A|
		MOV r0, #0
		DCW     0xE7F2
	INCBIN  baserom.gba_0x4802e_0x48034.extracted
		DCD     0xF7FB7FDD
|__16_sys_exit|
	BX       pc
	LSL      r0, r0, #0
|unk_0804803C|
; cited by 0x08048040 (a pc-relative load targets 0x08048050)
	CODE32
|arm_0804803C|
	MOV      r0, #0x18
	LDR      r1, [pc, #8]
|arm_08048044|
	DCD     0xEF123456
	BX       lr
|arm_0804804C|
	DCD     0x00000121
	ANDEQ    r0, r2, r6, lsr #32
	CODE16
	CODE16
	EXPORT |__default_signal_handler|
	EXPORT |sub_08048076|
	EXPORT |loc_08048098|
	EXPORT |sub_080480AC|
	EXPORT |loc_080480AE|
	EXPORT |loc_080480BA|
	EXPORT |loc_080480C8|
	EXPORT |loc_080480CE|
	EXPORT |loc_080480DC|
	EXPORT |sub_080480EA|
	EXPORT |loc_080480EC|
	EXPORT |sub_080480F2|
	EXPORT |loc_080480F4|
	EXPORT |loc_0804815C|
	EXPORT |loc_08048174|
	EXPORT |sub_08048186|
	EXPORT |sub_0804818A|
	EXPORT |sub_08048194|
	EXPORT |sub_08048196|
	EXPORT |sub_080481E4|
	EXPORT |sub_080481E6|
	EXPORT |sub_08048228|
	EXPORT |sub_0804822A|
	EXPORT |sub_08048238|
	EXPORT |sub_0804823A|
	EXPORT |loc_08048248|
	EXPORT |loc_0804824E|
	EXPORT |sub_080482A0|
	EXPORT |sub_080482A2|
	EXPORT |sub_080482AC|
	EXPORT |sub_080482AE|
	EXPORT |sub_080482BC|
	EXPORT |sub_080482BE|
	EXPORT |loc_08048346|
	EXPORT |loc_0804835E|
	EXPORT |loc_080483C4|
	EXPORT |loc_080483F6|
	EXPORT |sub_08048400|
	EXPORT |sub_08048402|
	EXPORT |sub_0804840C|
	EXPORT |sub_0804840E|
	EXPORT |sub_0804841C|
	EXPORT |sub_0804841E|
	EXPORT |loc_08048424|
	EXPORT |loc_08048464|
	EXPORT |loc_0804848C|
	EXPORT |sub_08048490|
	EXPORT |sub_08048492|
	EXPORT |loc_080484C0|
	EXPORT |loc_080484DA|
	EXPORT |loc_080484E0|
	EXPORT |sub_080484E4|
	EXPORT |sub_080484E6|
	EXPORT |sub_080484F8|
	EXPORT |sub_080484FA|
	EXPORT |sub_08048508|
	EXPORT |sub_0804850A|
	EXPORT |sub_08048518|
	EXPORT |sub_0804851A|
	EXPORT |sub_0804854C|
	EXPORT |sub_0804854E|
	EXPORT |sub_0804855C|
	EXPORT |sub_0804855E|
	EXPORT |loc_08048564|
	EXPORT |sub_0804856C|
	EXPORT |sub_0804856E|
	EXPORT |sub_0804859C|
	EXPORT |sub_0804859E|
	EXPORT |sub_080485B0|
	EXPORT |sub_080485B2|
	EXPORT |sub_080485DC|
	EXPORT |sub_080485DE|
	EXPORT |loc_0804860C|
	EXPORT |loc_08048620|
	EXPORT |sub_0804862A|
	EXPORT |sub_0804862E|
	EXPORT |sub_08048640|
	EXPORT |sub_08048642|
	EXPORT |sub_08048650|
	EXPORT |sub_08048652|
	EXPORT |sub_08048660|
	EXPORT |sub_08048662|
	EXPORT |sub_0804868C|
	EXPORT |sub_0804868E|
	EXPORT |loc_080486A4|
	EXPORT |loc_080486AC|
	EXPORT |loc_080486B8|
	EXPORT |loc_080486DE|
	EXPORT |loc_080486E6|
	EXPORT |sub_08048716|
	EXPORT |sub_0804871A|
	EXPORT |sub_08048732|
	EXPORT |sub_08048736|
	EXPORT |sub_0804879C|
	EXPORT |sub_0804879E|
	EXPORT |sub_080487C8|
	EXPORT |sub_080487CA|
	EXPORT |loc_080487D4|
	EXPORT |sub_080487F4|
	EXPORT |sub_080487F6|
	EXPORT |sub_08048804|
	EXPORT |sub_08048806|
	EXPORT |loc_08048834|
	EXPORT |loc_0804883A|
	EXPORT |sub_08048844|
	EXPORT |sub_08048846|
	EXPORT |loc_08048860|
	EXPORT |loc_08048868|
	EXPORT |loc_08048884|
	EXPORT |sub_0804888C|
	EXPORT |sub_0804888E|
	EXPORT |sub_0804889C|
	EXPORT |sub_0804889E|
	EXPORT |sub_080488AC|
	EXPORT |sub_080488AE|
	EXPORT |loc_080488B8|
	EXPORT |sub_080488F4|
	EXPORT |sub_080488F6|
	EXPORT |loc_08048900|
	EXPORT |sub_08048904|
	EXPORT |sub_08048906|
	EXPORT |loc_08048928|
	EXPORT |loc_08048930|
	EXPORT |loc_0804893A|
	EXPORT |loc_08048942|
	EXPORT |sub_08048950|
	EXPORT |sub_08048952|
	EXPORT |sub_08048960|
	EXPORT |sub_08048962|
	EXPORT |sub_08048974|
	EXPORT |sub_08048976|
	EXPORT |sub_0804898A|
	EXPORT |sub_0804898E|
	EXPORT |sub_080489A0|
	EXPORT |sub_080489A2|
	EXPORT |loc_080489B4|
	EXPORT |loc_080489BA|
	EXPORT |sub_08048A02|
	EXPORT |sub_08048A06|
	EXPORT |sub_08048A18|
	EXPORT |sub_08048A1A|
	EXPORT |sub_08048A28|
	EXPORT |sub_08048A2A|
	EXPORT |loc_08048A2C|
	EXPORT |sub_08048A38|
	EXPORT |sub_08048A3A|
	EXPORT |sub_08048A54|
	EXPORT |sub_08048A56|
	EXPORT |loc_08048A58|
	EXPORT |loc_08048A68|
	EXPORT |loc_08048A72|
	EXPORT |loc_08048A7A|
	EXPORT |loc_08048A84|
	EXPORT |sub_08048A88|
	EXPORT |sub_08048A8A|
	EXPORT |loc_08048A94|
	EXPORT |sub_08048A98|
	EXPORT |sub_08048A9A|
	EXPORT |loc_08048AA4|
	EXPORT |loc_08048AAA|
	EXPORT |sub_08048AB4|
	EXPORT |sub_08048AB6|
	EXPORT |loc_08048AC0|
	EXPORT |sub_08048AC4|
	EXPORT |sub_08048AC6|
	EXPORT |loc_08048AD4|
	EXPORT |loc_08048ADA|
	EXPORT |sub_08048AE4|
	EXPORT |sub_08048AE6|
	EXPORT |sub_08048AF4|
	EXPORT |sub_08048AF6|
	EXPORT |sub_08048B24|
	EXPORT |sub_08048B26|
	EXPORT |loc_08048B30|
	EXPORT |sub_08048B34|
	EXPORT |sub_08048B36|
	EXPORT |sub_08048B44|
	EXPORT |sub_08048B46|
	EXPORT |sub_08048B76|
	EXPORT |sub_08048B7A|
	EXPORT |loc_08048B80|
	EXPORT |loc_08048B98|
	EXPORT |loc_08048BA8|
	EXPORT |loc_08048BAE|
	EXPORT |sub_08048BBE|
	EXPORT |sub_08048BC2|
	EXPORT |sub_08048BD4|
	EXPORT |sub_08048BD6|
	EXPORT |sub_08048BE4|
	EXPORT |sub_08048BE6|
	EXPORT |loc_08048BEC|
	EXPORT |sub_08048BF4|
	EXPORT |sub_08048BF6|
	EXPORT |loc_08048C30|
	EXPORT |sub_08048C42|
	EXPORT |sub_08048C46|
	EXPORT |sub_08048C58|
	EXPORT |sub_08048C5A|
	EXPORT |loc_08048C70|
	EXPORT |sub_08048C84|
	EXPORT |sub_08048C86|
	EXPORT |loc_08048C88|
	EXPORT |loc_08048CA4|
	EXPORT |loc_08048CBA|
	EXPORT |loc_08048CC6|
	EXPORT |loc_08048CD6|
	EXPORT |loc_08048CE2|
	EXPORT |loc_08048CEC|
	EXPORT |loc_08048CF2|
	EXPORT |loc_08048CFC|
	EXPORT |loc_08048D02|
	EXPORT |sub_08048D0C|
	EXPORT |sub_08048D0E|
	EXPORT |sub_08048D1C|
	EXPORT |sub_08048D1E|
	EXPORT |sub_08048D2C|
	EXPORT |sub_08048D2E|
	EXPORT |sub_08048D40|
	EXPORT |sub_08048D42|
	EXPORT |sub_08048D50|
	EXPORT |sub_08048D52|
	EXPORT |sub_08048D60|
	EXPORT |sub_08048D62|
	EXPORT |sub_08048D70|
	EXPORT |sub_08048D72|
	EXPORT |loc_08048D80|
	EXPORT |loc_08048D86|
	EXPORT |sub_08048D90|
	EXPORT |sub_08048D92|
	EXPORT |loc_08048DA0|
	EXPORT |loc_08048DA6|
	EXPORT |sub_08048DB0|
	EXPORT |sub_08048DB2|
	EXPORT |loc_08048DB4|
	EXPORT |sub_08048DC0|
	EXPORT |sub_08048DC2|
	EXPORT |sub_08048DD0|
	EXPORT |sub_08048DD2|
	EXPORT |loc_08048DD8|
	EXPORT |sub_08048DE6|
	EXPORT |sub_08048DEA|
	EXPORT |sub_08048DFC|
	EXPORT |sub_08048DFE|
	EXPORT |sub_08048E44|
	EXPORT |sub_08048E46|
	EXPORT |sub_08048E54|
	EXPORT |sub_08048E56|
	EXPORT |loc_08048E6A|
	EXPORT |loc_08048E76|
	EXPORT |sub_08048E84|
	EXPORT |sub_08048E86|
	EXPORT |loc_08048EA2|
	EXPORT |sub_08048EA4|
	EXPORT |sub_08048EA6|
	EXPORT |sub_08048EB4|
	EXPORT |sub_08048EB6|
	EXPORT |sub_08048ECA|
	EXPORT |loc_08048F54|
	EXPORT |loc_08049010|
|__default_signal_handler|
	PUSH     {r3, r4, r5, lr}
	SUB      r2, r0, #1
	CMP      r2, #0xd
	ADD      r4, pc, #0x90
	BCS      |sub_080480AC|
	MOV      r2, #0x17
	LDR      r3, [pc, #0x8c]
	MUL      r2, r0
	ADD      r3, pc
	ADD      r5, r2, r3
	SUB      r5, #0x17
	CMP      r0, #2
	BNE      |loc_08048098|
	LSL      r0, r1, #5
	BPL      |sub_08048076|
	ADD      r4, pc, #0x80
	B        |loc_080480AE|
|sub_08048076|
|unk_08048076|
		LDR r0, [pc, #0x90]
		AND r0, r1
		BEQ      |loc_08048080|
		DCW     0xA423
		B        |loc_080480AE|
|loc_08048080|
		LSL r0, r1, #3
		BPL      |loc_08048088|
		DCW     0xA425
		B        |loc_080480AE|
|loc_08048088|
		LSL r0, r1, #2
		BPL      |loc_08048090|
		DCW     0xA426
		B        |loc_080480AE|
|loc_08048090|
		LSL r0, r1, #1
		BPL      |loc_080480AE|
		DCW     0xA427
		B        |loc_080480AE|
|loc_08048098|
|unk_08048098|
		CMP r0, #8
		BNE      |loc_080480A0|
		ADD r4, r1, #0
		B        |loc_080480AE|
|loc_080480A0|
		CMP r0, #9
		BNE      |loc_080480AE|
		CMP r1, #1
		BNE      |loc_080480AE|
		DCW     0xA526
		B        |loc_080480AE|
|sub_080480AC|
	ADR      r5, |loc_0804815C|
|loc_080480AE|
	MOV      r0, #0xa
	BL       |loc_08048174|
	LDRB     r0, [r5]
	CMP      r0, #0
	BEQ      |loc_080480C8|
|loc_080480BA|
	LDRB     r0, [r5]
	ADD      r5, #1
	BL       |loc_08048174|
	LDRB     r0, [r5]
	CMP      r0, #0
	BNE      |loc_080480BA|
|loc_080480C8|
	LDRB     r0, [r4]
	CMP      r0, #0
	BEQ      |loc_080480DC|
|loc_080480CE|
	LDRB     r0, [r4]
	ADD      r4, #1
	BL       |loc_08048174|
	LDRB     r0, [r4]
	CMP      r0, #0
	BNE      |loc_080480CE|
|loc_080480DC|
	MOV      r0, #0xa
	BL       |loc_08048174|
	POP      {r3, r4, r5}
	POP      {r3}
	MOV      r0, #1
	BX       r3
|sub_080480EA|
|unk_080480EA|
	INCBIN	baserom.gba_0x480ea_0x480ec.extracted
|loc_080480EC|
	DCW      0x0000
	DCW      0x0000,0xf7d0
|sub_080480F2|
	LSL      r6, r6, #1
|loc_080480F4|
	LDR      r1, [r1, #0x64]
	STR      r6, [r6, #0x14]
	LDR      r4, [r5, #0x14]
	MOV      r0, #0x64
	STRB     r7, [r1, #1]
	STRB     r5, [r4, #9]
	STRB     r1, [r4, #0x11]
	LDR      r1, [r5, #0x74]
	LSL      r6, r5, #1
	LSL      r0, r0, #0
	LSL      r2, r0, #0
	LSR      r0, r0, #0x20
	LDR      r4, [r0, #0x14]
	LDR      r6, [r6, #0x14]
	STR      r4, [r4, #0x54]
	TST      r0, r4
	MOV      r0, #0x79
	STR      r2, [r3, #0x54]
	LDR      r2, [r6, #0x74]
	LSL      r0, r0, #0
	STRB     r7, [r1, #0x19]
	STRB     r5, [r4, #9]
	LDR      r6, [r4, #0x44]
	STRB     r7, [r5, #0x1d]
	LSL      r0, r0, #0
	LSL      r0, r0, #0
	LDR      r5, [r2, #0x64]
	STR      r4, [r4, #0x54]
	STR      r2, [r6, #0x64]
	LDR      r4, [r5, #0x74]
	LSL      r7, r6, #1
	LSL      r0, r0, #0
	LDR      r1, [r1, #0x64]
	LDRB     r5, [r4, #1]
	STR      r1, [r4, #0x34]
	MOV      r0, #0x74
	STR      r2, [r2, #0x54]
	STRB     r3, [r6, #0x15]
	STRB     r4, [r5, #0x11]
	LSL      r0, r0, #0
	MOV      r0, #0x3a
	STR      r0, [r1, #0x54]
	STRB     r1, [r4, #1]
	LDR      r0, [r4, #0x50]
	LDR      r5, [r4, #0x54]
	STRB     r7, [r5, #9]
	MOV      r0, #0x79
	LDR      r3, [r4, #0x74]
	STRB     r2, [r6, #9]
	STRB     r5, [r6, #1]
	STR      r4, [r6, #0x54]
	LSL      r4, r4, #1
|loc_0804815C|
	LDR      r5, [r2, #0x64]
	LDR      r3, [r5, #0x64]
	STRB     r7, [r5, #0x1d]
	MOV      r0, #0x6e
	LDR      r3, [r6, #0x14]
	LDR      r7, [r4, #0x64]
	LDR      r1, [r4, #0x44]
	LSL      r0, r0, #0
	BX       pc
	LSL      r0, r0, #0
|unk_08048170|
	CODE32
	BX       lr
	CODE16
|loc_08048174|
	PUSH     {r3, lr}
	ADD      r3, sp, #0
	STRB     r0, [r3]
	MOV      r0, #3
	MOV      r1, sp
	SWI      0xab
	ADD      sp, #4
	POP      {r3}
	BX       r3
|sub_08048186|
|unk_08048186|
	INCBIN	baserom.gba_0x48186_0x4818a.extracted
|sub_0804818A|
	LSL      r0, r0, #0
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_08048194|
|unk_08048194|
	INCBIN	baserom.gba_0x48194_0x48196.extracted
|sub_08048196|
	LSL      r0, r0, #0xc
	PUSH     {r3, lr}
	LDR      r0, [pc, #8]
	BL       |inc_0x0158_0x143f2| + 0x46e0
	POP      {r3, pc}
	LSL      r0, r0, #0
	ASR      r0, r5, #1
	LSL      r0, r0, #0xc
	LDR      r2, [pc, #0x28]
	LDR      r0, [pc, #0x2c]
	MOV      r1, #0x40
	STR      r0, [r2]
	STRB     r1, [r2, #4]
	ADD      r2, #8
	STR      r0, [r2]
	MOV      r1, #0x80
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x18]
	ADD      r2, #8
	ADD      r1, #0x10
	STR      r0, [r1]
	MOV      r1, #0x20
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0xc]
	ADD      r1, #0x18
	STR      r0, [r1]
	MOV      r0, #0x10
	STRB     r0, [r1, #4]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, r3, r4
	LSL      r0, r0, #0xc
	ADD      r4, sp, #0x3d0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080481E4|
|unk_080481E4|
	INCBIN	baserom.gba_0x481e4_0x481e6.extracted
|sub_080481E6|
	LSL      r0, r0, #0xc
	LDR      r3, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x28]
	LDR      r0, [pc, #0x2c]
	MOV      r1, #1
	STR      r0, [r2]
	STRB     r1, [r2, #4]
	ADD      r2, #8
	STR      r0, [r2]
	MOV      r1, #0
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x18]
	ADD      r2, #8
	ADD      r1, #0x10
	STR      r0, [r1]
	MOV      r1, #2
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0xc]
	ADD      r1, #0x18
	STR      r0, [r1]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	BX       lr
	LSL      r0, r0, #0
	ADD      r4, r7, r4
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r3, r5}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048228|
|unk_08048228|
	INCBIN	baserom.gba_0x48228_0x4822a.extracted
|sub_0804822A|
	LSL      r0, r0, #0xc
	ADR      r0, |loc_080484E0|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048238|
|unk_08048238|
	INCBIN	baserom.gba_0x48238_0x4823a.extracted
|sub_0804823A|
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0xd0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048248|
	DCW      0x1964
	DCW      0x0300,0xbe08
|loc_0804824E|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	MOV      r0, #0
	STR      r0, [r1]
	STR      r0, [r1, #4]
	STR      r0, [r1, #8]
	STR      r0, [r1, #0xc]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, r2, r6
	LSL      r0, r0, #0xc
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x24]
	MOV      r2, #8
	ADD      r0, r4, #0
	ADD      r0, #0x44
	ADD      r1, r0, #0
	ADD      r1, #0x18
	LDR      r3, [pc, #0x1c]
	BL       |__vecmap1c__FPvT1iPFPv_v|
	ADD      r0, r4, #0
	ADD      r0, #0x5c
	ADD      r1, r0, #0
	MOV      r2, #0xc
	ADD      r1, #0x30
	LDR      r3, [pc, #0x10]
	BL       |__vecmap1c__FPvT1iPFPv_v|
	POP      {r4, pc}
	LSL      r0, r0, #0
	ADD      r4, r4, r6
	LSL      r0, r0, #0xc
	LSL      r1, r4, #0x1d
	LSR      r5, r0, #0x20
	LSL      r1, r2, #0x1e
	LSR      r5, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_080482A0|
|unk_080482A0|
	INCBIN	baserom.gba_0x482a0_0x482a2.extracted
|sub_080482A2|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080482AC|
|unk_080482AC|
	INCBIN	baserom.gba_0x482ac_0x482ae.extracted
|sub_080482AE|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x3a0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080482BC|
|unk_080482BC|
	INCBIN	baserom.gba_0x482bc_0x482be.extracted
|sub_080482BE|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x70]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x80]
	LDR      r1, [pc, #0x84]
	PUSH     {r4}
	STR      r0, [r1]
	LDR      r0, [pc, #0x7c]
	LDR      r2, [pc, #0x84]
	ADD      r0, #0x10
	STR      r2, [r0]
	MOV      r0, #3
	ADD      r1, #0x10
	STRB     r0, [r1, #4]
	ADD      r1, #8
	STR      r2, [r1]
	MOV      r2, #4
	STRB     r2, [r1, #4]
	LDR      r3, [pc, #0x68]
	LDR      r1, [pc, #0x70]
	ADD      r3, #0x20
	STR      r1, [r3]
	STRB     r0, [r3, #4]
	ADD      r3, #8
	STR      r1, [r3]
	STRB     r2, [r3, #4]
	LDR      r1, [pc, #0x58]
	LDR      r2, [pc, #0x64]
	ADD      r1, #0x30
	STRB     r0, [r1, #4]
	STR      r2, [r1]
	MOV      r1, #2
	ADD      r3, #0x10
	STRB     r1, [r3, #4]
	STR      r2, [r3]
	LDR      r2, [pc, #0x44]
	LDR      r4, [pc, #0x48]
	ADD      r2, #4
	STR      r4, [r2]
	MOV      r2, #5
	ADD      r3, #8
	STRB     r2, [r3, #4]
	LDR      r2, [pc, #0x4c]
	STR      r2, [r3]
	LDR      r2, [pc, #0x34]
	ADD      r3, #8
	ADD      r2, #0x48
	STRB     r0, [r2, #4]
	LDR      r2, [pc, #0x44]
	STR      r2, [r3]
	LDR      r2, [pc, #0x28]
	ADD      r2, #0x50
	STRB     r1, [r2, #4]
	LDR      r1, [pc, #0x3c]
	STR      r1, [r2]
	LDR      r1, [pc, #0x3c]
	SUB      r2, #0x48
	STR      r1, [r2]
	LDR      r1, [pc, #0x3c]
	ADD      r2, #4
	STR      r1, [r2]
	LDR      r1, [pc, #0x10]
	ADD      r1, #0x58
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x34]
	STR      r0, [r1]
	POP      {r4}
	BX       lr
|loc_08048346|
	DCW      0x0000
	DCW      0x985c,0x0804,0x1b00,0x0300,0xa188,0x0804,0xd784,0x0804
	DCW      0xc720,0x0804,0xe0ac
|loc_0804835E|
	LSR      r4, r0, #0x20
	ADR      r7, |loc_08048424|
	LSR      r4, r0, #0x20
	LDR      r6, [sp, #0x100]
	LSR      r4, r0, #0x20
	STMIA    r3!, {r2, r3, r4, r6}
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048620|
	LSR      r4, r0, #0x20
	ADR      r7, |loc_08048564|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_080486B8|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0x48]
	LDR      r1, [pc, #0x4c]
	LDR      r3, [pc, #0x58]
	STR      r0, [r1]
	ADD      r1, #4
	LDR      r0, [pc, #0x48]
	ADD      r2, r1, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x48]
	LDR      r1, [pc, #0x44]
	STR      r0, [r2]
	LDR      r0, [pc, #0x4c]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x48]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x48]
	ADD      r2, #4
	STR      r0, [r2]
	LDR      r0, [pc, #0x44]
	ADD      r2, #4
	STR      r0, [r2]
	ADD      r0, r2, #4
	STR      r1, [r0]
	ADD      r0, #4
	STR      r3, [r0]
	LDR      r1, [pc, #0x18]
	LDR      r0, [pc, #0x38]
	ADD      r1, #0x24
	STR      r0, [r1]
	LDR      r0, [pc, #0x38]
	ADD      r1, #4
	STR      r0, [r1]
	LDR      r0, [pc, #0x34]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_080483C4|
	DCW      0xc464
	DCW      0x0804,0x1b60,0x0300,0xda40,0x0804,0xdf3c,0x0804,0xe110
	DCW      0x0804,0xda50,0x0804,0xe194,0x0804,0xc474,0x0804,0xcd8c
	DCW      0x0804,0xd868,0x0804,0xe054,0x0804,0xe40c,0x0804,0xe374
|loc_080483F6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_08048400|
|unk_08048400|
	INCBIN	baserom.gba_0x48400_0x48402.extracted
|sub_08048402|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804840C|
|unk_0804840C|
	INCBIN	baserom.gba_0x4840c_0x4840e.extracted
|sub_0804840E|
	LSL      r0, r0, #0xc
	ADR      r2, |loc_08048464|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
	STR      r0, [r1]
	BX       lr
|sub_0804841C|
|unk_0804841C|
	INCBIN	baserom.gba_0x4841c_0x4841e.extracted
|sub_0804841E|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_08048424|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|unk_08048430|
	INCBIN	baserom.gba_0x48430_0x48432.extracted
	LSR      r4, r0, #0x20
	ADD      r4, r7, #0
	LSL      r0, r0, #0xc
	ADD      r3, sp, #0x1b0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x34]
	MOV      r2, #0x41
	LSL      r2, r2, #3
	MOV      r0, #0
	STR      r0, [r1, #4]
	ADD      r2, r1, r2
	STR      r0, [r2]
	LDR      r2, [pc, #0x2c]
	ADD      r2, r1, r2
	STR      r0, [r2]
	MOV      r2, #0x61
	LSL      r2, r2, #4
	ADD      r2, r1, r2
	STR      r0, [r2]
	MOV      r2, #0x2f
	LSL      r2, r2, #6
	ADD      r1, r1, r2
	STR      r0, [r1, #0x38]
	LDR      r1, [pc, #0x1c]
	LDR      r2, [pc, #0x18]
|loc_08048464|
	STR      r1, [r2]
	LDR      r1, [pc, #0xc]
	SUB      r1, #8
	STR      r0, [r1, #4]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r4, r1, #1
	LSL      r0, r0, #0xc
	LSL      r4, r1, #0x10
	LSL      r0, r0, #0
	CMP      r2, #0x4c
	LSL      r0, r0, #0xc
	STR      r2, [sp, #0x1d0]
	LSR      r4, r0, #0x20
	STR      r6, [sp, #0x1c0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
|loc_0804848C|
	STR      r0, [r1]
	BX       lr
|sub_08048490|
|unk_08048490|
	INCBIN	baserom.gba_0x48490_0x48492.extracted
|sub_08048492|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x28]
	LDR      r1, [pc, #0x2c]
	STR      r0, [r1]
	MOV      r0, #3
	ADD      r1, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x24]
	STR      r0, [r1]
	LDR      r0, [pc, #0x24]
	ADD      r1, #8
	STR      r0, [r1]
	MOV      r0, #3
	ADD      r1, #8
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x1c]
	STR      r0, [r1]
	ADD      r1, #8
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x18]
	STR      r0, [r1]
	BX       lr
|loc_080484C0|
	DCW      0xc384
	DCW      0x0804,0x2b38,0x0300,0xbef0,0x0804,0xc790,0x0804,0xc3a8
	DCW      0x0804,0xe00c,0x0804,0x4770
|loc_080484DA|
	LSL      r0, r0, #0
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_080484E0|
	STR      r0, [r1]
	BX       lr
|sub_080484E4|
|unk_080484E4|
	INCBIN	baserom.gba_0x484e4_0x484e6.extracted
|sub_080484E6|
	LSL      r0, r0, #0xc
	STR      r7, [sp, #0x290]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080484F8|
|unk_080484F8|
	INCBIN	baserom.gba_0x484f8_0x484fa.extracted
|sub_080484FA|
	LSL      r0, r0, #0xc
	ADD      r6, sp, #0x50
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048508|
|unk_08048508|
	INCBIN	baserom.gba_0x48508_0x4850a.extracted
|sub_0804850A|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x130]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048518|
|unk_08048518|
	INCBIN	baserom.gba_0x48518_0x4851a.extracted
|sub_0804851A|
	LSL      r0, r0, #0xc
	STR      r7, [sp, #0x390]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x14]
	MOV      r0, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	ADD      r1, #8
	MOV      r0, #4
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0xc]
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	CMP      r3, #0xb4
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r3, r4, r6}
	LSR      r4, r0, #0x20
	BGT      |loc_0804848C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804854C|
|unk_0804854C|
	INCBIN	baserom.gba_0x4854c_0x4854e.extracted
|sub_0804854E|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x1e0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804855C|
|unk_0804855C|
	INCBIN	baserom.gba_0x4855c_0x4855e.extracted
|sub_0804855E|
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x3d0]
	LSR      r4, r0, #0x20
|loc_08048564|
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804856C|
|unk_0804856C|
	INCBIN	baserom.gba_0x4856c_0x4856e.extracted
|sub_0804856E|
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0x270]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	MOV      r1, #0
	STR      r1, [r0]
	STR      r1, [r0, #0xc]
	LDR      r1, [pc, #8]
	STR      r1, [r0, #8]
	BX       lr
	LSL      r0, r0, #0
	CMP      r3, #0xd8
	LSL      r0, r0, #0xc
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1, #8]
	ADD      r1, #0xff
	LDR      r0, [pc, #0xc]
	ADD      r1, #0x95
	STR      r0, [r1, #8]
	BX       lr
|sub_0804859C|
|unk_0804859C|
	INCBIN	baserom.gba_0x4859c_0x4859e.extracted
|sub_0804859E|
	LSR      r4, r0, #0x20
	CMP      r5, #0x98
	LSL      r0, r0, #0xc
	STR      r3, [sp, #0x70]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080485B0|
|unk_080485B0|
	INCBIN	baserom.gba_0x485b0_0x485b2.extracted
|sub_080485B2|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x20
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r6!, {r2, r3, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	CMP      r7, #0xa8
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x160
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080485DC|
|unk_080485DC|
	INCBIN	baserom.gba_0x485dc_0x485de.extracted
|sub_080485DE|
	LSL      r0, r0, #0xc
	LDR      r1, [sp, #0x3f0]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r5, sp, #0x3c0
	LSR      r4, r0, #0x20
	CMP      r7, #0xc4
	LSL      r0, r0, #0xc
	LDR      r4, [sp, #0x60]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
|loc_0804860C|
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r4!, {r4}
	LSR      r4, r0, #0x20
	CMP      r7, #0xcc
	LSL      r0, r0, #0xc
|unk_08048618|
	INCBIN	baserom.gba_0x48618_0x4861a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_08048620|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_0804862A|
|unk_0804862A|
	INCBIN	baserom.gba_0x4862a_0x4862e.extracted
|sub_0804862E|
	LSR      r4, r0, #0x20
	CMP      r7, #0xd8
	LSL      r0, r0, #0xc
	ADR      r6, |loc_080488B8|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048640|
|unk_08048640|
	INCBIN	baserom.gba_0x48640_0x48642.extracted
|sub_08048642|
	LSL      r0, r0, #0xc
	LDR      r6, [sp, #0xc0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048650|
|unk_08048650|
	INCBIN	baserom.gba_0x48650_0x48652.extracted
|sub_08048652|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x250
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048660|
|unk_08048660|
	INCBIN	baserom.gba_0x48660_0x48662.extracted
|sub_08048662|
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048928|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0x170]
	LSR      r4, r0, #0x20
	CMP      r7, #0xf0
	LSL      r0, r0, #0xc
	POP      {pc}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804868C|
|unk_0804868C|
	INCBIN	baserom.gba_0x4868c_0x4868e.extracted
|sub_0804868E|
	LSL      r0, r0, #0xc
	BVS      |loc_0804860C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|loc_080486A4|
	CMP      r7, #0xfc
	LSL      r0, r0, #0xc
	ADR      r7, |loc_080486AC|
	LSR      r4, r0, #0x20
|loc_080486AC|
	ADD      r2, sp, #0x390
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
|loc_080486B8|
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BVS      |loc_080486A4|
	LSR      r4, r0, #0x20
	ADD      r0, #4
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_080486DE|
	DCW      0x0000
	DCW      0x3014,0x0300,0xb740
|loc_080486E6|
	LSR      r4, r0, #0x20
	ADR      r0, |loc_08048A2C|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
	ADD      r0, #0x1c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x70
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048716|
|unk_08048716|
	INCBIN	baserom.gba_0x48716_0x4871a.extracted
|sub_0804871A|
	LSR      r4, r0, #0x20
	ADD      r0, #0x24
	LSL      r0, r0, #0xc
	ADR      r6, |sub_08048804|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048732|
|unk_08048732|
	INCBIN	baserom.gba_0x48732_0x48736.extracted
|sub_08048736|
	LSR      r4, r0, #0x20
	ADD      r0, #0x30
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048860|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r5, r6}
	LSR      r4, r0, #0x20
	ADD      r0, #0x3c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0xb0
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r0, #0x4c
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x130
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048884|
	LSR      r4, r0, #0x20
	ADD      r0, #0x5c
	LSL      r0, r0, #0xc
	POP      {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804879C|
|unk_0804879C|
	INCBIN	baserom.gba_0x4879c_0x4879e.extracted
|sub_0804879E|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048868|
	LSR      r4, r0, #0x20
	ADD      r0, #0x68
	LSL      r0, r0, #0xc
	POP      {r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080487C8|
|unk_080487C8|
	INCBIN	baserom.gba_0x487c8_0x487ca.extracted
|sub_080487CA|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_080487D4|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r5!, {r3, r4}
	LSR      r4, r0, #0x20
	ADD      r0, #0x74
	LSL      r0, r0, #0xc
|unk_080487E8|
	INCBIN	baserom.gba_0x487e8_0x487ea.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080487F4|
|unk_080487F4|
	INCBIN	baserom.gba_0x487f4_0x487f6.extracted
|sub_080487F6|
	LSL      r0, r0, #0xc
|unk_080487F8|
	INCBIN	baserom.gba_0x487f8_0x487fa.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048804|
|unk_08048804|
	INCBIN	baserom.gba_0x48804_0x48806.extracted
|sub_08048806|
	LSL      r0, r0, #0xc
|unk_08048808|
	INCBIN	baserom.gba_0x48808_0x4880a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r0, #0x8c
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r3, r6, r7}
	LSR      r4, r0, #0x20
|unk_08048828|
	INCBIN	baserom.gba_0x48828_0x4882a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048834|
	DCW      0x30a0
	DCW      0x0300,0xbd88
|loc_0804883A|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048844|
|unk_08048844|
	INCBIN	baserom.gba_0x48844_0x48846.extracted
|sub_08048846|
	LSL      r0, r0, #0xc
|unk_08048848|
	INCBIN	baserom.gba_0x48848_0x4884a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r4!, {r2, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
|loc_08048860|
	ADD      r0, #0xa8
	LSL      r0, r0, #0xc
|unk_08048864|
	INCBIN	baserom.gba_0x48864_0x48866.extracted
	LSR      r4, r0, #0x20
|loc_08048868|
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BVC      |loc_080487D4|
	LSR      r4, r0, #0x20
	ADD      r0, #0xb0
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r3, r4, r5, r6, r7}
	LSR      r4, r0, #0x20
|loc_08048884|
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804888C|
|unk_0804888C|
		ADD r0, #0xb8
|sub_0804888E|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r4, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_0804889C|
|unk_0804889C|
	INCBIN	baserom.gba_0x4889c_0x4889e.extracted
|sub_0804889E|
	LSL      r0, r0, #0xc
	SUB      sp, #0x160
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080488AC|
|unk_080488AC|
	INCBIN	baserom.gba_0x488ac_0x488ae.extracted
|sub_080488AE|
	LSL      r0, r0, #0xc
	ADR      r6, |sub_08048AF4|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
|loc_080488B8|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048930|
	LSR      r4, r0, #0x20
	ADD      r0, #0xc8
	LSL      r0, r0, #0xc
	POP      {r4, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STMIA    r2!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r0, #0xd0
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x1d0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080488F4|
|unk_080488F4|
	INCBIN	baserom.gba_0x488f4_0x488f6.extracted
|sub_080488F6|
	LSL      r0, r0, #0xc
	BCS      |sub_0804888C|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048900|
	STR      r0, [r1]
	BX       lr
|sub_08048904|
|unk_08048904|
	INCBIN	baserom.gba_0x48904_0x48906.extracted
|sub_08048906|
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r3, r4, r5}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLT      |loc_08048900|
	LSR      r4, r0, #0x20
	ADD      r0, #0xe0
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r5, r7}
	LSR      r4, r0, #0x20
|loc_08048928|
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
|loc_08048930|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_0804893A|
	DCW      0x0000
	DCW      0x30ec,0x0300,0xb7d0
|loc_08048942|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048A68|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048950|
|unk_08048950|
	INCBIN	baserom.gba_0x48950_0x48952.extracted
|sub_08048952|
	LSL      r0, r0, #0xc
	POP      {r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048960|
|unk_08048960|
	INCBIN	baserom.gba_0x48960_0x48962.extracted
|sub_08048962|
	LSL      r0, r0, #0xc
	LDR      r2, [sp, #0x170]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048974|
|unk_08048974|
	INCBIN	baserom.gba_0x48974_0x48976.extracted
|sub_08048976|
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
|sub_0804898A|
|unk_0804898A|
	INCBIN	baserom.gba_0x4898a_0x4898e.extracted
|sub_0804898E|
	LSR      r4, r0, #0x20
	ADD      r1, #8
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048B98|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_080489A0|
|unk_080489A0|
	INCBIN	baserom.gba_0x489a0_0x489a2.extracted
|sub_080489A2|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x210
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #2
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_080489B4|
	DCW      0x3118
	DCW      0x0300,0xb840
|loc_080489BA|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLS      |loc_08048A58|
	LSR      r4, r0, #0x20
	ADD      r1, #0x20
	LSL      r0, r0, #0xc
	STMIA    r6!, {r5}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r3!, {r2, r3, r5, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r1, #0x28
	LSL      r0, r0, #0xc
	SUB      sp, #0x80
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048A02|
|unk_08048A02|
	INCBIN	baserom.gba_0x48a02_0x48a06.extracted
|sub_08048A06|
	LSR      r4, r0, #0x20
	ADD      r1, #0x30
	LSL      r0, r0, #0xc
	LDMIA    r7!, {r2, r3, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A18|
|unk_08048A18|
	INCBIN	baserom.gba_0x48a18_0x48a1a.extracted
|sub_08048A1A|
	LSL      r0, r0, #0xc
	ADR      r6, |loc_08048B80|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A28|
|unk_08048A28|
	INCBIN	baserom.gba_0x48a28_0x48a2a.extracted
|sub_08048A2A|
	LSL      r0, r0, #0xc
|loc_08048A2C|
	LDR      r3, [sp, #0x3e0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048A38|
|unk_08048A38|
	INCBIN	baserom.gba_0x48a38_0x48a3a.extracted
|sub_08048A3A|
	LSL      r0, r0, #0xc
	LDR      r5, [sp, #0x2e0]
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	LDR      r0, [pc, #0x14]
	ADD      r1, #8
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048A54|
|unk_08048A54|
	INCBIN	baserom.gba_0x48a54_0x48a56.extracted
|sub_08048A56|
	LSL      r0, r0, #0xc
|loc_08048A58|
	LDR      r6, [sp, #0x2b0]
	LSR      r4, r0, #0x20
	STMIA    r2!, {r2, r7}
	LSR      r4, r0, #0x20
	ADD      r2, sp, #0xf0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0xc]
	LDR      r0, [pc, #0x10]
|loc_08048A68|
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_08048A72|
	DCW      0x0000
	DCW      0x3158,0x0300,0xb788
|loc_08048A7A|
	LSR      r4, r0, #0x20
	ADR      r1, |loc_08048AC0|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048A84|
	STR      r0, [r1]
	BX       lr
|sub_08048A88|
|unk_08048A88|
	INCBIN	baserom.gba_0x48a88_0x48a8a.extracted
|sub_08048A8A|
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r4, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	MOV      r0, #0
|loc_08048A94|
	STR      r0, [r1]
	BX       lr
|sub_08048A98|
|unk_08048A98|
	INCBIN	baserom.gba_0x48a98_0x48a9a.extracted
|sub_08048A9A|
	LSL      r0, r0, #0xc
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048AA4|
	DCW      0x31f8
	DCW      0x0300,0xbd78
|loc_08048AAA|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AB4|
|unk_08048AB4|
	INCBIN	baserom.gba_0x48ab4_0x48ab6.extracted
|sub_08048AB6|
	LSL      r0, r0, #0xc
|unk_08048AB8|
	INCBIN	baserom.gba_0x48ab8_0x48aba.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048AC0|
	STR      r0, [r1]
	BX       lr
|sub_08048AC4|
|unk_08048AC4|
	INCBIN	baserom.gba_0x48ac4_0x48ac6.extracted
|sub_08048AC6|
	LSL      r0, r0, #0xc
	ADD      r2, sp, #0x350
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048AD4|
	DCW      0x3204
	DCW      0x0300,0xb710
|loc_08048ADA|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AE4|
|unk_08048AE4|
	INCBIN	baserom.gba_0x48ae4_0x48ae6.extracted
|sub_08048AE6|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x2c0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048AF4|
|unk_08048AF4|
	INCBIN	baserom.gba_0x48af4_0x48af6.extracted
|sub_08048AF6|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r2, r4, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	LDR      r0, [pc, #0x14]
	STR      r0, [r1]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x14
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r5, r7}
	LSR      r4, r0, #0x20
|unk_08048B18|
	INCBIN	baserom.gba_0x48b18_0x48b1a.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048B24|
|unk_08048B24|
	INCBIN	baserom.gba_0x48b24_0x48b26.extracted
|sub_08048B26|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
|loc_08048B30|
	STR      r0, [r1]
	BX       lr
|sub_08048B34|
|unk_08048B34|
	INCBIN	baserom.gba_0x48b34_0x48b36.extracted
|sub_08048B36|
	LSL      r0, r0, #0xc
	BVS      |loc_08048A94|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048B44|
|unk_08048B44|
	INCBIN	baserom.gba_0x48b44_0x48b46.extracted
|sub_08048B46|
	LSL      r0, r0, #0xc
	BVS      |loc_08048A84|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLS      |loc_08048C30|
	LSR      r4, r0, #0x20
	ADD      r2, #0x2c
	LSL      r0, r0, #0xc
	POP      {r3, r6, pc}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048B76|
|unk_08048B76|
	INCBIN	baserom.gba_0x48b76_0x48b7a.extracted
|sub_08048B7A|
	LSR      r4, r0, #0x20
	ADD      r2, #0x34
	LSL      r0, r0, #0xc
|loc_08048B80|
	BLS      |loc_08048BEC|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BLT      |loc_08048B30|
	LSR      r4, r0, #0x20
|loc_08048B98|
	ADD      r2, #0x3c
	LSL      r0, r0, #0xc
	LDMIA    r3!, {r4, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048BA8|
	DCW      0x3244
	DCW      0x0300,0xbd68
|loc_08048BAE|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048BBE|
|unk_08048BBE|
	INCBIN	baserom.gba_0x48bbe_0x48bc2.extracted
|sub_08048BC2|
	LSR      r4, r0, #0x20
	ADD      r2, #0x48
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, pc}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048BD4|
|unk_08048BD4|
	INCBIN	baserom.gba_0x48bd4_0x48bd6.extracted
|sub_08048BD6|
	LSL      r0, r0, #0xc
|unk_08048BD8|
	INCBIN	baserom.gba_0x48bd8_0x48bda.extracted
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048BE4|
|unk_08048BE4|
	INCBIN	baserom.gba_0x48be4_0x48be6.extracted
|sub_08048BE6|
	LSL      r0, r0, #0xc
	BMI      |loc_08048CA4|
	LSR      r4, r0, #0x20
|loc_08048BEC|
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048BF4|
|unk_08048BF4|
	INCBIN	baserom.gba_0x48bf4_0x48bf6.extracted
|sub_08048BF6|
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0x120
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	BCC      |loc_08048C30|
	LSR      r4, r0, #0x20
	ADD      r2, #0x5c
	LSL      r0, r0, #0xc
	POP      {r3, r4, r5, r6}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDMIA    r3!, {r3, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r2, #0x64
	LSL      r0, r0, #0xc
|loc_08048C30|
	SUB      sp, #0x40
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048C42|
|unk_08048C42|
	INCBIN	baserom.gba_0x48c42_0x48c46.extracted
|sub_08048C46|
	LSR      r4, r0, #0x20
	ADD      r2, #0x6c
	LSL      r0, r0, #0xc
	ADR      r0, |loc_08049010|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048C58|
|unk_08048C58|
	INCBIN	baserom.gba_0x48c58_0x48c5a.extracted
|sub_08048C5A|
	LSL      r0, r0, #0xc
	LDMIA    r7!, {r3, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
|loc_08048C70|
	STMIA    r6!, {r3, r4, r6, r7}
	LSR      r4, r0, #0x20
	ADD      r2, #0x78
	LSL      r0, r0, #0xc
	ADD      r5, sp, #0xa0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048C84|
|unk_08048C84|
	INCBIN	baserom.gba_0x48c84_0x48c86.extracted
|sub_08048C86|
	LSL      r0, r0, #0xc
|loc_08048C88|
	STMIA    r1!, {r2, r4, r5, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #0x10]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	ADD      r2, #0x8c
	LSL      r0, r0, #0xc
|loc_08048CA4|
	STMIA    r7!, {r2, r4, r5, r7}
	LSR      r4, r0, #0x20
	ADD      r5, sp, #0x220
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #8
	STR      r0, [r1]
	BX       lr
|loc_08048CBA|
	DCW      0x0000
	DCW      0xcff0,0x0804,0x3294,0x0300,0xb630
|loc_08048CC6|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|loc_08048CD6|
	DCW      0x0000
	DCW      0xd014,0x0804,0x32a0,0x0300,0xb668
|loc_08048CE2|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048CEC|
	DCW      0x32a8
	DCW      0x0300,0xb688
|loc_08048CF2|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048CFC|
	DCW      0x32ac
	DCW      0x0300,0xcb00
|loc_08048D02|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D0C|
|unk_08048D0C|
	INCBIN	baserom.gba_0x48d0c_0x48d0e.extracted
|sub_08048D0E|
	LSL      r0, r0, #0xc
	POP      {r3, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D1C|
|unk_08048D1C|
	INCBIN	baserom.gba_0x48d1c_0x48d1e.extracted
|sub_08048D1E|
	LSL      r0, r0, #0xc
	SWI      0x74
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D2C|
|unk_08048D2C|
	INCBIN	baserom.gba_0x48d2c_0x48d2e.extracted
|sub_08048D2E|
	LSL      r0, r0, #0xc
	LDMIA    r4!, {r2, r4, r5}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #8]
	MOV      r0, #3
	STRB     r0, [r1, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D40|
|unk_08048D40|
	INCBIN	baserom.gba_0x48d40_0x48d42.extracted
|sub_08048D42|
	LSL      r0, r0, #0xc
	BCC      |loc_08048C88|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D50|
|unk_08048D50|
	INCBIN	baserom.gba_0x48d50_0x48d52.extracted
|sub_08048D52|
	LSL      r0, r0, #0xc
	BVS      |loc_08048C70|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D60|
|unk_08048D60|
		ADD r2, #0xc8
|sub_08048D62|
	LSL      r0, r0, #0xc
	STMIA    r3!, {r4, r5, r6, r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D70|
|unk_08048D70|
	INCBIN	baserom.gba_0x48d70_0x48d72.extracted
|sub_08048D72|
	LSL      r0, r0, #0xc
	BVC      |sub_08048D60|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048D80|
	DCW      0x32d0
	DCW      0x0300,0xb81c
|loc_08048D86|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048D90|
|unk_08048D90|
	INCBIN	baserom.gba_0x48d90_0x48d92.extracted
|sub_08048D92|
	LSL      r0, r0, #0xc
	STMIA    r6!, {r7}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|loc_08048DA0|
	DCW      0x32d8
	DCW      0x0300,0xde24
|loc_08048DA6|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DB0|
|unk_08048DB0|
	INCBIN	baserom.gba_0x48db0_0x48db2.extracted
|sub_08048DB2|
	LSL      r0, r0, #0xc
|loc_08048DB4|
	SUB      sp, #0x1a0
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DC0|
|unk_08048DC0|
	INCBIN	baserom.gba_0x48dc0_0x48dc2.extracted
|sub_08048DC2|
	LSL      r0, r0, #0xc
	STMIA    r1!, {r6}
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DD0|
|unk_08048DD0|
	INCBIN	baserom.gba_0x48dd0_0x48dd2.extracted
|sub_08048DD2|
	LSL      r0, r0, #0xc
	ADR      r1, |loc_08048DD8|
	LSR      r4, r0, #0x20
|loc_08048DD8|
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048DE6|
|unk_08048DE6|
	INCBIN	baserom.gba_0x48de6_0x48dea.extracted
|sub_08048DEA|
	LSR      r4, r0, #0x20
	ADD      r2, #0xf4
	LSL      r0, r0, #0xc
	ADR      r1, |loc_08048F54|
	LSR      r4, r0, #0x20
	LDR      r1, [pc, #4]
	LDR      r0, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048DFC|
|unk_08048DFC|
	INCBIN	baserom.gba_0x48dfc_0x48dfe.extracted
|sub_08048DFE|
	LSL      r0, r0, #0xc
	BCS      |loc_08048DB4|
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	STR      r3, [sp, #0x320]
	LSR      r4, r0, #0x20
	ADD      r4, #0x8c
	LSL      r0, r0, #0xc
	STR      r5, [sp, #0x1b0]
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	ADD      r1, #4
	STR      r0, [r1]
	BX       lr
	LSL      r0, r0, #0
	LDR      r0, [sp, #0xd0]
	LSR      r4, r0, #0x20
	LDR      r2, [pc, #0x1c0]
	LSL      r0, r0, #0xc
|unk_08048E38|
	INCBIN	baserom.gba_0x48e38_0x48e3a.extracted
	LSR      r4, r0, #0x20
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E44|
|unk_08048E44|
	INCBIN	baserom.gba_0x48e44_0x48e46.extracted
|sub_08048E46|
	LSR      r4, r0, #0x20
	ADD      r4, r4, r5
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E54|
|unk_08048E54|
	INCBIN	baserom.gba_0x48e54_0x48e56.extracted
|sub_08048E56|
	LSR      r4, r0, #0x20
	SUB      r0, r6, r3
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r1, [pc, #0x14]
	LDR      r0, [pc, #0xc]
	STR      r0, [r1]
	BX       lr
|loc_08048E6A|
	DCW      0x0000
	DCW      0x9af0,0x0804,0x1c44,0x0300,0xe454
|loc_08048E76|
	LSR      r4, r0, #0x20
	CMP      r2, #0x4c
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #4]
	LDR      r1, [pc, #8]
	STR      r0, [r1]
	BX       lr
|sub_08048E84|
|unk_08048E84|
	INCBIN	baserom.gba_0x48e84_0x48e86.extracted
|sub_08048E86|
	LSR      r4, r0, #0x20
	CMP      r3, #0xd4
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0x14]
	PUSH     {r3, lr}
	LDR      r0, [r0]
	CMP      r0, #0
	BEQ      |loc_08048EA2|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r2, r2, r1
	MOV      r1, #1
	BL       |loc_08046AA4|
|loc_08048EA2|
	POP      {r3, pc}
|sub_08048EA4|
|unk_08048EA4|
	INCBIN	baserom.gba_0x48ea4_0x48ea6.extracted
|sub_08048EA6|
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #8]
	LDR      r1, [pc, #0xc]
	STR      r0, [r1]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048EB4|
|unk_08048EB4|
	INCBIN	baserom.gba_0x48eb4_0x48eb6.extracted
|sub_08048EB6|
	LSR      r4, r0, #0x20
	ADD      r4, #0x90
	LSL      r0, r0, #0xc
	LDR      r0, [pc, #0xc]
	LDR      r1, [pc, #0x10]
	STR      r0, [r1]
	LDR      r0, [pc, #0x10]
	SUB      r1, #4
	STR      r0, [r1]
	BX       lr
|sub_08048ECA|
|unk_08048ECA|
; cited by 0x08048EBC (a pc-relative load targets 0x08048ECC)
	INCBIN	baserom.gba_0x48eca_0x48f54.extracted
|loc_08048F54|
|unk_08048F54|
; cited by 0x08048E34 (a pc-relative load targets 0x08048FF8)
	INCBIN	baserom.gba_0x48f54_0x49010.extracted
|loc_08049010|
|unk_08049010|
; cited by 0x08048ED0 (a pc-relative load targets 0x080490A4)
	INCBIN	baserom.gba_0x49010_0x49114.extracted
