	CODE16
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
	EXPORT |loc_08047A08|
	EXPORT |sub_08047A1C|
	EXPORT |sub_08047A28|
