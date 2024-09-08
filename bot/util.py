import re

def parse_id(_id):
    """
    Parses <@1234567> kind of ids to numeric only 1234567
    """    
    _id = str(_id)
    if '@' in _id:
        return str(_id.split('@')[1][:-1])
    return _id


badge_to_emoji = {
    'ice': ':snowflake:',
    'bug': ':beetle:',
    'grass': ':seedling:',
    'water': ':droplet:',
    'normal': ':white_square_button:',
    'psychic': ':eye:',
    'ghost': ':badge_ghost:',
    'electric': ':zap:'
}