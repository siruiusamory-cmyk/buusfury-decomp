	CODE16
|sub_08051902|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xd898
	CMP      r5, #0
	BEQ      |loc_0805191A|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_0805191A|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051936|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051936|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051944|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051944|
	POP      {r3, r4, r5, pc}
|loc_08051946|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x3a18,0x0875,0xe454
|loc_08051956|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051972|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051972|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051980|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051980|
	POP      {r3, r4, r5, pc}
|loc_08051982|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x2f8c,0x0875,0xe454
|loc_08051992|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080519AE|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080519AE|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080519BC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080519BC|
	POP      {r3, r4, r5, pc}
|loc_080519BE|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x9c34,0x0871,0xe454
|loc_080519CE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_080519EA|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_080519EA|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_080519F8|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_080519F8|
	POP      {r3, r4, r5, pc}
|loc_080519FA|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x033c,0x0872,0xe454
|loc_08051A0A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051A26|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0, #4]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051A26|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051A34|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051A34|
	POP      {r3, r4, r5, pc}
|loc_08051A36|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0xba78,0x0876,0xe454
|loc_08051A46|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x38]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDR      r1, [r4, #0x14]
	MOV      r0, #0
	STR      r0, [r1, #0x2c]
	ADD      r0, r4, #0
	MOV      r1, #0
	ADD      r0, #0x18
	BL       |inc_0x03d784_0x041118| + 0x1e08
	LDR      r0, [pc, #0x28]
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x24]
	CMP      r1, r0
	BEQ      |loc_08051A76|
	LDR      r0, [pc, #0x24]
	LDR      r0, [r0, #8]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051A76|
	LDR      r0, [pc, #0x20]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051A84|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051A84|
	POP      {r3, r4, r5, pc}
|loc_08051A86|
	DCW      0x0000
	DCW      0xb4d8,0x0804,0x9680,0x0804,0xffff,0x0000,0x1c90,0x0807
	DCW      0xe454
|loc_08051A9A|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0xb75a
	CMP      r5, #0
	BEQ      |loc_08051AB2|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051AB2|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [pc, #0x24]
	ADD      r5, r1, #0
	STR      r0, [r4]
	LDRH     r1, [r4, #0xc]
	LDR      r0, [pc, #0x20]
	CMP      r1, r0
	BEQ      |loc_08051ACE|
	LDR      r0, [pc, #0x20]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x112d2
|loc_08051ACE|
	LDR      r0, [pc, #0x1c]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051ADC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051ADC|
	POP      {r3, r4, r5, pc}
|loc_08051ADE|
	DCW      0x0000
	DCW      0x9680,0x0804,0xffff,0x0000,0x2480,0x0807,0xe454
|loc_08051AEE|
	LSR      r4, r0, #0x20
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	ADD      r5, r1, #0
	MOV      r1, #0
	BL       |inc_0x0158_0x143f2| + 0x64c0
	CMP      r5, #0
	BEQ      |loc_08051B06|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051B06|
	POP      {r3, r4, r5, pc}
	PUSH     {r3, r4, r5, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #0xc]
	ADD      r5, r1, #0
	BL       |inc_0x0158_0x143f2| + 0x10c42
	LDR      r0, [pc, #0xc]
	CMP      r5, #0
	STR      r0, [r4]
	BEQ      |loc_08051B22|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
|loc_08051B22|
	POP      {r3, r4, r5, pc}
|sub_08051B24|
|unk_08051B24|
	INCBIN	baserom.gba_0x51b24_0x51b26.extracted
