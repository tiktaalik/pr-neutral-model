# real_dots.py
# produces dots from the real networks retrieved from the patns collection
# using real_networks.py
#
# Zackary Dunivin, Center for Advanced Computation, Reed College
# June 16 2015
import pickle
import operator
from pprint import pprint
from random import random



def flatten_text(D, keylabel = "key"):
    arr = []
    
    for elem in D:
        # just copies the dict entry in an array
        newElem = D[elem]
        newElem[keylabel] = elem
        arr.append(newElem)

    return arr


def write_dot(network,n,file_name="geneology",fake=False):
    # n is number of traits to look at
    # the results of real_networks.py produces a 4-tuple
    # 0: just_nodes: the pno of every node in the network
    # 1: node_gens: the pno of every node in the network separated into 
    #               lists by generation
    # 2: links: a tuple of parent pno and child pno for every edge in 
    #           the network
    # 3: gens: a dictionary containing the pno, citedby and sorted_text 
    #          for every node in the network the pno of every node in the
    #          network separated into lists by generation

    just_nodes = network[0]
    node_gens = network[1]
    links = network[2]
    gens = network[3]
    
    # list with just the records
    recs = []        
    for gen in gens:
        recs += gen
    
    rec_dict = {}
    for rec in recs:
        rec_dict[rec['pno']] = rec

    recs = rec_dict
    recs = trim_sorted_text(recs,n)


    node_gens = gens_by_pno(just_nodes,15)

    file = open(file_name + '.dot', 'w')
    file.write(
"""digraph inheritance {
center=true;
ratio = .77
size = 5
node [shape=square, style = filled, fixedsize=false, height = 4, width= 4, fillcolor = black, label = ""]
node [layer=all];
edge [arrowhead=none];
"""
)
    # guide rank
    file.write('/*guide*/ { node [color=invis, fillcolor = invis]; edge [style=invis]; ')
    for i in range(len(node_gens)-1):
        s = ('gen_',str(i),' -> ')
        s = ''.join(s)      
        file.write(s)
    s = ('gen_',str(len(node_gens)))
    s = ''.join(s) 
    file.write(s)
    file.write(';}\n')

    #
    # patent ranks
    #
    # generation
    for i in range(len(node_gens)):
        s = ('{ rank = same; gen_',str(i),'; ')            
        s = ''.join(s)
        file.write(s)
        # patent nodes            
        for pno in node_gens[i]:
            # genealogy                
            
            s = (str(pno),'; ')
            s = ''.join(s)           
            file.write(s)
                    
        # close subgraph
        file.write('}\n')

    # nodes
    # color the progenitor node
    string = '%d [color = red, fillcolor = red]\n' % just_nodes[0]
    file.write(string)

    if fake == False:
        for tup in links:
            # color the child red
            if shared_traits(tup[0],tup[1],recs):
                string = '%d [color = red, fillcolor = red]\n' % tup[1]
                file.write(string)
    else:
        for node in just_nodes[1::]:
            x = random()
            if x <= .12:
                string = '%d [color = red, fillcolor = red]\n' % node
                file.write(string)

    # edges
    for tup in links:
        string = '%d -> %d [color="black", style="solid"];\n' % (tup[0], tup[1])
        file.write(string)


    file.write('}\n')
    file.close()

def shared_traits(p1,p2,recs):
    try:
        p1set = set(recs[p1]['words'])
        type(recs)
        p2set = set(recs[p2]['words'])

        # color the child red
        if len(p1set.intersection(p2set)) > 0:
            return True
    
    except TypeError, IndexError:
        print(type(recs))    
    
    return False

def gens_by_pno(just_nodes,width):
    nodes = sorted(just_nodes)
    # first generation is the progenitor patent
    new_gens = [[nodes.pop(0)]]

    while len(nodes) > width:
        gen = []
        for i in range(width):
            gen.append(nodes.pop(0))

        new_gens.append(gen)

    # remaining patents make their own generation
    last_gen = []
    while len(nodes) > 0:
        last_gen.append(nodes.pop(0))

    new_gens.append(last_gen)

    return new_gens


def trim_sorted_text(recs,n):
    """sorted_text = top n tf-idf words"""
    for k in recs:
        n_traits = top_n_words(recs[k],n)
        recs[k]['words'] = n_traits

    return recs


def top_n_words(rec,n):
    # given a record returns the top n tf-idf words
    traits = []
    try: 
        bow = rec['sorted_text']

    except KeyError:
        bow = flatten_text(rec['text'],'word')
        try:
            sorted_text = sorted(bow, key=lambda w: w[u'tf-idf'], reverse = True)
        # may not have tf-idf
        except KeyError:
            return None


    for word in bow[0:n]:
        traits.append(word['word'])

    return traits


