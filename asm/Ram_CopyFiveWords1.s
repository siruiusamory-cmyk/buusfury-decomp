	CODE16
|Ram_CopyFiveWords1|
	PUSH     {r4, lr}
	LDR      r4, [pc, #0x64]
	LDMIA    r0!, {r1, r2, r3}
	STMIA    r4!, {r1, r2, r3}
	LDMIA    r0!, {r2, r3}
	STMIA    r4!, {r2, r3}
	LDR      r4, [pc, #0x58]
	LDR      r0, [r4, #0x20]
	BL       |inc_0x1c3f2_0x2ab4c| + 0x4ce4
	LDR      r0, [r4, #0xc]
	BL       |loc_080099B6|
	LDR      r0, [r4, #0x14]
	BL       |Object_Construct8|
	POP      {r4, pc}
