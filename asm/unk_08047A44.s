	CODE16
|unk_08047A44|
; cited by 0x08047A88 (a pc-relative load targets 0x08047C8C)
	CODE32
	MOV      r2, #0
|arm_08047A48|
	CMP      r1, #4
	BLO      |arm_08047A74|
	ANDS     ip, r0, #3
	BEQ      |arm_08046CC4|
	RSB      ip, ip, #4
	CMP      ip, #2
	STRB     r2, [r0], #1
|arm_08047A64|
	DCD     0xA4C02001
|arm_08047A68|
	DCD     0xC4C02001
	SUB      r1, r1, ip
	B        |arm_08046CC4|
|arm_08047A74|
	MOVS     ip, r1, LSL #0x1f
|arm_08047A78|
	DCD     0x24C02001
|arm_08047A7C|
	DCD     0x24C02001
|arm_08047A80|
	DCD     0x44C02001
	BX       lr
|arm_08047A88|
	DCD     0xE92D4D80
	STMDB    sp!, {r2, r3, r4, r5, r6}
	BIC      r6, r1, #128, 8
	ADDS     ip, r6, #192, 8
	SUBGES   ip, ip, #0x4100000
	MOV      r5, r0
	MOV      r4, r1
	MOV      fp, r1
	BLT      |arm_08047AF8|
	ADDS     ip, r6, #144, 8
	SUBGES   ip, ip, #0xff00000
	BGT      |arm_08047AC4|
	BNE      |arm_08047AE4|
	CMP      r5, #0
	BEQ      |arm_08047AE4|
|arm_08047AC4|
	MOV      r3, r4
	MOV      r2, r5
	MOV      r1, r4
	MOV      r0, r5
	BL       |arm_080534A8|
|arm_08047AD8|
	LDMIA    sp!, {r2, r3, r4, r5, r6}
	LDMIA    sp!, {r7, r8, sl, fp, lr}
	BX       lr
|arm_08047AE4|
	ADD      r1, pc, #0x268
	CMP      fp, #0
	ADDLE    r1, pc, #0x268
	LDMIA    r1, {r0, r1}
	B        |arm_08047AD8|
|arm_08047AF8|
	ADDS     ip, r6, #196, 8
	SUBGES   ip, ip, #0x3dc0000
	ADD      r7, pc, #0x25c
	BGE      |arm_08047B44|
	ADDS     ip, r6, #208, 8
	SUBGES   ip, ip, #0xe200000
	BGE      |arm_08047B3C|
	ADD      r0, pc, #148, 30
	LDMIA    r0, {r2, r3}
	MOV      r0, r5
	MOV      r1, r4
	BL       |arm_080534A8|
	LDMIA    r7, {r2, r3}
	BL       |arm_08054058|
	MOVHI    r0, r5
	MOVHI    r1, r4
	BHI      |arm_08047AD8|
|arm_08047B3C|
	MVN      r6, #0
	B        |arm_08047C48|
|arm_08047B44|
	BIC      r1, r4, #128, 8
	MOV      r4, r5
	ADDS     ip, r6, #0xc1000000
	SUBGES   ip, ip, #0xf30000
	MOV      r5, r1
	BGE      |arm_08047BD8|
	ADDS     ip, r6, #0xc1000000
	SUBGES   ip, ip, #0xe60000
	BGE      |arm_08047BAC|
	ADD      r8, pc, #0x204
	LDMIA    r8, {r2, r3}
	MOV      r6, #0
	MOV      r1, r5
	MOV      r0, r4
	BL       |arm_08054160|
	LDMIA    r7, {r2, r3}
	BL       |arm_080536E0|
	MOV      r7, r0
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r8, {r2, r3}
	BL       |arm_080534A8|
	MOV      r3, sl
	MOV      r2, r7
	B        |arm_08047C3C|
|arm_08047BAC|
	MOV      r6, #1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r7, {r2, r3}
	BL       |arm_080536E0|
	MOV      r8, r0
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	LDMIA    r7, {r2, r3}
	B        |arm_08047C30|
|arm_08047BD8|
	ADDS     ip, r6, #192, 8
	SUBGES   ip, ip, #224, 22
	ADDGE    r0, pc, #0x194
|arm_08047BE4|
	DCD     0xA890000C
	MOVGE    r0, r4
	MOVGE    r6, #3
	MOVGE    r1, r5
	BGE      |arm_08047C3C|
	ADD      r0, pc, #0x184
	LDMIA    r0, {r2, r3}
	MOV      r0, r4
	MOV      r6, #2
	MOV      r1, r5
	BL       |arm_080536E0|
	MOV      r8, r0
	ADD      r0, pc, #0x168
	LDMIA    r0, {r2, r3}
	MOV      sl, r1
	MOV      r1, r5
	MOV      r0, r4
	BL       |arm_08054160|
	LDMIA    r7, {r2, r3}
|arm_08047C30|
	BL       |arm_080534A8|
	MOV      r3, sl
	MOV      r2, r8
