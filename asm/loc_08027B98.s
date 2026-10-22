	CODE16
|loc_08027B98|
	CMP      r0, r1
	BLE      |loc_08027BA8|
	MOV      r3, #3
	CMP      r2, #0
	BGT      |loc_08027BA4|
	MOV      r3, #2
|loc_08027BA4|
	ADD      r0, r3, #0
	B        |loc_08027BB0|
|loc_08027BA8|
	MOV      r0, #1
	CMP      r3, #0
	BLE      |loc_08027BB0|
	MOV      r0, #0
|loc_08027BB0|
	ADD      r3, r0, #0
	ADD      r2, r6, #0
	ADD      r1, r7, #0
	MOV      r0, #0
	BL       |loc_08027CBC|
	ADD      r1, r0, #0
	STR      r0, [r4, #0x18]
	LDR      r0, [pc, #0x68]
	LDR      r0, [r0]
	BL       |inc_0x0158_0x143f2| + 0x117c2
	ADD      sp, #0x1c
	POP      {r4, r5, r6, r7, pc}
|sub_08027BCC|
|unk_08027BCC|
		BX       lr
