	CODE16
|unk_08054850|
; cited by 0x0805495C (a pc-relative load targets 0x080549A0)
	CODE32
|arm_08054850|
	TST      ip, #0x10
	MOVEQ    r2, r1
	STMDB    sp!, {r0, r1, r2, r3}
	STMDB    sp!, {r0, r1}
	STMDB    sp!, {r2, r3, ip, lr}
	BL       |arm_08047A2C|
	LDMIA    sp!, {r2, r3, ip, lr}
	MOV      r2, r0
	LDMIA    sp!, {r0, r1}
	LDR      r1, [r2]
	BIC      r3, ip, r1, lsl #18
	ANDS     r3, r3, #192, 10
	ORRNE    ip, ip, #64, 8
	MOV      r3, ip, LSL #1
	MOV      r3, r3, LSR #0x1b
	ORR      r1, r1, r3
	AND      r3, r1, #112, 14
	ORR      ip, ip, r3
	STR      r1, [r2]
	AND      r3, ip, #0xf
	TEQ      r3, #8
	ANDNE    r3, ip, #0x70
	ORRNE    ip, ip, r3, lsl #3
	MOVEQ    r3, #128, 22
	BICEQS   r3, r3, ip
	ORREQ    ip, ip, #192, 16
	TST      ip, #128, 10
	BNE      |arm_080548F8|
	TST      ip, #64, 10
	BNE      |arm_080548E8|
	TST      ip, #64, 8
	BNE      |arm_08054924|
	TST      ip, #128, 12
	BNE      |arm_08054908|
	TST      r1, #64, 30
	LDMIA    sp!, {r0, r1, r2, r3}
	BEQ      |arm_08054968|
	B        |arm_08054F14|
|arm_080548E8|
	TST      r1, #64, 28
	LDMIA    sp!, {r0, r1, r2, r3}
	BEQ      |arm_0805493C|
	B        |arm_08054F14|
|arm_080548F8|
	TST      r1, #128, 28
	LDMIA    sp!, {r0, r1, r2, r3}
	BEQ      |arm_08054934|
	B        |arm_08054F14|
|arm_08054908|
	TST      r1, #128, 30
	LDMIA    sp!, {r0, r1, r2, r3}
	BNE      |arm_08054F14|
	TST      ip, #0x10
	EORNE    r2, r1, r3
	EOREQ    r2, r0, r2
	B        |arm_08054948|
|arm_08054924|
	TST      r1, #64, 26
	LDMIA    sp!, {r0, r1, r2, r3}
	BEQ      |arm_08054934|
	B        |arm_08054F14|
|arm_08054934|
	TST      ip, #0x10
	BX       lr
|arm_0805493C|
	TST      ip, #0x80
	ANDNE    r2, r1, #128, 8
	ANDEQ    r2, r0, #128, 8
|arm_08054948|
	AND      r2, r2, #128, 8
	TST      ip, #0x10
	ADDNE    r0, pc, #0x38
|arm_08054954|
	DCD     0x18900003
	ORRNE    r1, r1, r2
	LDREQ    r0, [pc, #0x3c]
	ORREQ    r0, r0, r2
	BX       lr
|arm_08054968|
	TST      ip, #0x80
	ANDNE    r2, r1, #128, 8
	ANDEQ    r2, r0, #128, 8
	TST      ip, #0x10
	ADDNE    r0, pc, #0x28
|arm_0805497C|
	DCD     0x18900003
	ORRNE    r1, r1, r2
	LDREQ    r0, [pc, #0x24]
	ORREQ    r0, r0, r2
	B        |arm_08054E78|
|arm_08054990|
	DCD     0x00000000
|arm_08054994|
	DCD     0x7FF00000
|arm_08054998|
	DCD     0xFFFFFFFF
|arm_0805499C|
	DCD     0x7FEFFFFF
|arm_080549A0|
	DCD     0x7F800000
	CODE16
	CODE16
	EXPORT |sub_080549A6|
|unk_080549A4|
	INCBIN	baserom.gba_0x549a4_0x549a6.extracted
