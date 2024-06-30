from memory_addresses import *

# Pokemons is a class for interacting with all Pokemon in the game
class Pokemons:
    def __init__(self, emulator):
        self.emulator = emulator

    def get_party_size(self):
        return self.emulator.read_m(PARTY_SIZE_ADDRESS)

    def get_current_party(self):
        i = 0
        party = []
        while i in range(self.get_party_size()):
            party.append(Pokemon(i,self.emulator))
            i+=1
        return party

    def get_current_party_pokemon_ids(self):
        return [self.emulator.read_m(addr) for addr in PARTY_ADDRESSES]

    def get_avg_party_level(self):
        poke_levels = [max(self.emulator.read_m(a) - 2, 0) for a in LEVELS_ADDRESSES]
        return sum(poke_levels)/(max(self.get_party_size(),1))

    def get_total_party_level(self):
        poke_levels = [max(self.emulator.read_m(a) - 2, 0) for a in LEVELS_ADDRESSES]
        return max(sum(poke_levels), 0) # subtract starting pokemon level

    def get_seen_poke(self):
        return sum([self.bit_count(self.emulator.read_m(a)) for a in SEEN_POKEMONS_ADDRESSES])

    def get_caught_poke(self):
        return sum([self.bit_count(self.emulator.read_m(a)) for a in CAUGHT_POKEMONS_ADDRESSES])

# Pokemon is a class for interacting with a single Pokemon
class Pokemon:
    def __init__(self, index, emulator):
        self.index = index
        self.emulator = emulator

    def get_id(self):
        return self.emulator.read_m(PARTY_ADDRESSES[self.index])

    def get_level(self):
        return self.emulator.read_m(LEVELS_ADDRESSES[self.index])

    def get_current_hp(self):
        return read_hp(self.emulator,HP_ADDRESSES[self.index])

    def get_max_hp(self):
        return read_hp(self.emulator,MAX_HP_ADDRESSES[self.index])

    def get_status(self):
        return self.emulator.read_m(PARTY_STATUS_ADDRESSES[self.index])

    def get_pokemon_name(self):
        return get_pokemon_name(self.get_id())

def read_hp(emulator, start):
    return 256 * emulator.read_m(start) + emulator.read_m(start+1)

def get_pokemon_status(status_id):
    match status_id:
        case 8:
            return 'PSN'
        case _:
            return f'unknown {status_id}'

def get_pokemon_name(id):
    match id:
        case 1:
            return ''
        case 9:
            return 'Ivysaur'
        case 28:
            return 'Blastoise'
        case 36:
            return 'Pidgey'
        case 150:
            return 'Pidgeotto'
        case 151:
            return 'Pidgeot'
        case 165:
            return 'Rattata'
        case 166:
            return 'Raticate'
        case 153:
            return 'Bulbasaur'
        case 154:
            return 'Venusaur'
        case 176:
            return 'Charmander'
        case 177:
            return 'Squirtle'
        case 178:
            return 'Charmeleon'
        case 180:
            return 'Charizard'
        case 188:
            return 'Wartortle'
        case _:
            return f'unknown {id}'


# Caterpie     123
# Metapod      124
# Butterfree   125
# Weedle       112
# Kakuna       113
# Beedrill     114
# Pidgey        36
# Pidgeotto    150
# Pidgeot      151
# Rattata      165
# Raticate     166
# Spearow        5
# Fearow        35
# Ekans        108
# Arbok         45
# Pikachu       84
# Raichu        85
# Sandshrew     96
# Sandslash     97
# Nidoran(F)    15
# Nidorina     168
# Nidoqueen     16
# Nidoran(M)     3
# Nidorino     167
# Nidoking       7
# Clefairy       4
# Clefable     142
# Vulpix        82
# Ninetales     83
# Jigglypuff   100
# Wigglytuff   101
# Zubat        107
# Golbat       130
# Oddish       185
# Gloom        186
# Vileplume    187
# Paras        109
# Parasect      46
# Venonat       65
# Venomoth     119
# Diglett       59
# Dugtrio      118
# Meowth        77
# Persian      144
# Psyduck       47
# Golduck      128
# Mankey        57
# Primeape     117
# Growlithe     33
# Arcanine      20
# Poliwag       71
# Poliwhirl    110
# Poliwrath    111
# Abra         148
# Kadabra       38
# Alakazam     149
# Machop       106
# Machoke       41
# Machamp      126
# Bellsprout   188
# Weepinbell   189
# Victreebell  190
# Tentacool     24
# Tentacruel   155
# Geodude      169
# Graveler      39
# Golem         49
# Ponyta       163
# Rapidash     164
# Slowpoke      37
# Slowbro        8
# Magnemite    173
# Magneton      54
# Farfetch'd    64
# Doduo         70
# Dodrio       116
# Seel          58
# Dewgong      120
# Grimer        13
# Muk          136
# Shellder      23
# Cloyster     139
# Gastly        25
# Haunter      147
# Gengar        14
# Onix          34
# Drowzee       48
# Hypno        129
# Krabby        78
# Kingler      138
# Voltorb        6
# Electrode    141
# Exeggcute     12
# Exeggutor     10
# Cubone        17
# Marowak      145
# Hitmonlee     43
# Hitmonchan    44
# Lickitung     11
# Koffing       55
# Weezing      143
# Rhyhorn       18
# Rhydon         1
# Chansey       40
# Tangela       30
# Kangaskhan     2
# Horsea        92
# Seadra        93
# Goldeen      157
# Seaking      158
# Staryu        27
# Starmie      152
# Mr. Mime      42
# Scyther       26
# Jynx          72
# Electabuzz    53
# Magmar        51
# Pinsir        29
# Tauros        60
# Magikarp     133
# Gyarados      22
# Lapras        19
# Ditto         76
# Eevee        102
# Vaporeon     105
# Jolteon      104
# Flareon      103
# Porygon      170
# Omanyte       98
# Omastar       99
# Kabuto        90
# Kabutops      91
# Aerodactyl   171
# Snorlax      132
# Articuno      74
# Zapdos        75
# Moltres       73
# Dratini       88
# Dragonair     89
# Dragonite     66
# Mewtwo       131
# Mew           21