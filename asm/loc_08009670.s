	CODE16
|loc_08009670|
	PUSH     {r3, lr}
	ADD      r1, #0x40
	LDR      r0, [pc, #0x280]
	LDMIA    r1!, {r1, r2}
	LDR      r0, [r0, #8]
	BL       |loc_08012664|
	POP      {r3, pc}
	MOV      r1, #0
	ADD      r0, #0x80
	PUSH     {r3, lr}
	STR      r1, [r0, #0x10]
	LDR      r0, [pc, #0x26c]
	LDR      r0, [r0]
	BL       |Object_RebuildSlots1|
	POP      {r3, pc}
