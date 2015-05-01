from entity import BASIC_ENEMY, KNIGHT, BARBARIAN, TROLL, HORSE_RIDER, DEMON, GHOST, WRAITH, LICH, WYVERN, DEMON_GENERAL, WISP, LIGHTNING_ELEMENTAL, EARTH_ELEMENTAL, FIRE_ELEMENTAL

ROUND_REWARD_INCREMENT = 5

class RoundManager:
	def __init__(self, level):
		self.level = level
		self.round_number = 0
		self.round_counter = 0
		self.round_reward_counter = 0
		self.round_active = False
		self.current_wave_index = 0
		self.current_wave = []

	def update(self):
		self.wave_update()
		if not self.level.entities and self.round_number in MASTER_ROUND_MAP:
			round_map = MASTER_ROUND_MAP[self.round_number]
			keys = sorted(round_map.keys())
			last_group = round_map[keys[-1]]
			if self.round_counter > keys[-1] + last_group[1]*last_group[2]:
				self.end_round()
				return
		self.round_counter += 1

	def wave_update(self):
		if not self.round_number in MASTER_ROUND_MAP: return
		round_map = MASTER_ROUND_MAP[self.round_number]
		if self.round_counter in round_map: 
			self.current_wave_index = self.round_counter
			self.current_wave = round_map[self.round_counter]
		self.current_wave_update()

	def current_wave_update(self):
		if not self.current_wave: return
		count, increment = self.current_wave[1], self.current_wave[2]
		if self.round_counter >= self.current_wave_index + count*increment: return
		if  (self.round_counter - self.current_wave_index)%increment == 0:
			self.level.send_enemy(self.current_wave[0])
		self.round_reward_counter += ROUND_REWARD_INCREMENT

	def toggle(self):
		if not self.round_active: self.begin_round()

	def begin_round(self):
		self.round_active = True
		self.round_number += 1
		self.round_counter = 0
		self.round_reward_counter = 0

	def end_round(self):
		self.round_active = False
		self.level.give_money(self.round_reward_counter)

ROUND_1_MAP = {
	5:[
		BASIC_ENEMY, 3, 40
	],
	125:[
		FIRE_ELEMENTAL, 1, 10
	]
}

ROUND_2_MAP = {
	20:[
		BASIC_ENEMY, 4, 35
	]
}

ROUND_3_MAP = {
	5:[
		BASIC_ENEMY, 10, 20
	]
}

ROUND_4_MAP = {
	5:[
		BASIC_ENEMY, 3, 15
	],
	60:[
		KNIGHT, 1, 10
	]
}

ROUND_5_MAP = {
	10:[
		BASIC_ENEMY, 2, 10
	],
	35:[
		KNIGHT, 3, 30
	],
	150:[
		BASIC_ENEMY, 5, 5
	]
}

ROUND_6_MAP = {
	5:[
		BARBARIAN, 10, 10
	]
}

ROUND_7_MAP = {
	5:[
		KNIGHT, 20, 5
	]
}

ROUND_8_MAP = {
	100:[
		KNIGHT, 50, 10
	]
}

ROUND_9_MAP = {
	50:[
		KNIGHT, 100, 50
	]
}

ROUND_10_MAP = {
	200:[
		TROLL, 1, 10
	]
}

ROUND_11_MAP = {
	50:[
		HORSE_RIDER, 8, 30
	]
}

ROUND_12_MAP = {
	20:[
		KNIGHT, 15, 20
	],
	330:[
		TROLL, 1, 10
	],
	360:[
		KNIGHT, 3, 20
	],
	450:[
		HORSE_RIDER, 3, 20
	]
}

ROUND_13_MAP = {
	10:[
		DEMON, 10, 10
	]
}

ROUND_14_MAP = {
	10:[
		HORSE_RIDER, 5, 10
	],
	80:[
		TROLL, 2, 30
	]
}

ROUND_15_MAP = {
	20:[
		TROLL, 1, 30
	],
	50:[
		DEMON, 50, 10
	]
}

ROUND_16_MAP = {
	10:[
		KNIGHT, 3, 10
	],
	40:[
		HORSE_RIDER, 1, 10
	],
	50:[
		KNIGHT, 1, 50
	],
	100:[
		TROLL, 1, 20
	],
	160:[
		GHOST, 50, 10
	]
}

ROUND_17_MAP = {
	50:[
		TROLL, 10, 50
	]
}

ROUND_18_MAP = {
	25:[
		WRAITH, 10, 25
	]
}

ROUND_19_MAP = {
	25:[
		WRAITH, 2, 10
	],
	60:[
		LICH, 1, 10
	]
}

ROUND_20_MAP = {
	10:[
		KNIGHT, 5, 10
	],
	80:[
		WYVERN, 1, 10
	]
}

ROUND_21_MAP = {
	20:[
		WRAITH, 50, 15
	],
	800:[
		DEMON, 50, 10
	]
}

ROUND_22_MAP = {
	10:[
		HORSE_RIDER, 2, 5
	],
	35:[
		WYVERN, 1, 5
	],
	40:[
		KNIGHT, 100, 5
	]
}

ROUND_23_MAP = {
	5:[
		KNIGHT, 1, 10
	],
	15:[
		HORSE_RIDER, 1, 15
	],
	30:[
		TROLL, 3, 15
	],
	110:[
		WYVERN, 2, 15
	]
}

ROUND_24_MAP = {
	200:[
		WYVERN, 1, 10
	],
	210:[
		LICH, 1, 10
	],
	220:[
		WRAITH, 200, 10
	]
}

ROUND_25_MAP = {
	30:[
		WYVERN, 5, 20
	],
	150:[
		TROLL, 50, 10
	]
}

ROUND_26_MAP = {
	30:[
		LICH, 3, 30
	]
}

ROUND_27_MAP = {
	10:[
		WYVERN, 7, 20
	],
	150:[
		TROLL, 3, 20
	]
}

ROUND_28_MAP = {
	
}

ROUND_29_MAP = {
	
}

ROUND_30_MAP = {
	
}

MASTER_ROUND_MAP = {
	0:None,
	1:ROUND_1_MAP,
	2:ROUND_2_MAP,
	3:ROUND_3_MAP,
	4:ROUND_4_MAP,
	5:ROUND_5_MAP,
	6:ROUND_6_MAP,
	7:ROUND_7_MAP,
	8:ROUND_8_MAP,
	9:ROUND_9_MAP,
	10:ROUND_10_MAP,
	11:ROUND_11_MAP,
	12:ROUND_12_MAP,
	13:ROUND_13_MAP,
	14:ROUND_14_MAP,
	15:ROUND_15_MAP,
	16:ROUND_16_MAP,
	17:ROUND_17_MAP,
	18:ROUND_18_MAP,
	19:ROUND_19_MAP,
	20:ROUND_20_MAP,
	21:ROUND_21_MAP,
	22:ROUND_22_MAP,
	23:ROUND_23_MAP,
	24:ROUND_24_MAP,
	25:ROUND_25_MAP,
	26:ROUND_26_MAP,
	27:ROUND_27_MAP,
	28:ROUND_28_MAP,
	29:ROUND_29_MAP,
	30:ROUND_30_MAP
}