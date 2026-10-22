	CODE16
|sub_0804AA82|
	LSL      r0, r0, #0
	SUB      r2, #0x7d
	LSL      r0, r0, #0
	LDR      r4, [pc, #0x284]
|unk_0804AA8A|
	INCBIN	baserom.gba_0x4aa8a_0x4aa8e.extracted
	LSL      r0, r0, #0
|unk_0804AA90|
	INCBIN	baserom.gba_0x4aa90_0x4aa92.extracted
	LSL      r0, r0, #0
|unk_0804AA94|
; cited by 0x0004864A (a pool word names 0x0804AA94)
	DCD	0xFFFDEE45
	DCD	0xFFFDEE6F
	LDR      r2, [pc, #0x374]
	LSL      r0, r0, #0
|unk_0804AAA0|
	INCBIN	baserom.gba_0x4aaa0_0x4aaa2.extracted
|sub_0804AAA2|
|unk_0804AAA2|
; cited by 0x0804A8FC (a pc-relative load targets 0x0804AAA4)
	DCW	0x0000
	DCD	0xFFFE9805
	DCD	0xFFFE980B
	DCD	0xFFFE9863
	DCD	0xFFFE9879
	DCD	0x00006A25
	DCW	0xE771
|sub_0804AABA|
|unk_0804AABA|
	INCBIN	baserom.gba_0x4aaba_0x4aabe.extracted
	LSL      r0, r0, #0
	STR      r7, [sp, #0x3cc]
|unk_0804AAC2|
	DCW	0xFFFE
	DCD	0xFFFE984B
	DCD	0xFFFE9861
	DCW	0x6A25
	LSL      r0, r0, #0
	ORR      r5, r3
	LSL      r0, r0, #0
	SUB      r3, #0xf1
	LSL      r0, r0, #0
	STRB     r5, [r3, r3]
	LSL      r0, r0, #0
	LDR      r2, [pc, #0x274]
	LSL      r0, r0, #0
|unk_0804AAE0|
	INCBIN	baserom.gba_0x4aae0_0x4aae2.extracted
	LSL      r0, r0, #0
	SUB      r2, #0x1d
	LSL      r0, r0, #0
	STRB     r5, [r4, r3]
	LSL      r0, r0, #0
	LDR      r2, [pc, #0x234]
	LSL      r0, r0, #0
|unk_0804AAF0|
	INCBIN	baserom.gba_0x4aaf0_0x4aaf2.extracted
|sub_0804AAF2|
; cited by 0x0804A970 (a pc-relative load targets 0x0804AB48)
	INCLUDE rawlabeled_4aaf2.s
