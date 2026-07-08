# Object classes from AP core, to represent an entire MultiWorld and this individual World that's part of it
from typing import Any
from worlds.AutoWorld import World
from BaseClasses import MultiWorld, CollectionState, Item

# Object classes from Manual -- extending AP core -- representing items and locations that are used in generation
from ..Items import ManualItem
from ..Locations import ManualLocation

# Raw JSON data from the Manual apworld, respectively:
#          data/game.json, data/items.json, data/locations.json, data/regions.json
#
from ..Data import game_table, item_table, location_table, region_table

# These helper methods allow you to determine if an option has been set, or what its value is, for any player in the multiworld
from ..Helpers import is_option_enabled, get_option_value, format_state_prog_items_key, ProgItemsCat, remove_specific_item

# calling logging.info("message") anywhere below in this file will output the message to both console and log file
import logging

########################################################################################
## Order of method calls when the world generates:
##    1. create_regions - Creates regions and locations
##    2. create_items - Creates the item pool
##    3. set_rules - Creates rules for accessing regions and locations
##    4. generate_basic - Runs any post item pool options, like place item/category
##    5. pre_fill - Creates the victory location
##
## The create_item method is used by plando and start_inventory settings to create an item from an item name.
## The fill_slot_data method will be used to send data to the Manual client for later use, like deathlink.
########################################################################################

GOAL_ID_CURE_ELISE = 3
TROPHY_NAME = "Rainbow Rose Petal"


# Use this function to change the valid filler items to be created to replace item links or starting items.
# Default value is the `filler_item_name` from game.json
def hook_get_filler_item_name(world: World, multiworld: MultiWorld, player: int) -> str | bool:
    return False

def before_generate_early(world: World, multiworld: MultiWorld, player: int) -> None:
    """
    This is the earliest hook called during generation, before anything else is done.
    Use it to check or modify incompatible options, or to set up variables for later use.
    """
    pass

