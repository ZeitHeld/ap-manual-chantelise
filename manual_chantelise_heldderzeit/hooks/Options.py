# Object classes from AP that represent different types of options that you can create
from Options import Option, FreeText, NumericOption, Toggle, DefaultOnToggle, Choice, TextChoice, Range, NamedRange, OptionGroup, PerGameCommonOptions
# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value
from typing import Type, Any


####################################################################
# NOTE: At the time that options are created, Manual has no concept of the multiworld or its own world.
#       Options are defined before the world is even created.
#
# Example of creating your own option:
#
#   class MakeThePlayerOP(Toggle):
#       """Should the player be overpowered? Probably not, but you can choose for this to do... something!"""
#       display_name = "Make me OP"
#
#   options["make_op"] = MakeThePlayerOP
#
#
# Then, to see if the option is set, you can call is_option_enabled or get_option_value.
#####################################################################


# To add an option, use the before_options_defined hook below and something like this:
#   options["total_characters_to_win_with"] = TotalCharactersToWinWith
#

class FishTrade(Toggle):
	"""
	Fish trades from the Fisherman in Plains gives other rewards.
	"""
	
	display_name = "Fish Trading"

class ShopShuffle(Choice):
	"""
	Randomizes the Items that are to be found in the Shhop.
	Availbale Options:
	- None
	- Aira
	- Aira + Merchant
	- All (Aira, Merchant + Survival Dungeon)
	"""

	display_name = "Shop Shuffle"
	
	option_none = 0
	option_aira_only = 1
	option_include_merchant = 2
	option_both_with_survival = 3
	
	default = 2
	
class ShopSellUnlockShuffle(DefaultOnToggle):
	"""
	If enabled with Shop Shuffle, will also include checks to buy the unlocked items.
	"""
	
	display_name = "Shop Sell Unlock Shuffle"


class Fishsanity(Toggle):
	"""
	!! NOT YET IMPLEMENTED !!
	Adds in a check for catching a fish for the first time, and items for the corresponding fishes.
	"""
	
	display_name = "Fishsanity"


class Stagesanity(Toggle):
	"""
	!! NOT YET IMPLEMENTED !!
	Unlocks of Stages give Items
	and find Stages as Items
	"""
	
	display_name = "Stagesanity"

class Spellsanity(Choice):
	"""
	!! NOT YET IMPLEMENTED !!
	Adds in every spell as it's own unlockable Item.
	Spells get prioritied over junk during generation. 
	Available Options: None, Tiers 3-4, Tiers 2-4 (You can only cast spells with one gem.)
	"""
	
	display_name = "Spell Shuffle"

	option_none = 0
	option_regular = 1
	option_include_tier2 = 2

	default = 0

class ProgressiveStages(Toggle):
	"""
	!! NOT YET IMPLEMENTED !!
	Makes Stage Unlocks for Dungeons Progressive
	"""
	
	display_name = "Progressive Stages"

	option_disabled = 0
	option_enabled = 1
	option_include_bonus_stage = 2

	default = 0



#option_groups = [
#	OptionGroup(
#		"Gameplay Options"
#		[Stagesanity, ProgressiveStages]
#	),
#	OptionGroup(
#		"Randomization Options"
#		[ShopShuffle, ShopSellUnlockShuffle, FishTrade, Fishsanity, Spellsanity]
#	),
#	OptionGroup(
#		"Misc Options"
#		[DeathLink]
#	)
#]

#option_presets = {
#	"default": {
#		"stage_sanity": False,
#		"progressive_stages": ProgressiveStages.option_enabled,
#		"shop_shuffle": ShopShuffle.option_include_merchant,
#		"shop_sell_unlock_shuffle": True,
#		"fish_trading_shuffle": True,
#		"fishsanity": False,
#		"death_link": False
#	}
#}






# This is called before any manual options are defined, in case you want to define your own with a clean slate or let Manual define over them
def before_options_defined(options: dict[str, Type[Option[Any]]]) -> dict[str, Type[Option[Any]]]:
    #options["stage_sanity"] = Stagesanity
	#options["progressive_stages"] = ProgressiveStages
	options["shop_shuffle"] = ShopShuffle
	options["shop_sell_unlock_shuffle"] = ShopSellUnlockShuffle
	options["fish_trading_shuffle"] = FishTrade
	#options["fishsanity"] = Fishsanity
	#options["spellsanity"] = Spellsanity
	#options["death_link"] = 
	return options

# This is called after any manual options are defined, in case you want to see what options are defined or want to modify the defined options
def after_options_defined(options: Type[PerGameCommonOptions]):
    # To access a modifiable version of options check the dict in options.type_hints
    # For example if you want to change DLC_enabled's display name you would do:
    # options.type_hints["DLC_enabled"].display_name = "New Display Name"

    #  Here's an example on how to add your aliases to the generated goal
    # options.type_hints['goal'].aliases.update({"example": 0, "second_alias": 1})
    # options.type_hints['goal'].options.update({"example": 0, "second_alias": 1})  #for an alias to be valid it must also be in options

    pass

# Use this Hook if you want to add your Option to an Option group (existing or not)
def before_option_groups_created(groups: dict[str, list[Type[Option[Any]]]]) -> dict[str, list[Type[Option[Any]]]]:
    # Uses the format groups['GroupName'] = [TotalCharactersToWinWith]
	
	#groups["Gameplay Options"] = [Stagesanity]
	#groups["Gameplay Options"] = [ProgressiveStages]
	
	groups["Randomization Options"] = [ShopShuffle]
	groups["Randomization Options"] = [ShopSellUnlockShuffle]
	groups["Randomization Options"] = [FishTrade]
	#groups["Randomization Options"] = [Fishsanity]
	#groups["Randomization Options"] = [Spellsanity]
    return groups

def after_option_groups_created(groups: list[OptionGroup]) -> list[OptionGroup]:
    return groups
