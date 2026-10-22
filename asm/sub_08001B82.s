	CODE16
|sub_08001B82|
	MOV      r5, #0
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r6, [pc, #0x78]
	LDR      r2, [r0, #4]
	LDR      r0, [r6, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001BB0|
	LDR      r1, [pc, #0x6c]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	STR      r5, [r0, #0x10]
	STR      r2, [r0, #0xc]
|loc_08001BB0|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001BBA|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001BBA|
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	LDR      r5, [pc, #0x40]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r5, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001BF0|
	LDR      r1, [pc, #0x2c]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	STR      r2, [r0, #8]
|loc_08001BF0|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001BFA|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001BFA|
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
|loc_08001C02|
	DCW      0x0000
	DCW      0xdd58,0x0804,0x4fbc,0x0805,0xb940,0x0804,0xc864,0x0804
	DCW      0xe0fc,0x0804,0xdeb4
|loc_08001C1A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	LDR      r5, [pc, #0x28c]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r5, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001C4C|
	LDR      r1, [pc, #0x270]
	STMIA    r0!, {r1, r2}
	SUB      r0, #8
	MOV      r1, #1
	STR      r1, [r0, #8]
|loc_08001C4C|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001C56|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001C56|
	LDR      r0, [r5, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r7, [pc, #0x24c]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r7, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001C9E|
	LDR      r1, [pc, #0x21c]
	STMIA    r0!, {r1, r2, r5, r6}
	SUB      r0, #0x10
|loc_08001C9E|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001CA8|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001CA8|
	LDR      r0, [r7, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r7, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0x1d0]
	MOV      r1, #8
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0x34
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001CFE|
	LDR      r1, [pc, #0x1c4]
	STMIA    r0!, {r1, r2, r6, r7}
	SUB      r0, #0x10
	STR      r5, [r0, #0x10]
	STR      r2, [r0, #0x30]
|loc_08001CFE|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001D08|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001D08|
	LDR      r0, [pc, #0x1a4]
	LDR      r0, [r0, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r7, [pc, #0x198]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r7, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0x30
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001D54|
	LDR      r1, [pc, #0x170]
	STMIA    r0!, {r1, r2, r5, r6}
	SUB      r0, #0x10
	STR      r2, [r0, #0x2c]
|loc_08001D54|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001D5E|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001D5E|
	LDR      r0, [r7, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	LDR      r6, [pc, #0x144]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r6, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001D9C|
	LDR      r1, [pc, #0x12c]
	STMIA    r0!, {r1, r2, r5}
	SUB      r0, #0xc
|loc_08001D9C|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001DA6|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001DA6|
	LDR      r0, [r6, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {r3, r4, r5, r6, r7, lr}
	LDR      r1, [r0]
	LDR      r7, [pc, #0xfc]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [r7, #0x18]
	MOV      r1, #8
	BL       |loc_08011C70|
	ADD      r4, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	MOV      r2, #0
	CMP      r0, #0
	BEQ      |loc_08001DEE|
	LDR      r1, [pc, #0xdc]
	STMIA    r0!, {r1, r2, r5, r6}
	SUB      r0, #0x10
|loc_08001DEE|
	ADD      r1, r0, #0
	CMP      r4, #0
	BEQ      |loc_08001DF8|
	ADD      r2, r4, #0
	ADD      r2, #0xc
|loc_08001DF8|
	LDR      r0, [r7, #0x1c]
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, r6, r7, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r2, [r0, #4]
	LDR      r0, [pc, #0x94]
	MOV      r1, #8
	LDR      r0, [r0, #0x18]
	BL       |loc_08011C70|
	STR      r4, [r0, #0x18]
	LDR      r1, [r0, #0x30]
	ADD      r1, r1, r4
	STR      r1, [r0, #4]
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r5, r0, #0
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001E60|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x70]
	STR      r4, [r0, #8]
	STR      r1, [r0]
	STR      r5, [r0, #0xc]
|loc_08001E60|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x4c]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
|loc_08001E68|
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4d82
	ADD      r1, r0, #0
	LDR      r0, [pc, #0xc]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	ADD      sp, #0xc
	POP      {pc}
|loc_08001EB0|
	DCW      0x4fbc
	DCW      0x0805,0xdeb4
|loc_08001EB6|
	LSR      r4, r0, #0x20
	STMIA    r4!, {r2, r3, r4, r5}
	LSR      r4, r0, #0x20
|unk_08001EBC|
	INCBIN	baserom.gba_0x1ebc_0x1ebe.extracted
	LSR      r4, r0, #0x20
	BLE      |loc_08001ED4|
	LSR      r4, r0, #0x20
	ADD      r3, sp, #0x160
	LSR      r4, r0, #0x20
	LDMIA    r5!, {r5, r6}
	LSR      r4, r0, #0x20
	BGT      |loc_08001E68|
	LSR      r4, r0, #0x20
	PUSH     {r4, lr}
	LDR      r1, [r0]
|loc_08001ED4|
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001EF2|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x270]
	STR      r4, [r0, #8]
	STR      r1, [r0]
|loc_08001EF2|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x26c]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001F22|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x248]
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_08001F22|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x23c]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001F52|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x21c]
	STR      r1, [r0]
	STR      r4, [r0, #8]
|loc_08001F52|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x20c]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0x10
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001F8E|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x1e8]
	STR      r1, [r0]
	STR      r4, [r0, #8]
	STR      r5, [r0, #0xc]
|loc_08001F8E|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x1d0]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r3, r4, r5, pc}
	PUSH     {r4, r5, r6, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r6, [r2, #4]
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r5, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r4, [r0, #4]
	MOV      r0, #0x14
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_08001FD6|
	MOV      r1, #0
	STR      r1, [r0, #4]
	LDR      r1, [pc, #0x1a4]
	STR      r1, [r0]
	ADD      r0, #8
	STMIA    r0!, {r4, r5, r6}
	SUB      r0, #0x14
|loc_08001FD6|
	ADD      r1, r0, #0
	LDR      r0, [pc, #0x188]
	ADD      r0, #0x1c
	LDMIA    r0!, {r0, r2}
	BL       |inc_0x153f2_0x1a3f2| + 0x3f78
	POP      {r4, r5, r6, pc}
	PUSH     {lr}
	LDR      r1, [r0]
	SUB      sp, #0xc
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r2, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r1, r1, r0
	LDR      r1, [r1, #4]
	STR      r1, [sp, #8]
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	ADD      r1, sp, #4
	STR      r0, [sp, #4]
	MOV      r0, #0
	BL       |inc_0x153f2_0x1a3f2| + 0x776
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      sp, #0xc
	POP      {pc}
	PUSH     {r4, lr}
	LDR      r1, [r0]
	SUB      sp, #0x20
	SUB      r1, #1
	LSL      r2, r1, #2
	STR      r1, [r0]
	ADD      r2, r2, r0
	LDR      r4, [r2, #4]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	ADD      r1, r0, #0
	ADD      r0, sp, #8
	BL       |sub_0800FDFA|
	LDR      r0, [sp, #8]
	LDR      r2, [sp, #0x10]
	LDR      r3, [sp, #0x14]
	ADD      r2, r0, r2
	LDR      r0, [sp, #0xc]
	STR      r2, [sp]
	ADD      r0, r0, r3
	STR      r0, [sp, #4]
	ASR      r0, r0, #1
	ASR      r2, r2, #1
	STR      r0, [sp, #4]
	STR      r0, [sp, #0x1c]
	ADD      r0, r2, #0
	SUB      r0, #0x78
	STR      r2, [sp, #0x18]
	STR      r0, [sp, #0x18]
	LDR      r0, [sp, #0x1c]
	STR      r2, [sp]
	SUB      r0, #0x50
	STR      r0, [sp, #0x1c]
	ADD      r2, r4, #0
	MOV      r0, #0
	ADD      r1, sp, #0x18
	BL       |inc_0x153f2_0x1a3f2| + 0x776
	BL       |inc_0x03d784_0x041118| + 0x11c
	ADD      sp, #0x20
	POP      {r4, pc}
	PUSH     {r3, r4, r5, lr}
	LDR      r1, [r0]
	SUB      r1, #1
	STR      r1, [r0]
	LSL      r1, r1, #2
	ADD      r0, r1, r0
	LDR      r0, [r0, #4]
	BL       |loc_080001C6|
	LDR      r5, [pc, #0xd0]
	ADD      r4, r0, #0
	LDR      r0, [r5, #0x24]
	ADD      r0, #0x80
	LDR      r0, [r0, #0x10]
	CMP      r0, #0
	BEQ      |sub_080020BE|
	MOV      r0, #0xc
	BL       |GBARam_Malloc|
	CMP      r0, #0
	BEQ      |loc_080020B4|
	LDR      r1, [pc, #0xcc]
	STMIA    r0!, {r1, r4}
	SUB      r0, #8
	MOV      r1, #0
	MVN      r1, r1
	STR      r1, [r0, #8]
|loc_080020B4|
	ADD      r1, r0, #0
	LDR      r0, [r5, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ca2
	POP      {r3, r4, r5, pc}
