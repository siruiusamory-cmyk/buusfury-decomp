	CODE16
|sub_0804F4C8|
	PUSH     {r4, lr}
	ADD      r4, r0, #0
	LDR      r0, [r0, #4]
	CMP      r0, #0
	BEQ      |loc_0804F4DC|
	LDR      r1, [r0]
	LDR      r2, [r1]
	ADD      r1, r2, r1
	BL       |inc_0x046118_0x049114| + 0x98a
|loc_0804F4DC|
	ADD      r0, r4, #0
	BL       |GBARam_Free|
	POP      {r4, pc}
|sub_0804F4E4|
|unk_0804F4E4|
		BX       lr
|sub_0804F4E6|
	DCW      0x0000