def colors_for_graphviz(palette="rainbow"):
    # For multi-colored inheritance layers. Greys, black and white removed.
    # Shuffle into random order
    rainbow = ["red", "yellow", "orange", "green", "blue", "purple"]
    svg = ["aliceblue", "antiquewhite", "aqua", "aquamarine", "beige", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "forestgreen", "fuchsia", "gainsboro", "gold", "goldenrod", "gray", "green", "greenyellow", "hotpink", "indianred", "indigo", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "whitesmoke", "yellow", "yellowgreen"]
    x11 = ["aliceblue", "antiquewhite", "antiquewhite1", "antiquewhite2", "antiquewhite3", "antiquewhite4", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4", "honeydew", "honeydew1", "honeydew2", "honeydew3", "honeydew4", "hotpink", "hotpink1", "hotpink2", "hotpink3", "hotpink4", "indianred", "indianred1", "indianred2", "indianred3", "indianred4", "indigo", "invis", "ivory", "ivory1", "ivory2", "ivory3", "ivory4", "khaki", "khaki1", "khaki2", "khaki3", "khaki4", "lavender", "lavenderblush", "lavenderblush1", "lavenderblush2", "lavenderblush3", "lavenderblush4", "lawngreen", "lemonchiffon", "lemonchiffon1", "lemonchiffon2", "lemonchiffon3", "lemonchiffon4", "lightblue", "lightblue1", "lightblue2", "lightblue3", "lightblue4", "lightcoral", "lightcyan", "lightcyan1", "lightcyan2", "lightcyan3", "lightcyan4", "lightgoldenrod", "lightgoldenrod1", "lightgoldenrod2", "lightgoldenrod3", "lightgoldenrod4", "lightgoldenrodyellow", "lightgray", "lightgrey", "lightpink", "lightpink1", "lightpink2", "lightpink3", "lightpink4", "lightsalmon", "lightsalmon1", "lightsalmon2", "lightsalmon3", "lightsalmon4", "lightseagreen", "lightskyblue", "lightskyblue1", "lightskyblue2", "lightskyblue3", "lightskyblue4", "lightslateblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightsteelblue1", "lightsteelblue2", "lightsteelblue3", "lightsteelblue4", "lightyellow", "lightyellow1", "lightyellow2", "lightyellow3", "lightyellow4", "limegreen", "linen", "magenta", "magenta1", "magenta2", "magenta3", "magenta4", "maroon", "maroon1", "maroon2", "maroon3", "maroon4", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumorchid1", "mediumorchid2", "mediumorchid3", "mediumorchid4", "mediumpurple", "mediumpurple1", "mediumpurple2", "mediumpurple3", "mediumpurple4", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "mistyrose1", "mistyrose2", "mistyrose3", "mistyrose4", "moccasin", "navajowhite", "navajowhite1", "navajowhite2", "navajowhite3", "navajowhite4", "navy", "navyblue", "none", "oldlace", "olivedrab", "olivedrab1", "olivedrab2", "olivedrab3", "olivedrab4", "orange", "orange1", "orange2", "orange3", "orange4", "orangered", "orangered1", "orangered2", "orangered3", "orangered4", "orchid", "orchid1", "orchid2", "orchid3", "orchid4", "palegoldenrod", "palegreen", "palegreen1", "palegreen2", "palegreen3", "palegreen4", "paleturquoise", "paleturquoise1", "paleturquoise2", "paleturquoise3", "paleturquoise4", "palevioletred", "palevioletred1", "palevioletred2", "palevioletred3", "palevioletred4", "papayawhip", "peachpuff", "peachpuff1", "peachpuff2", "peachpuff3", "peachpuff4", "peru", "pink", "pink1", "pink2", "pink3", "pink4", "plum", "plum1", "plum2", "plum3", "plum4", "powderblue", "purple", "purple1", "purple2", "purple3", "purple4", "red", "red1", "red2", "red3", "red4", "rosybrown", "rosybrown1", "rosybrown2", "rosybrown3", "rosybrown4", "royalblue", "royalblue1", "royalblue2", "royalblue3", "royalblue4", "saddlebrown", "salmon", "salmon1", "salmon2", "salmon3", "salmon4", "sandybrown", "seagreen", "seagreen1", "seagreen2", "seagreen3", "seagreen4", "seashell", "seashell1", "seashell2", "seashell3", "seashell4", "sienna", "sienna1", "sienna2", "sienna3", "sienna4", "skyblue", "skyblue1", "skyblue2", "skyblue3", "skyblue4", "slateblue", "slateblue1", "slateblue2", "slateblue3", "slateblue4", "slategray", "slategray1", "slategray2", "slategray3", "slategray4", "slategrey", "snow", "snow1", "snow2", "snow3", "snow4", "springgreen", "springgreen1", "springgreen2", "springgreen3", "springgreen4", "steelblue", "steelblue1", "steelblue2", "steelblue3", "steelblue4", "tan", "tan1", "tan2", "tan3", "tan4", "thistle", "thistle1", "thistle2", "thistle3", "thistle4", "tomato", "tomato1", "tomato2", "tomato3", "tomato4", "transparent", "turquoise", "turquoise1", "turquoise2", "turquoise3", "turquoise4", "violet", "violetred", "violetred1", "violetred2", "violetred3", "violetred4", "wheat", "wheat1", "wheat2", "wheat3", "wheat", "whitesmoke", "yellow", "yellow1", "yellow2", "yellow3", "yellow4", "yellowgreen"]

    # if need colors randomized independently of keyword colors
    if palette == "x11":
        colors = x11
    elif palette == "svg":
        colors = svg
    else:
        colors = rainbow

    shuffle(colors)
    return colors    





f = open('encryption_network.p', 'rb')
network = pickle.load(f)
n = 10

just_nodes = network[0]
node_gens = network[1]
links = network[2]
gens = network[3]

recs = []        
for gen in gens:
    recs += gen

write_dot(network,10,'rsa_network',fake=True)

# likelihood won't trait
#1 - (.2**10)