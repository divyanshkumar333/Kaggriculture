import base64, json, zlib

def main():
    code = open('agents/v060_melon_frontrunner.py').read()
    b64 = code.split('base64.b85decode(\'')[1].split('\'')[0]
    actions = json.loads(zlib.decompress(base64.b85decode(b64)).decode('utf-8'))
    
    plants = set()
    animals = set()
    for a in actions:
        if not a: continue
        farmer_action = a.get('farmer')
        if type(farmer_action) == list and len(farmer_action) >= 2:
            if farmer_action[0] == 'PLANT':
                plants.add(farmer_action[1])
            elif farmer_action[0] == 'PLACE':
                animals.add(farmer_action[1])
                
        for w in a.get('hands', []):
            if type(w) == list and len(w) >= 2:
                if w[0] == 'PLANT':
                    plants.add(w[1])
                elif w[0] == 'PLACE':
                    animals.add(w[1])
                    
    print('Plants in base64:', plants)
    print('Animals in base64:', animals)

if __name__ == "__main__":
    main()
