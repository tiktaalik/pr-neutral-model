from pymongo import MongoClient
import pprint as prettyprint
import pickle




c = MongoClient()

collection = c.patents.patns

def walk_down_graph(pno,depth,threshold):
    p = collection.find_one({'pno':pno},{'pno':1, 'citedby':1, 'sorted_text':1})
    gens = [[p]]
    just_nodes = [p['pno']]
    node_gens = [[p['pno']]]
    links = []
    
    for i in range(1,depth):
        parents = gens[i-1]
        next_gen = []
        new_nodes = []

        for par in parents:
            children_pnos = par['citedby']
            children = collection.find({'pno': {"$in":children_pnos}}, {'pno':1, 'citedby':1, 'sorted_text':1, 'text':1})
            
            for child in list(children):
                if len(child['citedby']) >= threshold:
                    links.append((par['pno'],child['pno']))
                    # add only previously unseen nodes
                    if child['pno'] not in just_nodes:
                        next_gen.append(child)
                        new_nodes.append(child['pno'])
                        just_nodes.append(child['pno'])

        gens.append(next_gen)
        node_gens.append(new_nodes)

    return (just_nodes,node_gens,links,gens)

def pprint(to_print):
    pp = prettyprint.PrettyPrinter()
    pp.pprint(to_print)

results = walk_down_graph(4405829,5,400)
f = open('encryption_network.p','wb')
pickle.dump(results,f)
