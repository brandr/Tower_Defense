SLOW = "slow"		
POISON = "poison"

def build_effect(key, arg):
	#constructor = EFFECT_CONSTRUCTOR_MAP[key]
	constructor = EFFECT_DATA_MAP[key][CONSTRUCTOR]
	return constructor(arg)

class Effect:
	def __init__(self, key):
		self.effect_key = key
		self.duration = EFFECT_DATA_MAP[key][DURATION]

	def reset_duration(self):
		self.duration = EFFECT_DATA_MAP[self.effect_key][DURATION]

class SlowEffect(Effect):
	def __init__(self, arg):
		self.slow_value = arg
		Effect.__init__(self, SLOW)

class PoisonEffect(Effect):
	def __init__(self, arg):
		self.poison_value = arg
		Effect.__init__(self, POISON)

CONSTRUCTOR = "constructor"
DURATION = "duration"

EFFECT_DATA_MAP = {
	SLOW:{
		CONSTRUCTOR:SlowEffect,
		DURATION:80
	},
	POISON:{
		CONSTRUCTOR:PoisonEffect,
		DURATION:100
	}
}