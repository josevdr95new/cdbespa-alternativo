<div align="center">

# 🃏 CDB Español Alternativo

**Cartas en Español para EDOPro con nombres en inglés**

*Serie Español-Alternativo*

</div>

---

## ⚙️ Configuración

Añade este bloque a tu `user_configs.json`:

```json
{
    "url": "https://github.com/josevdr95new/cdbespa-alternativo",
    "repo_name": "josevdr95 cdbespa-alternativo",
    "repo_path": "./config/languages/Español-Alternativo",
    "should_update": true,
    "should_read": true
}
```

---

Creado con [CDBtext_migrator](https://github.com/josevdr95new/CDBtext_migrator)

<!-- STATS:START -->
## 📊 Estadísticas

![Visitas](https://img.shields.io/badge/Visitas-22-blue) ![Visitantes únicos](https://img.shields.io/badge/Visitantes_únicos-7-brightgreen) ![Clonaciones](https://img.shields.io/badge/Clonaciones-10-green) ![Stars](https://img.shields.io/badge/⭐_Stars-5-ff69b4) ![Forks](https://img.shields.io/badge/Forks-0-orange) ![Watchers](https://img.shields.io/badge/Watchers-1-9cf)

| Métrica | Total | Únicos |
|---------|------:|-------:|
| 👁️ Visitas | **22** | **7** |
| 🌀 Clonaciones | **10** | **9** |
| ⭐ Stars | **5** | — |
| 🍴 Forks | **0** | — |
| 👀 Watchers | **1** | — |

<sub>Actualizado: 2026-07-17 · Registro desde: 2026-07-02</sub>

<!-- STATS:END -->

<!-- MIGRATE_LOG:START -->
## 🔄 Log de migración

<sub>Última verificación: **2026-07-17 12:08 UTC**</sub>

**Condición:** nombres en inglés · efectos en español · texto en `""` en inglés

**Fuentes:**
- `ProjectIgnis/BabelCDB` @ `9c962bb`
- `Team13fr/IgnisMulti` @ `d438822`

### Estado por archivo

| Archivo | Cartas EN | Traducidas ES | ✅ OK | 🔧 Corregidas | ❌ Sin trad. ES |
|---------|----------:|--------------:|------:|--------------:|----------------:|
| `cards-rush.cdb` | 3398 | 3194 | 3070 | **124** | **204** |
| `cards-skills-unofficial.cdb` | 19 | 19 | 19 | 0 | 0 |
| `cards-skills.cdb` | 208 | 208 | 208 | 0 | 0 |
| `cards-unofficial.cdb` | 5878 | 5876 | 5749 | **123** | **2** |
| `cards.cdb` | 14578 | 14336 | 1323 | **13006** | **242** |
| `goat-entries.cdb` | 191 | 191 | 191 | 0 | 0 |
| `prerelease-cards-rush.cdb` | 39 | 0 | 0 | 0 | **39** |
| `prerelease-others.cdb` | 12 | 0 | 0 | 0 | **12** |
| `prerelease-cori.cdb` | — | — | — | — | 📋 solo español, actualizado |
| `prerelease-loch.cdb` | — | — | — | — | 📋 solo español, actualizado |
| `prerelease-locr.cdb` | — | — | — | — | 📋 solo español, actualizado |
| `prerelease-mzmu.cdb` | — | — | — | — | 📋 solo español, actualizado |
| `release-blzd.cdb` | — | — | — | — | 📋 solo español, actualizado |
| `prerelease-betb.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| `prerelease-cori-en.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| `prerelease-dbgv.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| `prerelease-lpg2.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| `prerelease-rv01.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| `release-cori.cdb` | — | — | — | — | 📋 solo inglés, copiado |
| **Total** | **24323** | **23824** | **10560** | **13253** | **499** |

<sub>**Cartas EN** = total en BabelCDB · **Traducidas ES** = también en IgnisMulti/Español · **✅ OK** = ya cumplen condición · **🔧 Corregidas** = aplicadas esta ejecución · **❌ Sin trad. ES** = no existen en la DB española aún</sub>

### 🔧 Cartas corregidas

**`cards-rush.cdb`** (124 cartas)

| ID | Nombre | Campo | Antes → Después |
|--:|--------|-------|-----------------|
| 160005037 | Coil Dragon of the Fertile Land | name | `Coiled Dragon of Fertility` → `Coil Dragon of the Fertile Land` |
| 160006061 | Backup Barrage | name | `Covering Barrage` → `Backup Barrage` |
| 160007009 | Medley the Elite Noodle Ninja | name | `Cross Promotion the Elite Noodle Ni` → `Medley the Elite Noodle Ninja` |
| 160007029 | Reporter Raccoon | str1 | `Add 1 "Delivery Machine Whirr" or 1` → `Add 1 "Scoop Shooter" or 1 "Soul of` |
| 160007038 | Extra Meat the Special Noodle Ninja | name | `Meat Spice the Special Noodle Ninja` → `Extra Meat the Special Noodle Ninja` |
| 160007039 | Instant Miso the Special Noodle Ninja | name | `Miso Instant the Special Noodle Nin` → `Instant Miso the Special Noodle Nin` |
| 160007039 | Instant Miso the Special Noodle Ninja | desc | `"Cross Promotion the Elite Noodle N` → `"Medley the Elite Noodle Ninja" + "` |
| 160008013 | Excutie Feena | name | `Executie Feena` → `Excutie Feena` |
| 160008015 | Mecha Umbretta | name | `Mecha Ambulator` → `Mecha Umbretta` |
| 160009033 | Excutie Phermi | name | `Executie Phermi` → `Excutie Phermi` |
| 160009052 | Excutie Power Up! | name | `Executie Up!` → `Excutie Power Up!` |
| 160009052 | Excutie Power Up! | str1 | `Tribute Summon ("Excutie Up!")` → `Tribute Summon ("Excutie Power Up!"` |
| 160009065 | Sacred Tower in Crisis | name | `Crisis at the Sacred Tower` → `Sacred Tower in Crisis` |
| 160011042 | Qwerty Keyblade | name | `QWERTY Keyblade` → `Qwerty Keyblade` |
| 160012019 | Excutie Flame | name | `Executie Flame` → `Excutie Flame` |
| 160012020 | Soleil, the Fairy of Skysavior | name | `Soleil the Skysavior Angel` → `Soleil, the Fairy of Skysavior` |
| 160012020 | Soleil, the Fairy of Skysavior | desc | `[REQUIREMENT] Reveal 1 Warrior Typ` → `[REQUIREMENT] Reveal 1 Warrior Typ` |
| 160012021 | Lua, the Fairy of Skysavior | name | `Lua the Skysavior Angel` → `Lua, the Fairy of Skysavior` |
| 160012021 | Lua, the Fairy of Skysavior | desc | `[REQUIREMENT] Reveal 1 Warrior Typ` → `[REQUIREMENT] Reveal 1 Warrior Typ` |
| 160012022 | Langa, the Knight of Skysavior | name | `Ranga the Skysavior Knight` → `Langa, the Knight of Skysavior` |
| 160012022 | Langa, the Knight of Skysavior | desc | `[REQUIREMENT] During the turn you ` → `[REQUIREMENT] During the turn you ` |
| 160012023 | Sael, the Knight of Skysavior | name | `Seir the Skysavior Knight` → `Sael, the Knight of Skysavior` |
| 160012024 | Ciela, the Knight of Skysavior | name | `Ciela the Skysavior Knight` → `Ciela, the Knight of Skysavior` |
| 160012025 | Dankus, the Knight of Skysavior | name | `Dunkes the Skysavior Knight` → `Dankus, the Knight of Skysavior` |
| 160012038 | Solciere, the Radiant Skysavior | name | `Solcier the Skysavior Lightflash` → `Solciere, the Radiant Skysavior` |
| 160012038 | Solciere, the Radiant Skysavior | desc | `"Ciela the Skysavior Knight" + "Sol` → `"Ciela, the Knight of Skysavior" + ` |
| | *...y 104 cartas más* | | Ver detalle en [`MIGRATE_LOG.md`](MIGRATE_LOG.md) |

**`cards-unofficial.cdb`** (123 cartas)

| ID | Nombre | Campo | Antes → Después |
|--:|--------|-------|-----------------|
| 100000000 | Chaos End Ruler - Ruler of the Beginning | name | `Chaos End Ruler - Ruler of the Begi` → `Chaos End Ruler - Ruler of the Begi` |
| 100000078 | Quick Summon (Anime) - TBR | name | `Quick Summon` → `Quick Summon (Anime) - TBR` |
| 100000083 | Illusion Gate (VG) | name | `Illusion Gate` → `Illusion Gate (VG)` |
| 100000090 | Malefic Force (VG) | name | `Malefic Force` → `Malefic Force (VG)` |
| 100000092 | Malefic Paradigm Shift (Anime) | name | `Malefic Paradigm Shift` → `Malefic Paradigm Shift (Anime)` |
| 100000106 | Arcana Force XII - The Hangman (VG) | name | `Arcana Force XII - The Hangman` → `Arcana Force XII - The Hangman (VG)` |
| 100000139 | Maiden in Love (VG) | name | `Maiden in Love` → `Maiden in Love (VG)` |
| 100000264 | Fallen Angel in Darkness (Manga) | name | `Fallen Angel in Darkness` → `Fallen Angel in Darkness (Manga)` |
| 100000316 | Last Tusk Mammoth (Anime) | name | `Last Tusk Mammoth` → `Last Tusk Mammoth (Anime)` |
| 100000330 | Fairy Tale Prologue: Journey's Dawn (Man | name | `Fairy Tale Prologue: Journey's Dawn` → `Fairy Tale Prologue: Journey's Dawn` |
| 100000330 | Fairy Tale Prologue: Journey's Dawn (Man | str1 | `Please choose a "Fairy Tale Second ` → `Please choose a "Fairy Tale Chapter` |
| 100000340 | Bat, The Forest Ninja (Manga) | name | `Bat, The Forest Ninja` → `Bat, The Forest Ninja (Manga)` |
| 100000343 | Wonko, Noble Knight of the Forest (Manga | name | `Wonko, Noble Knight of the Forest` → `Wonko, Noble Knight of the Forest (` |
| 100000539 | Rainbow Bridge Bifrost (Anime) | name | `Rainbow Bridge Bifrost` → `Rainbow Bridge Bifrost (Anime)` |
| 100000650 | Chaos Distill (VG/TBR) | name | `Chaos Distill (VG)` → `Chaos Distill (VG/TBR)` |
| 100001005 | Long-Tailed Black Horse (Manga) | name | `Long-Tailed Black Horse` → `Long-Tailed Black Horse (Manga)` |
| 100001008 | Plasma Warrior Eitom (VG) | name | `Plasma Warrior Eitom` → `Plasma Warrior Eitom (VG)` |
| 100100090 | Gate Blocker (Anime) | name | `Gate Blocker` → `Gate Blocker (Anime)` |
| 170000207 | Backup Gardna (Anime) | name | `Backup Gardna` → `Backup Gardna (Anime)` |
| 344000001 | Garbage Ogre (Anime) | name | `Garbage Ogre` → `Garbage Ogre (Anime)` |
| 500000006 | Ancient Gear Statue (Anime) | name | `Ancient Gear Statue` → `Ancient Gear Statue (Anime)` |
| | *...y 103 cartas más* | | Ver detalle en [`MIGRATE_LOG.md`](MIGRATE_LOG.md) |

**`cards.cdb`** (13006 cartas)

| ID | Nombre | Campo | Antes → Después |
|--:|--------|-------|-----------------|
| 483 | Parallel Teleport | name | `Teleportación Paralela` → `Parallel Teleport` |
| 483 | Parallel Teleport | desc | `Sacrifica 1 monstruo Psíquico con u` → `Sacrifica 1 monstruo Psíquico con u` |
| 2511 | Labrynth Cooclock | name | `Reloj Cucú del Labrislinto` → `Labrynth Cooclock` |
| 2511 | Labrynth Cooclock | desc | `(Efecto Rápido): puedes descartar e` → `(Efecto Rápido): puedes descartar e` |
| 10000 | Ten Thousand Dragon | name | `Dragón Diez Mil` → `Ten Thousand Dragon` |
| 27551 | Limit Reverse | name | `Invertir el Límite` → `Limit Reverse` |
| 32864 | The 13th Grave | name | `El Decimotercer Sepulcro` → `The 13th Grave` |
| 35699 | SPYRAL Sleeper | name | `Agente Encubierto E.S.P.I.R.A.L.` → `SPYRAL Sleeper` |
| 35699 | SPYRAL Sleeper | desc | `No puede ser Invocado de Modo Norma` → `No puede ser Invocado de Modo Norma` |
| 39015 | Assault Sentinel | name | `Centinela de Ataque` → `Assault Sentinel` |
| 39015 | Assault Sentinel | desc | `Puedes Sacrificar esta carta; Invoc` → `Puedes Sacrificar esta carta; Invoc` |
| 41546 | D/D Savant Thomas | name | `D/D Thomas el Sabio` → `D/D Savant Thomas` |
| 41546 | D/D Savant Thomas | desc | `[ Monstruo de Efecto ]  Puedes sele` → `[ Monstruo de Efecto ]  Puedes sele` |
| 41777 | Gem-Enhancement | name | `Gema-Mejora` → `Gem-Enhancement` |
| 41777 | Gem-Enhancement | desc | `Sacrifica 1 monstruo "Caballero-Gem` → `Sacrifica 1 monstruo "Gem-Knight", ` |
| 43227 | Magnum the Reliever | name | `Mágnum el Suplente` → `Magnum the Reliever` |
| 43227 | Magnum the Reliever | desc | `1 monstruo Invocado de Modo Especia` → `1 monstruo Invocado de Modo Especia` |
| 44818 | Starry Knight Orbitael | name | `Cabalnoche de Estrellas Orbitael` → `Starry Knight Orbitael` |
| 44818 | Starry Knight Orbitael | desc | `(Efecto Rápido): puedes seleccionar` → `(Efecto Rápido): puedes seleccionar` |
| 50755 | Magician's Circle | name | `Círculo del Mago` → `Magician's Circle` |
| 56889 | Cross-Dimensional Duel | name | `Duelo Interdimensional` → `Cross-Dimensional Duel` |
| 56889 | Cross-Dimensional Duel | desc | `Selecciona 1 monstruo "Mecanismo An` → `Selecciona 1 monstruo "Ancient Gear` |
| 59080 | Magia Magic - Thunder of Judgment | name | `Magia Hechizo - Trueno del Juicio` → `Magia Magic - Thunder of Judgment` |
| 59080 | Magia Magic - Thunder of Judgment | desc | `(Esta carta se trata siempre como u` → `(Esta carta se trata siempre como u` |
| 62121 | Castle of Dark Illusions | name | `Castillo de las Ilusiones Oscuras` → `Castle of Dark Illusions` |
| 98905 | Cipher Spectrum | name | `Espectro Cifrado` → `Cipher Spectrum` |
| 98905 | Cipher Spectrum | desc | `Si uno o más Monstruos Xyz "Cifrado` → `Si uno o más Monstruos Xyz "Cipher"` |
| 102380 | Lava Golem | name | `Golem de Lava` → `Lava Golem` |
| 109401 | Dark Dimension Soldier | name | `Soldado de la Dimensión Oscura` → `Dark Dimension Soldier` |
| 109401 | Dark Dimension Soldier | desc | `1 Cantante + 1+ monstruos que no se` → `1 Cantante + 1+ monstruos que no se` |
| 111280 | Dark Magic Expanded | name | `Magia Oscura Expandida` → `Dark Magic Expanded` |
| 111280 | Dark Magic Expanded | desc | `Aplica estos efectos en orden, basá` → `Aplica estos efectos en orden, basá` |
| 114932 | Seismic Crasher | name | `Aplastador Sísmico` → `Seismic Crasher` |
| | *...y 12986 cartas más* | | Ver detalle en [`MIGRATE_LOG.md`](MIGRATE_LOG.md) |

### ❌ Cartas sin traducción española

Estas cartas existen en BabelCDB (inglés) pero no en IgnisMulti/Español. Se incluirán automáticamente cuando se traduzcan.

**`cards-rush.cdb`** (204 cartas)

| ID | Nombre (EN) |
|--:|-------------|
| 160025001 | Galactica Oblivion |
| 160025002 | Harpie Lady (Rush) |
| 160025003 | Enceladustellime |
| 160025004 | Civil Twirider |
| 160025005 | Vanishing Solitius |
| 160025006 | Vanishing Sopdet |
| 160025007 | Reporter Wars Scoopies [L] |
| 160025008 | Reporter Wars Scoopies |
| 160025009 | Reporter Wars Scoopies [R] |
| 160025010 | Reporter Recorder |
| 160025011 | Reporter Lilim |
| 160025012 | High-Speed Machine ENG |
| 160025013 | Rampaging Machine Headhorn |
| 160025014 | Premium Printing Presser |
| 160025015 | Lightclad Dragon - Llates |
| 160025016 | Stella the Clad Dragon Researcher |
| 160025017 | Shannah the Clad Dragon Researcher |
| 160025018 | Astel the Clad Dragon Researcher |
| 160025019 | Infernoclad Dragon - Flagal |
| 160025020 | Verdantclad Dragon - Greeray |
| 160025021 | Magiclad Dragon - Vezzal the Star Eater |
| 160025022 | Rise Motor Emergent |
| 160025023 | Rise Motor Keelcopper |
| 160025024 | Rising HERO Reglam |
| 160025025 | Rising HERO Argent R |
| 160025026 | Rising Unit |
| 160025027 | Ice Age Pounder |
| 160025028 | Worker Warrior - Multitasking Manager |
| 160025029 | Hydrangea the Shadow Flower Tea Master |
| 160025030 | Tour Guide From the Underworld (Rush) |
| 160025031 | Fiend's Mirage |
| 160025032 | Fiend's Absoluter |
| 160025033 | Brassdes of the Wicked Wheels |
| 160025034 | Prey Archfiend |
| 160025035 | Prey Dullahan |
| 160025036 | Soen the Molten Martial Machine |
| 160025037 | Mässig Anglurr |
| 160025038 | Galactica Rising Oblivion |
| 160025039 | Resurrection Heliacal Riser |
| 160025040 | Interscrime |
| 160025041 | Lightclad Dragon Egg |
| 160025042 | Rising HERO Argent O |
| 160025043 | Rising HERO Argent F |
| 160025044 | Familiar-Possessed - Wynn (Rush) |
| 160025045 | Absorbing Fiend's Mirror |
| 160025046 | Vanishing Attack |
| 160025047 | Galactica Fusion Space |
| 160025048 | Happy Journal |
| 160025049 | Extra! Extra! Hot Off the Press |
| 160025050 | Clad Dragon Tome - Chapter on Curse Breaking |
| | *...y 154 cartas más* |

**`cards-unofficial.cdb`** (2 cartas)

| ID | Nombre (EN) |
|--:|-------------|
| 17412731 | Elder Entity Norden |
| 96782896 | Mind Master |

**`cards.cdb`** (242 cartas)

| ID | Nombre (EN) |
|--:|-------------|
| 64865 | Cyberse Code Magician |
| 64866 | Cyberse Code Magician |
| 847217 | Orichalcos Sword of Sealing |
| 1186447 | Horoscope Sorcerer, the Stargazer Magician |
| 1186448 | Horoscope Sorcerer, the Stargazer Magician |
| 1463589 | Anti-GMX Final Experiment |
| 1595137 | Evolved Daneen |
| 2263870 | Ultimate Slayer |
| 2347658 | Lovely Labrynth of the Silver Castle |
| 2618725 | GMX Partner Selandea |
| 3294539 | Crimson Blade Dragon |
| 3434362 | Rustin Mammoth |
| 4026187 | Teller of Fairy Tails |
| 4731784 | A Bao A Qu, the Lightless Shadow |
| 4993187 | W:P Fancy Ball |
| 5125629 | Malefic Paradigm Shift |
| 5148778 | Starving Venom Wing Dragon |
| 5208118 | Solving for Pendulum |
| 6083904 | Diabrocken the Ominous Specter |
| 6325660 | Dominus Spark |
| 6361316 | WAKE CUP! Kuro |
| 6547248 | Clown Crew New Face |
| 10000120 | Prince of Fairies |
| 10266279 | Junoldo the Shadespirit Power Patron |
| 12908094 | Gagaga Magician - Gagaga Magic |
| 12908095 | Gagaga Magician - Gagaga Magic |
| 13021682 | Starjunk Synchron |
| 13021683 | Starjunk Synchron |
| 13048473 | Pre-Preparation of Rites |
| 13203964 | Perfectron Hydradrive Dragon |
| 13243124 | Favorite HERO Flame Wingman |
| 13243125 | Favorite HERO Flame Wingman |
| 14391626 | Visas Samsara |
| 14425515 | Infernity Doom Slinger |
| 14556954 | VIP Whale |
| 14965712 | Multiplying Kuriboh! |
| 14965713 | Multiplying Kuriboh! |
| 15141103 | Dark Tuner Catastrogue |
| 15725501 | Makourai, the Lightning Strike |
| 15778492 | Gaming Gamer GG |
| 16734927 | Ectoplasmic Fortification |
| 17209452 | Kewl Tune Rotary |
| 17269895 | King's Resonance |
| 17473466 | Nervedo the Shadebeast Power Patron |
| 17856505 | Pumpking the Great Ghost King |
| 18078153 | Army of the Haunted |
| 18321034 | Hecahands Mankibuel |
| 18482473 | H.E.R.O. Flash! |
| 18595008 | Predaplant Lilizard |
| 18711696 | Assault Sonic Warrior |
| | *...y 192 cartas más* |

**`prerelease-cards-rush.cdb`** (39 cartas)

| ID | Nombre (EN) |
|--:|-------------|
| 160026003 | Royal Rebel's Pitch Shifter |
| 160026004 | Royal Rebel's Great Mixer |
| 160026005 | Royal Rebel's Falsetto |
| 160026006 | Royal Rebel's Extreme |
| 160026010 | Slay the Star Protector's Gunslinger |
| 160026011 | Fist the Star Protector's Roaring Gauntlet |
| 160026036 | Contractor of the Abyssal Dragon |
| 160026037 | Fist the Contractor of the Imprisoned Dragon |
| 160026039 | Familiar-Possessed - Eria (Rush) |
| 160026045 | Royal Rebel's Starting |
| 160026047 | Star Protector Awakening |
| 160026067 | Neo-Spacian Grand Mole (Rush) |
| 160026068 | Elemental HERO Earth Neos |
| 160402066 | Chaoskampf Beast Leviatriton |
| 160459001 | Dark Magician of Chaos (Rush) |
| 160459002 | Breaker the Magical Warrior (Rush) |
| 160459003 | Brain Control (Rush) |
| 160459004 | Bottomless Trap Hole (Rush) |
| 160459005 | Mad Reloader (Rush) |
| 160459006 | Magician of Faith (Rush) |
| 160459007 | Mask of Darkness (Rush) |
| 160459008 | Rescue Cat (Rush) |
| 160459009 | Summoner Monk (Rush) |
| 160459010 | Maha Vailo (Rush) |
| 160459011 | The Forceful Sentry (Rush) |
| 160459012 | Mystical Space Typhoon (Rush) |
| 160459013 | Shield Crush (Rush) |
| 160459014 | Super Polymerization (Rush) |
| 160459015 | One for One (Rush) |
| 160459016 | Happy Lover (Rush) |
| 160459017 | Saggi the Dark Clown (Rush) |
| 160459018 | Jerry Beans Man (Rush) |
| 160459019 | Shining Friendship (Rush) |
| 160459020 | Robotic Knight (Rush) |
| 160459021 | Swordstalker (Rush) |
| 160459022 | Penguin Soldier (Rush) |
| 160459023 | Rocket Warrior (Rush) |
| 160459024 | Panther Warrior (Rush) |
| 160459025 | Goblin Attack Force (Rush) |

**`prerelease-others.cdb`** (12 cartas)

| ID | Nombre (EN) |
|--:|-------------|
| 100200292 | Thoroughbred Elf |
| 100200293 | Assault Lion |
| 100200294 | Power Connection |
| 100200295 | Evil Lord - Zorc |
| 100295121 | Clown Crew Hat |
| 100296302 | Witchcrafter Seed |
| 100350262 | The Magical King of Dimension Zeta |
| 100457001 | Ancient Secrets |
| 100457102 | Mind Mirror Force |
| 100457103 | Emissaries from Darkness |
| 100457104 | Dark Armed Dragon Punisher |
| 100457105 | Ekhajar, Descendant Dragon of the Ice Barrier |

<!-- MIGRATE_LOG:END -->