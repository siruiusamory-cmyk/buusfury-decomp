# Friend v3 playtest: romhack checklist

Speedrun checklist for what this hack changes. Retail behaviour is not listed. The full
chapter list is `FRIEND_V3_PLAYTEST_CHAPTERS.md`; status and evidence for every item are in
`FRIEND_V3_TRACKER.md`.

## Before the run

- [ ] ROM hash is `acd98c2ac90907ae0d83e78019c19b9b26001a49bc28e8bd436da7be9b4bb48c`
      (`(Get-FileHash <rom> -Algorithm SHA256).Hash.ToLower()`); 10,140,972 bytes
- [ ] save type EEPROM or Flash 128K; the Grand Kai must not show `The game will not run on this hardware`
      ([Almar's Guides](https://almarsguides.com/retro/walkthroughs/GBA/games/DragonBallZBuusFury/))
- [ ] New Game from an empty save (delete the `.sav`); never load a save from another build

## Names to expect

| retail | shows as |
| --- | --- |
| Goku | Yamcha |
| Gohan | Krillin |
| Krillin | Goku |
| Goten | Videl |
| Trunks | Uub |
| Vegeta | Tien |
| Chi-Chi | Bulma |
| Bulma | Tulma |
| Android 18 | Chi-Chi |
| Gogeta | Yamien |
| Vegito | Tiencha |
| Great Saiyaman | Great Soyman |

Piccolo unchanged; no rename recorded for Hercule or Gotenks. Report a defect by retail name.

## Boosted characters: Yamcha, Krillin, Videl, Uub, Tien (retail Goku, Gohan, Goten, Trunks, Vegeta)

| check | Yamcha | Krillin | Videl | Uub | Tien |
| --- | --- | --- | --- | --- | --- |
| stat screen: LVL 200 | [ ] | [ ] | [ ] | [ ] | [ ] |
| STR, POW, END, SPD all 255 | [ ] | [ ] | [ ] | [ ] | [ ] |
| HP and EP positive, normal size | [ ] | [ ] | [ ] | [ ] | [ ] |
| an energy attack fires | [ ] | [ ] | [ ] | [ ] | [ ] |
| switch to them and back: stats unchanged | [ ] | [ ] | [ ] | [ ] | [ ] |

- [ ] first experience gain at level 200 does not break the stat screen or freeze
- [ ] fusions (Gotenks, Tiencha, Yamien) work; weaker than the boosted five is expected

## Level gates (boosted character should pass)

- [ ] chapter 1: gate 65 (Grand Kai's planet, after Olibu)
- [ ] chapter 3: Yamcha's forest gate to Videl (East District 439)
- [ ] chapter 4: Yamcha's Southwest Forest gate; Tien's level 120 door
- [ ] chapter 6: Uub's level 80 gate (Thieves Den)
- [ ] any gate that refuses: note chapter, place, level shown

## Tulma

- [ ] chapter 2, West City, Tulma's house: Tulma art and portrait, not retail Bulma
- [ ] chapter 3, tournament registration: Bulma says `Look at how mad Tulma is! Do you think I went too far this time?`
- [ ] same scene: Tulma says `That bitch! She knew I was going to wear this!`
- [ ] lines in the right mouths, no stray spaces or cut text
- [ ] chapter 6, West City: Tulma hands over the Dragon Radar
- [ ] Tulma scan: twin sister of Bulma, daughter of Dr. Brief, no marriage line

## Text

- [ ] chapter 2 title and lines read `Great Soyman`, never `Saiyaman`
- [ ] chapter 3, Kibito scene: line names `Krillin`, scene plays through, no freeze
- [ ] chapter 3, tournament grounds (map 134): no crash
- [ ] chapter 5 title reads `Majin Tien`
- [ ] quest log and Capsule Corp text say `Tulma`, not `Bulma`, where retail meant Bulma
- [ ] no name shows as dots or odd glyphs
- [ ] chapter 12 credits include `Cale Aaron Cymek`

## Save and stability

- [ ] save, quit, reload: progress, stats and inventory intact
- [ ] no crash, freeze or softlock through chapter 12

## Not bugs

- no Bandana at the start: removed on purpose, get it in play
- a save from another build showing retail stats
- fusions weaker than the boosted five

## Bug report

1. ROM hash (first 8 characters)
2. fresh save: yes or no
3. chapter, place, fight
4. what you did just before
5. what the screen showed (screenshot if visual)
6. kept running, froze, or closed
7. reproduced twice from a fresh save: yes or no