# Called before regions and locations are created. Not clear why you'd want this, but it's here. Victory location is included, but Victory event is not placed yet.
def before_create_regions(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after regions and locations are created, in case you want to see or modify that information. Victory location is included.
def after_create_regions(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to remove locations from the world
    locationNamesToRemove: list[str] = [] # List of location names

    # Add your code here to calculate which locations to remove

    for region in multiworld.regions:
        if region.player == player:
            for location in list(region.locations):
                if location.name in locationNamesToRemove:
                    region.locations.remove(location)

# This hook allows you to access the item names & counts before the items are created. Use this to increase/decrease the amount of a specific item in the pool
# Valid item_config key/values:
# {"Item Name": 5} <- This will create qty 5 items using all the default settings
# {"Item Name": {"useful": 7}} <- This will create qty 7 items and force them to be classified as useful
# {"Item Name": {"progression": 2, "useful": 1}} <- This will create 3 items, with 2 classified as progression and 1 as useful
# {"Item Name": {0b0110: 5}} <- If you know the special flag for the item classes, you can also define non-standard options. This setup
#       will create 5 items that are the "useful trap" class
# {"Item Name": {ItemClassification.useful: 5}} <- You can also use the classification directly
def before_create_items_all(item_config: dict[str, int|dict], world: World, multiworld: MultiWorld, player: int) -> dict[str, int|dict]:
    progressive_equipment = get_option_value(multiworld, player, "progressive_equipment")
    goal = get_option_value(multiworld, player, "goal")
    required_petals = get_option_value(multiworld, player, "petals_required")
    total_petals = get_option_value(multiworld, player, "petals_total")
    
    # for item in item_config:
    #     if progressive_equipment and "Standalone Equipment" in world.item_name_to_item[item.name].get("category", []):
    #         {item.name: {"filler": 1}}

    #item_config["itemNameA"] = 5 # name & amount

    if goal == GOAL_ID_CURE_ELISE:
        if required_petals > total_petals:
            if required_petals > 45:
                total_petals = 50
            else:                
                total_petals = required_petals + 5

        if total_petals > 0:
            ### logging.info("<Chantelise-Manual> (before_create_items_all) Adding *" + str(total_petals) + "* Petals to pool.")

            item_config[TROPHY_NAME] = total_petals
           
        else:
            ### logging.info("<Chantelise-Manual> (before_create_items_all) No Petals needed.")
            pass

    return item_config

# The item pool before starting items are processed, in case you want to see the raw item pool at that stage
def before_create_items_starting(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    return item_pool

# The item pool after starting items are processed but before filler is added, in case you want to see the raw item pool at that stage
def before_create_items_filler(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    # Use this hook to remove items from the item pool
    itemNamesToRemove: list[str] = [] # List of item names

    goal = get_option_value(multiworld, player, "goal")
    required_petals = get_option_value(multiworld, player, "trophies_required")
    total_petals = get_option_value(multiworld, player, "trophies_total")
    shop_shuffle_aira = get_option_value(multiworld, player, "shop_shuffle") >= 1
    shop_shuffle_merchant = get_option_value(multiworld, player, "shop_shuffle") >= 2
    shop_shuffle_survival = get_option_value(multiworld, player, "shop_shuffle") >= 3
    trade_shuffle = get_option_value(multiworld, player, "fish_trade")
    progressive_equipment = get_option_value(multiworld, player, "progressive_equipment")
    
    aira_list: list[str] = []
    merchant_list: list[str] = []
    survival_list: list[str] = []
    trade_list: list[str] = []
    prog_equip_list: list[str] = []

    for item in item_pool:
        if (shop_shuffle_aira == False and "Aira Item" in world.item_name_to_item[item.name].get("category", [])):
            ### logging.info("<Chantelise-Manual> (before_create_items_filler) FOUND - AIRA ITEM TO REMOVE: " + item.name)
            if not item.name in aira_list:
                ### logging.info("<Chantelise-Manual> (before_create_items_filler) FIRST ONE!")
                aira_list.append(item.name)
        if shop_shuffle_merchant == False and "Merchant Item" in world.item_name_to_item[item.name].get("category", []):
            ### logging.info("<Chantelise-Manual> (before_create_items_filler) FOUND - MERCHANT ITEM TO REMOVE: " + item.name)
            if not item.name in merchant_list:
                ### logging.info("<Chantelise-Manual> (before_create_items_filler) FIRST ONE!")
                merchant_list.append(item.name)
        if shop_shuffle_survival == False and "Survival Dungeon Item" in world.item_name_to_item[item.name].get("category", []):
            ### logging.info("<Chantelise-Manual> (before_create_items_filler) FOUND - SD ITEM TO REMOVE: " + item.name)
            if not item.name in survival_list:
                ### logging.info("<Chantelise-Manual> (before_create_items_filler) FIRST ONE!")
                survival_list.append(item.name)
        if (trade_shuffle == False) and ("Trading Reward" in world.item_name_to_item[item.name].get("category", [])):
            ### logging.info("<Chantelise-Manual> (before_create_items_filler) FOUND - TRADE REWARD TO REMOVE: " + item.name)
            if not item.name in trade_list:
                ### logging.info("<Chantelise-Manual> (before_create_items_filler) FIRST ONE!")
                trade_list.append(item.name)

        # if progressive_equipment and "Standalone Equipment" in world.item_name_to_item[item.name].get("category", []):
        #     logging.info("<Chantelise-Manual> (before_create_items_filler) FOUND A SOLO EQUIP TO REMOVE: " + item.name)
        #     if not item.name in prog_equip_list:
        #         prog_equip_list.append(item.name)
        #         item.count = 1
        # if progressive_equipment:
        #     prog_equip_list.append("")

    for itemName in aira_list:
        ### logging.info("<Chantelise-Manual> (before_create_items_filler) Adding Aira Item for removal: " + itemName)
        itemNamesToRemove.append(itemName)
    for itemName in merchant_list:
        ### logging.info("<Chantelise-Manual> (before_create_items_filler) Adding Merchant Item for removal: " + itemName)
        itemNamesToRemove.append(itemName)
    for itemName in survival_list:
        ### logging.info("<Chantelise-Manual> (before_create_items_filler) Adding SD Item for removal: " + itemName)
        itemNamesToRemove.append(itemName)
    for itemName in trade_list:
        ### logging.info("<Chantelise-Manual> (before_create_items_filler) Adding Trade Item for removal: " + itemName)
        itemNamesToRemove.append(itemName)
    # for itemName in prog_equip_list:
    #     itemNamesToRemove.append(itemName)

    # Add your code here to calculate which items to remove.
    #
    # Because multiple copies of an item can exist, you need to add an item name
    # to the list multiple times if you want to remove multiple copies of it.

    for itemName in itemNamesToRemove:
        ### logging.info("<Chantelise-Manual> (before_create_items_filler) Gonna Remove: " + itemName)
        item = next(i for i in item_pool if i.name == itemName)
        remove_specific_item(item_pool, item)



    return item_pool

    # Some other useful hook options:

    ## Place an item at a specific location
    # location = next(l for l in multiworld.get_unfilled_locations(player=player) if l.name == "Location Name")
    # item_to_place = next(i for i in item_pool if i.name == "Item Name")
    # location.place_locked_item(item_to_place)
    # remove_specific_item(item_pool, item_to_place)

# The complete item pool prior to being set for generation is provided here, in case you want to make changes to it
def after_create_items(item_pool: list, world: World, multiworld: MultiWorld, player: int) -> list:
    goal = get_option_value(multiworld, player, "goal")
    required_petals = get_option_value(multiworld, player, "trophies_required")
    total_petals = get_option_value(multiworld, player, "trophies_total")
    trade_shuffle = get_option_value(multiworld, player, "fish_trade")
    fishsanity = get_option_value(multiworld, player, "fishsanity")
    shop_shuffle_none = get_option_value(multiworld, player, "shop_shuffle") == 0
    progressive_equipment = get_option_value(multiworld, player, "progressive_equipment")


    # for item in item_pool:
    #     if shop_shuffle_none:
    #         logging.info("<Chantelise-Manual> (after_create_items) NO SHOP SHUFFLE")
    #         if item.name == ("Cat Statue" or "Coin Emblem"):
    #             logging.info("<Chantelise-Manual> (after_create_items) MARKING COIN ITEMS AS FILLER")
    #             item.classification = "filler"
    #             logging.info("<Chantelise-Manual> (after_create_items) MARKED COIN ITEMS AS FILLER")
    #     if progressive_equipment:
    #         logging.info("<Chantelise-Manual> (after_create_items) EQUIPS ARE PROGRESSIVE")
    #         if "Separate Equipment" in world.item_name_to_item[item.name].get("category", []):
    #             logging.info("<Chantelise-Manual> (after_create_items) MARKING SOLO EQUIPS AS FILLER")
    #             item.classification = "filler"
    #             logging.info("<Chantelise-Manual> (after_create_items) MARKED SOLO EQUIPS AS FILLER")

    return item_pool

# Called before rules for accessing regions and locations are created. Not clear why you'd want this, but it's here.
def before_set_rules(world: World, multiworld: MultiWorld, player: int):
    pass

# Called after rules for accessing regions and locations are created, in case you want to see or modify that information.
def after_set_rules(world: World, multiworld: MultiWorld, player: int):
    # Use this hook to modify the access rules for a given location
    goal = get_option_value(multiworld, player, "goal")

    def Example_Rule(state: CollectionState) -> bool:
        # Calculated rules take a CollectionState object and return a boolean
        # True if the player can access the location
        # CollectionState is defined in BaseClasses
        return True
    
    def hasEnoughTrophies(state: CollectionState) -> bool:
        """Checks if the player has enough Rose Petals to beat the game."""
        #return state.count("Blue Rose Petal", player) >= get_option_value(multiworld, player, "trophies_required")

        #return "|Blue Rose Petal:" + str(get_option_value(multiworld, player, "trophies_required")) + "|"

        return state.has(TROPHY_NAME, player, get_option_value(multiworld, player, "trophies_required"))


    ## Common functions:
    # location = world.get_location(location_name, player)
    # location.access_rule = Example_Rule

    if goal == GOAL_ID_CURE_ELISE:
        trophy_location = world.get_location("Cure Chante with Rainbow Rose Petals")
        #trophy_location.access_rule = lambda state: hasEnoughTrophies(state)
        trophy_location.access_rule = lambda state: state.has(TROPHY_NAME, player, get_option_value(multiworld, player, "petals_required"))

    ## Combine rules:
    # old_rule = location.access_rule
    # location.access_rule = lambda state: old_rule(state) and Example_Rule(state)
    # OR
    # location.access_rule = lambda state: old_rule(state) or Example_Rule(state)

# The item name to create is provided before the item is created, in case you want to make changes to it
def before_create_item(item_name: str, world: World, multiworld: MultiWorld, player: int) -> str:
    return item_name

# The item that was created is provided after creation, in case you want to modify the item
def after_create_item(item: ManualItem, world: World, multiworld: MultiWorld, player: int) -> ManualItem:
    return item

# This method is run towards the end of pre-generation, before the place_item options have been handled and before AP generation occurs
def before_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run at the very end of pre-generation, once the place_item options have been handled and before AP generation occurs
def after_generate_basic(world: World, multiworld: MultiWorld, player: int):
    pass

# This method is run every time an item is added to the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be cancelled/undone in after_remove_item
def after_collect_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you add to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] += 1
    pass

# This method is run every time an item is removed from the state, can be used to modify the value of an item.
# IMPORTANT! Any changes made in this hook must be first done in after_collect_item
def after_remove_item(world: World, state: CollectionState, Changed: bool, item: Item):
    # the following let you undo the addition to the Potato Item Value count
    # if item.name == "Cooked Potato":
    #     state.prog_items[item.player][format_state_prog_items_key(ProgItemsCat.VALUE, "Potato")] -= 1
    pass


# This is called before slot data is set and provides an empty dict ({}), in case you want to modify it before Manual does
def before_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called after slot data is set and provides the slot data at the time, in case you want to check and modify it after Manual is done with it
def after_fill_slot_data(slot_data: dict, world: World, multiworld: MultiWorld, player: int) -> dict:
    return slot_data

# This is called right at the end, in case you want to write stuff to the spoiler log
def before_write_spoiler(world: World, multiworld: MultiWorld, spoiler_handle) -> None:
    pass

# This is called when you want to add information to the hint text
def before_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:

    ### Example way to use this hook:
    # if player not in hint_data:
    #     hint_data.update({player: {}})
    # for location in multiworld.get_locations(player):
    #     if not location.address:
    #         continue
    #
    #     use this section to calculate the hint string
    #
    #     hint_data[player][location.address] = hint_string

    pass

def after_extend_hint_information(hint_data: dict[int, dict[int, str]], world: World, multiworld: MultiWorld, player: int) -> None:
    pass

def hook_interpret_slot_data(world: World, player: int, slot_data: dict[str, Any]) -> dict[str, Any]:
    """
        Called when Universal Tracker wants to perform a fake generation
        Use this if you want to use or modify the slot_data for passed into re_gen_passthrough
    """
    return slot_data
