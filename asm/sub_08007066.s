	CODE16
|sub_08007066|
	PUSH     {r3, lr}
	LDR      r0, [r0, #4]
	BL       |List_ReleaseAll2|
	POP      {r3, pc}
|loc_08007070|
	DCW      0x01a0
	DCW      0x0807