|arm_08047C3C|
	BL       |arm_08053A20|
	MOV      r5, r0
	MOV      r4, r1
|arm_08047C48|
	MOV      r3, r4
	MOV      r2, r5
	MOV      r1, r4
	MOV      r0, r5
	BL       |arm_08054160|
	MOV      sl, r0
	STR      r1, [sp]
	MOV      r3, r1
	MOV      r2, r0
	BL       |arm_08054160|
	MOV      r7, r0
	MOV      r2, r0
	LDR      r0, [pc, #0x10c]
	MOV      r8, r1
	MOV      r3, r1
	MOV      r1, #6
	ADD      r0, pc, r0
	BL       |arm_08047D9C|
	MOV      r2, sl
	LDR      r3, [sp]
	BL       |arm_08054160|
	MOV      sl, r0
	LDR      r0, [pc, #0xe8]
	STR      r1, [sp, #4]
	MOV      r1, #5
	MOV      r3, r8
	MOV      r2, r7
	ADD      r0, pc, r0
	BL       |arm_08047D9C|
	MOV      r3, r8
	MOV      r2, r7
	BL       |arm_08054160|
	MOV      r3, r1
	MOV      r2, r0
	MOV      r0, sl
	LDR      r1, [sp, #4]
	CMP      r6, #0
	BGE      |arm_08047D00|
	BL       |arm_080534A8|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08054160|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08053698|
	B        |arm_08047AD8|
|arm_08047D00|
	BL       |arm_080534A8|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_08054160|
	LDR      r2, [pc, #0x7c]
	ADD      r2, pc, r2
	ADD      r2, r2, r6, lsl #3
	LDMIA    r2, {r2, r3}
	BL       |arm_080536E0|
	MOV      r3, r4
	MOV      r2, r5
	BL       |arm_080536E0|
	LDR      r2, [pc, #0x60]
	ADD      r2, pc, r2
	ADD      r2, r2, r6, lsl #3
	LDMIA    r2, {r2, r3}
	BL       |arm_08053698|
	CMP      fp, #0
	EORLT    r1, r1, #128, 8
	BLT      |arm_08047AD8|
	B        |arm_08047AD8|
|arm_08047D54|
	DCD     0x54442D18
|arm_08047D58|
	DCD     0x3FF921FB
|arm_08047D5C|
	DCD     0x54442D18
|arm_08047D60|
	DCD     0xBFF921FB
	ANDEQ    r0, r0, r0
|arm_08047D68|
	DCD     0x3FF00000
|arm_08047D6C|
	DCD     0x8800759C
|arm_08047D70|
	DCD     0x7E37E43C
	ANDEQ    r0, r0, r0
	ANDMI    r0, r0, r0
	ANDEQ    r0, r0, r0
|arm_08047D80|
	DCD     0xBFF00000
	ANDEQ    r0, r0, r0
|arm_08047D88|
	DCD     0x3FF80000
	RSBEQS   pc, r6, r0, ror fp
	RSBEQS   pc, r6, ip, lsl fp
|arm_08047D94|
	DCD     0x0076FA9C
|arm_08047D98|
	DCD     0x0076FA5C
|arm_08047D9C|
	DCD     0xE92D40F0
|arm_08047DA0|
	DCD     0xE2414001
|arm_08047DA4|
	DCD     0xE0801184
|arm_08047DA8|
	DCD     0xE52D3004
|arm_08047DAC|
	DCD     0xE1A05000
|arm_08047DB0|
	DCD     0xE8910003
|arm_08047DB4|
	DCD     0xE3540008
|arm_08047DB8|
	DCD     0xE1A07003
|arm_08047DBC|
	DCD     0xE1A06002
|arm_08047DC0|
	DCD     0x908FF104
|arm_08047DC4|
	DCD     0xEA00000F
|arm_08047DC8|
	DCD     0xEA00000E
|arm_08047DCC|
	DCD     0xEA000040
|arm_08047DD0|
	DCD     0xEA000038
|arm_08047DD4|
	DCD     0xEA000030
|arm_08047DD8|
	DCD     0xEA000028
|arm_08047DDC|
	DCD     0xEA000020
|arm_08047DE0|
	DCD     0xEA000018
|arm_08047DE4|
	DCD     0xEA000010
|arm_08047DE8|
	DCD     0xEA000008
|arm_08047DEC|
	DCD     0xE1A03007
|arm_08047DF0|
	DCD     0xE1A02006
|arm_08047DF4|
	DCD     0xEB0030D9
|arm_08047DF8|
	DCD     0xE2444001
|arm_08047DFC|
	DCD     0xE0852184
|arm_08047E00|
	DCD     0xE892000C
|arm_08047E04|
	DCD     0xEB002DA7
|arm_08047E08|
	DCD     0xE3540008
|arm_08047E0C|
	DCD     0xCAFFFFF6
|arm_08047E10|
	DCD     0xE1A03007
|arm_08047E14|
	DCD     0xE1A02006
|arm_08047E18|
	DCD     0xEB0030D0
|arm_08047E1C|
	DCD     0xE2444001
|arm_08047E20|
	DCD     0xE0852184
|arm_08047E24|
	DCD     0xE892000C
|arm_08047E28|
	DCD     0xEB002D9E
|arm_08047E2C|
	DCD     0xE1A03007
|arm_08047E30|
	DCD     0xE1A02006
|arm_08047E34|
	DCD     0xEB0030C9
|arm_08047E38|
	DCD     0xE2444001
|arm_08047E3C|
	DCD     0xE0852184
|arm_08047E40|
	DCD     0xE892000C
|arm_08047E44|
	DCD     0xEB002D97
|arm_08047E48|
	DCD     0xE1A03007
|arm_08047E4C|
	DCD     0xE1A02006
|arm_08047E50|
	DCD     0xEB0030C2
|arm_08047E54|
	DCD     0xE2444001
|arm_08047E58|
	DCD     0xE0852184
|arm_08047E5C|
	DCD     0xE892000C
|arm_08047E60|
	DCD     0xEB002D90
|arm_08047E64|
	DCD     0xE1A03007
|arm_08047E68|
	DCD     0xE1A02006
|arm_08047E6C|
	DCD     0xEB0030BB
|arm_08047E70|
	DCD     0xE2444001
|arm_08047E74|
	DCD     0xE0852184
|arm_08047E78|
	DCD     0xE892000C
|arm_08047E7C|
	DCD     0xEB002D89
|arm_08047E80|
	DCD     0xE1A03007
|arm_08047E84|
	DCD     0xE1A02006
|arm_08047E88|
	DCD     0xEB0030B4
|arm_08047E8C|
	DCD     0xE2444001
|arm_08047E90|
	DCD     0xE0852184
|arm_08047E94|
	DCD     0xE892000C
|arm_08047E98|
	DCD     0xEB002D82
|arm_08047E9C|
	DCD     0xE1A03007
|arm_08047EA0|
	DCD     0xE1A02006
|arm_08047EA4|
	DCD     0xEB0030AD
|arm_08047EA8|
	DCD     0xE2444001
|arm_08047EAC|
	DCD     0xE0852184
|arm_08047EB0|
	DCD     0xE892000C
|arm_08047EB4|
	DCD     0xEB002D7B
|arm_08047EB8|
	DCD     0xE1A03007
|arm_08047EBC|
	DCD     0xE1A02006
|arm_08047EC0|
	DCD     0xEB0030A6
|arm_08047EC4|
	DCD     0xE2444001
|arm_08047EC8|
	DCD     0xE0852184
|arm_08047ECC|
	DCD     0xE892000C
|arm_08047ED0|
	DCD     0xEB002D74
|arm_08047ED4|
	DCD     0xE1A03007
|arm_08047ED8|
	DCD     0xE1A02006
|arm_08047EDC|
	DCD     0xEB00309F
|arm_08047EE0|
	DCD     0xE2442001
|arm_08047EE4|
	DCD     0xE0852182
|arm_08047EE8|
	DCD     0xE892000C
|arm_08047EEC|
	DCD     0xE28DD004
|arm_08047EF0|
	DCD     0xE8BD40F0
|arm_08047EF4|
	DCD     0xEA002D6B
|arm_08047EF8|
	DCD     0xE92D4038
|arm_08047EFC|
	DCD     0xE2603000
|arm_08047F00|
	DCD     0xE1803003
|arm_08047F04|
	DCD     0xE3C12480
|arm_08047F08|
	DCD     0xE1822FA3
|arm_08047F0C|
	DCD     0xE26226FF
|arm_08047F10|
	DCD     0xE2822470
|arm_08047F14|
	DCD     0xE1B02FA2
|arm_08047F18|
	DCD     0xE1A05001
|arm_08047F1C|
	DCD     0xE1A04000
|arm_08047F20|
	DCD     0x1A000009
|arm_08047F24|
	DCD     0xE28F2030
|arm_08047F28|
	DCD     0xE892000C
|arm_08047F2C|
	DCD     0xEB00306A
|arm_08047F30|
	DCD     0x2A000005
|arm_08047F34|
	DCD     0xE3A00001
|arm_08047F38|
	DCD     0xEB0004A3
|arm_08047F3C|
	DCD     0xE28F1020
|arm_08047F40|
	DCD     0xE8910003
|arm_08047F44|
	DCD     0xE8BD4038
|arm_08047F48|
	DCD     0xE12FFF1E
|arm_08047F4C|
	DCD     0xE1A01005
|arm_08047F50|
	DCD     0xE1A00004
|arm_08047F54|
	DCD     0xEB003131
|arm_08047F58|
	DCD     0xEAFFFFF9
	CODE16
	CODE16
	EXPORT |sub_08047F5C|
	EXPORT |loc_08047F84|
	EXPORT |sub_08047F94|
	EXPORT |__16__user_libspace|
