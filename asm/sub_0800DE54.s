	CODE16
|sub_0800DE54|
	PUSH     {r3, lr}
	BL       |GBARam_Free|
	POP      {r3, pc}
	MOV      r5, #0xac
	LSR      r7, r0, #0x20
