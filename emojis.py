import random
from math import floor

class emojiLib:
    def __init__(self):
        self.emojis = {
            'misc': {
                'dotahouse': '<a:DotaHouse:849006603663048724>',
                'points': '<:points:1208489988879155262>',
                "creep_radiant": '<:Creep_Radiant:1207041014481682502>',
                "creep_dire": '<:Creep_Dire:1207041042780790784>'
            },
            'medals': {
                'herald': '<:Herald:843856608353845269>',
                'guardian': '<:Guardian:843856608831995964>',
                'crusader': '<:Crusader:843856608471941173>',
                'archon': '<:Archon:843856608815087626>',
                'legend': '<:Legend:843856608785858601>',
                'ancient': '<:Ancient:843856608882589747>',
                'divine': '<:Divine:843856608609828865>',
                'immortal': '<:Immortal:843856609477787719>'
            },
            'items': {
                'rapier': '<:Rapier:850828789947564053>',
                'observer': '<:Observer:1228867437017960540>'
            },
            'heros': {
                'invoker': '<:Invoker:849442548044660777>',
                'earthshaker': '<:Earthshaker:849443338772152360>',
                'mars': '<:Mars:849444978034737242>',
                'pudge_cartoon': '<:PudgeArcana:849636106383130664>',
            },
            'abilities': {
                'techiesmine': '<:TechiesMine:843852928351338516>'
            },
            'cosmetics': {
                'clockhead': '<:ClockHead:859597036310233121>',
                'dragonclaw': '<:DChook:848629647116730389>',
            }
        }

    def getEmoji(self, name: str):
        for emojis in self.emojis.values():
            if name in emojis.keys():
                return emojis[name]
            
    def getEmojiId(self, name: str):
        for emojis in self.emojis.values():
            if name in emojis.keys():
                return int(emojis[name].split(':')[2].replace('>',''))

    def getRandomGameEmoji(self):
        return random.choice(
            list(self.emojis['items'].values()) +
            list(self.emojis['heros'].values()) +
            list(self.emojis['abilities'].values()) +
            list(self.emojis['cosmetics'].values())
        )
    
    def medal(self, name: str = None, ratio: float = None):
        if name:
            name = name.lower()
            if name not in self.emojis['medals'].keys():
                return f"[invalid medal name: {name}]"
            return self.emojis['medals'][name]
        if ratio is not None:
            if ratio > 1.0 or ratio < 0.0:
                return f"[Medal range is [0,1], got: {ratio}]"
            if ratio == 1:
                return self.emojis['medals']['immortal']
            medal_order = ['herald','guardian','crusader','archon','legend','ancient','divine']
            medal_index = floor(ratio**(2/3)*len(medal_order))
            return self.emojis['medals'][medal_order[medal_index]]
        
emojis = emojiLib()
            
if __name__ == '__main__':
    print(emojis.getEmojiId('creep_radiant'))