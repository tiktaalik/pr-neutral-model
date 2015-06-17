import csv
import os
from random import shuffle



class NetworkAnalysis(object):

    def __init__(self, parentage_file, phenomes_file, progeny_count_file, num_traits=5, num_keywords=100, gen_len=100):
        self.parentage_file = parentage_file
        self.progeny_count_file = progeny_count_file
        self.phenomes_file = phenomes_file
        self.num_traits = num_traits
        self.num_keywords = num_keywords
        self.gen_len = gen_len
        self.setup()

    def setup(self):
        self.define_phenomes()
        self.define_parentage()
        self.define_progeny_count()
        self.define_trait_count()
        self.get_phylogenies()  
    
    def define_trait_count(self):
        self.trait_count = [0 for i in range(self.num_keywords)]

    def define_parentage(self):
        self.parentage = []
        with open(self.parentage_file) as f:
            for row in csv.reader(f, delimiter=","):
                self.parentage.append(row)

        # convert lists of strings to lists of ints
        self.parentage = [map(int, parents) for parents in self.parentage]

        self.num_records = len(self.parentage)

    def define_progeny_count(self):
        if self.progeny_count_file == None:
            return

        self.progeny_count = []
        with open(self.progeny_count_file) as f:
            for row in csv.reader(f):
                self.progeny_count.append(row)
        
    def define_phenomes(self):
        self.phenomes = []
        with open(self.phenomes_file) as f:
            for row in csv.reader(f, delimiter=","):
                self.phenomes.append(row)
        
        # convert lists of strings to frozensets of ints
        self.phenomes = [frozenset(map(int, traits)) for traits in self.phenomes]
    
#==============================================================================
# analysis
#==============================================================================
    def first_degree_chains(self):
        self.inheritance_count = [0 for i in range(len(self.parentage))]
        self.inheritance_interactions = [[] for i in range(len(self.parentage))]
        self.inheritance_interactions_colored = [[] for i in range(len(self.parentage))]
        surviving_keywords = self.get_surviving_keywords(self.gen_len)
        
        for child, parents in enumerate(self.parentage):

            for parent in parents:
                intersection = self.phenomes[parent].intersection(self.phenomes[child])
                # remove from intersection those keywords which do not persist to the final generation                
                intersection = intersection.intersection(surviving_keywords)
                if intersection:
                    self.inheritance_count[parent] += len(intersection)
                    for keyword in intersection:
                        child_and_keyword = (child, keyword)
                        self.update_trait_count(keyword)

                    self.inheritance_interactions_colored[parent].append(child_and_keyword)
                    self.inheritance_interactions[parent].append(child*len(intersection))

    def update_trait_count(self, keyword):
        self.trait_count[keyword] += 1
        
    def get_top_keywords(self, range):
        # most cited patents
        ordered_keywords_and_counts = sorted(enumerate(self.keyword_count), key=itemgetter(1))
        reversed_ks_and_cs = ordered_keywords_and_counts[::-1]
        most_cited_ks_and_cs = reversed_ks_and_cs[0:range]

        return most_cited_ks_and_cs
    
    def get_surviving_keywords(self, gen_len):
        surviving_keywords = set()       
        
        for i in range(gen_len):        
            phenome = self.phenomes[-i]
            for keyword in phenome:
                surviving_keywords.add(keyword)
        return frozenset(surviving_keywords)
 
    def get_phylogenies(self):
        parentage_sets = [frozenset(parents) for parents in self.parentage]
        ancestors = [frozenset() for i in range(len(self.parentage))]

        descendents = [frozenset() for i in range(len(self.parentage))]
        
        # ancestors
        for child, parents in enumerate(parentage_sets):
            ancestors[child] = parents
            for parent in parents:
                ancestors[child] = ancestors[child].union(ancestors[parent])

        # descendents
        direct_descendents = [[] for i in range(len(self.parentage))]
        for child, parents in enumerate(parentage_sets):
            for parent in parents:
                direct_descendents[parent].append(child)

        # This isn't working properly!
        # list of frozensets        
        direct_descendents = [frozenset(i) for i in direct_descendents]
        descendents = direct_descendents

        enum_dds = [(parent, children) for parent, children in enumerate(direct_descendents)]     
        reversed_e_dds = enum_dds[::-1]
        for parent, children in reversed_e_dds:
            for child in children:
                descendents[parent] = direct_descendents[parent].union(descendents[child])

        # list of lists        
        descendents = [list(i) for i in descendents]

        self.ancestors = ancestors   
        self.descendents = descendents

#==============================================================================
#  metrics
#==============================================================================
    def percent_inheritance(self):
        num_citations = 0
        for parents in self.parentage:
            num_citations += len(parents)

        expected = float(self.num_traits ** 2) / (self.num_keywords)
        actual = float(sum(self.keyword_count)) / num_citations

        expected *= 100
        actual *= 100
        print ("expected: %d%%" % expected)
        print ("actual: %d%%" % actual)

    def inheritance_average_random(self):
        for record in range(self.num_records):           
            for comparison in range(self.num_records):
                if record != comparison:                
                    intersection = self.phenomes[record].intersection(self.phenomes[comparison])              
    
                    try:
                      average
                    except NameError:
                        average = float(len(intersection))
                    else:
                        average = float(len(intersection) + average) / 2
           
        return average
                    
    def inheritance_average_related(self):
        for child, parents in enumerate(self.parentage):       
            for parent in parents:
                intersection = self.phenomes[child].intersection(self.phenomes[parent])
                
                try:
                  average
                except NameError:
                    average = float(len(intersection))
                else:
                    average = float(len(intersection) + average) / 2
                    
        return average
        
                    
#==============================================================================
# csv    
#==============================================================================

    def write_inheritance_count(self):
        with open('inheritance_count.txt', 'w') as file:
            writer = csv.writer(file)
            writer.writerow("sum: %d" % self.trait_count)
            writer.writerows("inheritance_count")

#==============================================================================
# plotting
#==============================================================================

    def colors_for_graphviz(self, palette="rainbow"):
        # For multi-colored inheritance layers. Greys, black and white removed.
        # Shuffle into random order
        rainbow = ["red", "yellow", "orange", "green", "blue", "purple"]
        svg = ["aliceblue", "antiquewhite", "aqua", "aquamarine", "beige", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse", "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon", "darkseagreen", "darkslateblue", "darkslategray", "darkturquoise", "darkviolet", "deeppink", "deepskyblue", "dimgray", "dodgerblue", "firebrick", "forestgreen", "fuchsia", "gainsboro", "gold", "goldenrod", "gray", "green", "greenyellow", "hotpink", "indianred", "indigo", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue", "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod", "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink", "plum", "powderblue", "purple", "red", "rosybrown", "royalblue", "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver", "skyblue", "slateblue", "slategray", "slategrey", "springgreen", "steelblue", "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "whitesmoke", "yellow", "yellowgreen"]
        x11 = ["aliceblue", "antiquewhite", "antiquewhite1", "antiquewhite2", "antiquewhite3", "antiquewhite4", "aquamarine", "aquamarine1", "aquamarine2", "aquamarine3", "aquamarine4", "azure", "azure1", "azure2", "azure3", "azure4", "beige", "bisque", "bisque1", "bisque2", "bisque3", "bisque4", "blanchedalmond", "blue", "blue1", "blue2", "blue3", "blue4", "blueviolet", "brown", "brown1", "brown2", "brown3", "brown4", "burlywood", "burlywood1", "burlywood2", "burlywood3", "burlywood4", "cadetblue", "cadetblue1", "cadetblue2", "cadetblue3", "cadetblue4", "chartreuse", "chartreuse1", "chartreuse2", "chartreuse3", "chartreuse4", "chocolate", "chocolate1", "chocolate2", "chocolate3", "chocolate4", "coral", "coral1", "coral2", "coral3", "coral4", "cornflowerblue", "cornsilk", "cornsilk1", "cornsilk2", "cornsilk3", "cornsilk4", "crimson", "cyan", "cyan1", "cyan2", "cyan3", "cyan4", "darkgoldenrod", "darkgoldenrod1", "darkgoldenrod2", "darkgoldenrod3", "darkgoldenrod4", "darkgreen", "darkkhaki", "darkolivegreen", "darkolivegreen1", "darkolivegreen2", "darkolivegreen3", "darkolivegreen4", "darkorange", "darkorange1", "darkorange2", "darkorange3", "darkorange4", "darkorchid", "darkorchid1", "darkorchid2", "darkorchid3", "darkorchid4", "darksalmon", "darkseagreen", "darkseagreen1", "darkseagreen2", "darkseagreen3", "darkseagreen4", "darkslateblue", "darkslategray", "darkslategray1", "darkslategray2", "darkslategray3", "darkslategray4", "darkslategrey", "darkturquoise", "darkviolet", "deeppink", "deeppink1", "deeppink2", "deeppink3", "deeppink4", "deepskyblue", "deepskyblue1", "deepskyblue2", "deepskyblue3", "deepskyblue4", "dimgray", "dimgrey", "dodgerblue", "dodgerblue1", "dodgerblue2", "dodgerblue3", "dodgerblue4", "firebrick", "firebrick1", "firebrick2", "firebrick3", "firebrick4", "floralwhite", "forestgreen", "gainsboro", "ghostwhite", "gold", "gold1", "gold2", "gold3", "gold4", "goldenrod", "goldenrod1", "goldenrod2", "goldenrod3", "goldenrod4", "honeydew", "honeydew1", "honeydew2", "honeydew3", "honeydew4", "hotpink", "hotpink1", "hotpink2", "hotpink3", "hotpink4", "indianred", "indianred1", "indianred2", "indianred3", "indianred4", "indigo", "invis", "ivory", "ivory1", "ivory2", "ivory3", "ivory4", "khaki", "khaki1", "khaki2", "khaki3", "khaki4", "lavender", "lavenderblush", "lavenderblush1", "lavenderblush2", "lavenderblush3", "lavenderblush4", "lawngreen", "lemonchiffon", "lemonchiffon1", "lemonchiffon2", "lemonchiffon3", "lemonchiffon4", "lightblue", "lightblue1", "lightblue2", "lightblue3", "lightblue4", "lightcoral", "lightcyan", "lightcyan1", "lightcyan2", "lightcyan3", "lightcyan4", "lightgoldenrod", "lightgoldenrod1", "lightgoldenrod2", "lightgoldenrod3", "lightgoldenrod4", "lightgoldenrodyellow", "lightgray", "lightgrey", "lightpink", "lightpink1", "lightpink2", "lightpink3", "lightpink4", "lightsalmon", "lightsalmon1", "lightsalmon2", "lightsalmon3", "lightsalmon4", "lightseagreen", "lightskyblue", "lightskyblue1", "lightskyblue2", "lightskyblue3", "lightskyblue4", "lightslateblue", "lightslategray", "lightslategrey", "lightsteelblue", "lightsteelblue1", "lightsteelblue2", "lightsteelblue3", "lightsteelblue4", "lightyellow", "lightyellow1", "lightyellow2", "lightyellow3", "lightyellow4", "limegreen", "linen", "magenta", "magenta1", "magenta2", "magenta3", "magenta4", "maroon", "maroon1", "maroon2", "maroon3", "maroon4", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumorchid1", "mediumorchid2", "mediumorchid3", "mediumorchid4", "mediumpurple", "mediumpurple1", "mediumpurple2", "mediumpurple3", "mediumpurple4", "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "mistyrose1", "mistyrose2", "mistyrose3", "mistyrose4", "moccasin", "navajowhite", "navajowhite1", "navajowhite2", "navajowhite3", "navajowhite4", "navy", "navyblue", "none", "oldlace", "olivedrab", "olivedrab1", "olivedrab2", "olivedrab3", "olivedrab4", "orange", "orange1", "orange2", "orange3", "orange4", "orangered", "orangered1", "orangered2", "orangered3", "orangered4", "orchid", "orchid1", "orchid2", "orchid3", "orchid4", "palegoldenrod", "palegreen", "palegreen1", "palegreen2", "palegreen3", "palegreen4", "paleturquoise", "paleturquoise1", "paleturquoise2", "paleturquoise3", "paleturquoise4", "palevioletred", "palevioletred1", "palevioletred2", "palevioletred3", "palevioletred4", "papayawhip", "peachpuff", "peachpuff1", "peachpuff2", "peachpuff3", "peachpuff4", "peru", "pink", "pink1", "pink2", "pink3", "pink4", "plum", "plum1", "plum2", "plum3", "plum4", "powderblue", "purple", "purple1", "purple2", "purple3", "purple4", "red", "red1", "red2", "red3", "red4", "rosybrown", "rosybrown1", "rosybrown2", "rosybrown3", "rosybrown4", "royalblue", "royalblue1", "royalblue2", "royalblue3", "royalblue4", "saddlebrown", "salmon", "salmon1", "salmon2", "salmon3", "salmon4", "sandybrown", "seagreen", "seagreen1", "seagreen2", "seagreen3", "seagreen4", "seashell", "seashell1", "seashell2", "seashell3", "seashell4", "sienna", "sienna1", "sienna2", "sienna3", "sienna4", "skyblue", "skyblue1", "skyblue2", "skyblue3", "skyblue4", "slateblue", "slateblue1", "slateblue2", "slateblue3", "slateblue4", "slategray", "slategray1", "slategray2", "slategray3", "slategray4", "slategrey", "snow", "snow1", "snow2", "snow3", "snow4", "springgreen", "springgreen1", "springgreen2", "springgreen3", "springgreen4", "steelblue", "steelblue1", "steelblue2", "steelblue3", "steelblue4", "tan", "tan1", "tan2", "tan3", "tan4", "thistle", "thistle1", "thistle2", "thistle3", "thistle4", "tomato", "tomato1", "tomato2", "tomato3", "tomato4", "transparent", "turquoise", "turquoise1", "turquoise2", "turquoise3", "turquoise4", "violet", "violetred", "violetred1", "violetred2", "violetred3", "violetred4", "wheat", "wheat1", "wheat2", "wheat3", "wheat", "whitesmoke", "yellow", "yellow1", "yellow2", "yellow3", "yellow4", "yellowgreen"]


        if not hasattr(self, 'keyword_colors'):
            shuffle(x11)
            self.keyword_colors = x11

        # if need colors randomized independently of keyword colors
        if palette == "x11":
            colors = x11
        elif palette == "svg":
            colors = svg
        else:
            colors = rainbow

        shuffle(colors)
        return colors

    def grid(self, starting_node, ending_node, nodes_per_gen, xmax, ymax, starting_y, num_rows, file):
        xmax = float(xmax)
        ymax = float(ymax)

        y = starting_y
        num_nodes = ending_node - starting_node
        if not num_rows:
            num_rows = (num_nodes/nodes_per_gen)

        # number of inches / (number of rows - 1)
        yincr = ymax / (num_rows - 1)

        x = 0
        for n in range(starting_node, ending_node):
            # max inches across
            xincr = xmax/ (nodes_per_gen - 1)
            file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
            x += xincr

            # new row: reset x and increment y
            if (n + 1) % nodes_per_gen == 0:
               x = 0
               y -= yincr

    def pyramid(self, limits, xmax, ymax, num_rows, file):
        # num_rows should include both pyramid AND rectangular grid in order
        # that each "generation" be equal

        xmax = float(xmax)
        ymax = float(ymax)

        y = ymax
        yprime = 0
        # number of inches / (number of rows - 1)
        yincr = ymax/(num_rows - 1)

        file.write('0 [pos="%f, %f!"];\n' % (xmax/2, y))

        for a_range in limits:
            range_min = a_range[0]
            range_max = a_range[1]

            yprime += yincr
            y -= yincr
            # outermost nodes are on the lines from the origin to the outermost
            # nodes of the first generation of the rectangular grid (a'b/a = b')
            row_width = (yprime*xmax)/(yincr*(len(limits)+1))
            x = xmax/2 - row_width/2
            for n in range(range_min, range_max):
                xincr = row_width / (range_max - range_min - 1)
                file.write('%d [pos="%f, %f!"];\n' % (n, x, y))
                x += xincr

        # starting position for grid
        y -= yincr
        return y

    def dot_for_graphviz(self, selected_layer, focus):
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -Kfdp -n -Tps -o sample.ps  dot_for_graphviz.dot (prints paths which can be opened in Illustrator)

        phylo_prefix = "phylo_"
        keyword_prefix = "keyword_"
        both_prefix = "both_"

        phylo_colors = self.colors_for_graphviz("rainbow")

        edges = []
        for child, parents in enumerate(self.parentage):
            if parents:
                for parent in parents:
                    row = "/*bottom*/ %d -> %d [color=black, layer=\"bottom\", style=\"solid\"];\n" % (parent, child)

                    if 'phylo' in focus:
                       if (selected_layer in self.ancestors[parent]) or (parent == selected_layer):
                            # write rows
                            row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"bold\"];\n"
                                   % (parent, child, phylo_colors[0]))

                    elif selected_layer == "all":
                        pass

                    else:
                        if child in self.inheritance_interactions[parent] and (selected_layer == "top" or type(selected_layer) is int):
                             for citation, keyword in self.inheritance_interactions_colored[parent]:
                                    if child == citation:

                                        if self.inheritance_interactions[parent].count(child) <= 1:
                                            style = "solid"
                                        else:
                                            style = "bold"


                                        if focus == "both":
                                            # phylo edges
                                            if selected_layer in self.ancestors[child]:
                                                    # write rows
                                                    row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n"
                                                           % (parent, child, phylo_colors[0], style))
                                        else:
                                            if type(selected_layer) == int:
                                                if keyword == selected_layer:
                                                    row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n"
                                                           % (parent, child, self.keyword_colors[keyword % len(self.keyword_colors)], style))
                                            elif selected_layer == "top":
                                               # row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"%s\"];\n"
                                                 #          % (parent, child, self.keyword_colors[keyword % len(self.keyword_colors)], style))
                                                 row = ("/*top*/ %d -> %d [color=\"red\", layer=\"top\", style=\"%s\"];\n"
                                                        % (parent, child, style))
                    edges.append(row)

        edges.sort()

        # get the path
        full_path = os.path.realpath(__file__)
        start_path = os.path.dirname(full_path)

        if 'phylo' in focus:
            output_file = phylo_prefix + str(selected_layer) + ".dot"
        elif 'key' in focus:
            output_file = keyword_prefix + str(selected_layer) + ".dot"
        elif 'both' in focus:
            output_file = both_prefix + str(selected_layer) + ".dot"

        final_path = os.path.join(start_path, 'network', 'to_file', output_file)
        file = open(final_path, 'w')

        if not selected_layer in ("all", "bottom"):
            selected_layer = "top"

        # general attributes
        file.write(
"""digraph inheritance {
center=true;
node [shape=point]
node [layer=all];
splines=line;
edge [arrowhead=none];
layers="bottom:top";
layerselect="%s";
overlap="true";

""" % selected_layer
)
        # nodes (house plot)
#==============================================================================
#         xmax = float(30)
#         ymax = float(30)
#         num_rows = 15
# 
#         limits = [(1, 3), (3, 13), (13, 33), (33, 63), (63, 100)]
#         starting_y = self.pyramid(limits, xmax, ymax, num_rows, file)
#         self.grid(100, 1000, 20, xmax, 5, starting_y, num_rows, file)
#==============================================================================

        xmax = float(30)
        ymax = float(30)
        self.grid(0, 1000, self.gen_len, xmax, ymax, ymax, 100, file)

        # edges
        for row in edges:
            file.write(row)
        file.write('}\n')
        file.close()

    def genealogy_dot(self, focus, interest, selected_layer):
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -Kfdp -n -Tps -o sample.ps  dot_for_graphviz.dot (prints paths which can be opened in Illustrator)
        
        descendents = []
        for i in interest:
            descendents += self.descendents[i]
    
        phylo_colors = self.colors_for_graphviz("rainbow")
        
        edges = []
        for child, parents in enumerate(self.parentage):
            if parents:
                for parent in parents:
                    if parent in descendents or parent in interest:
                        row = '/*bottom*/ %d -> %d [color="black", layer="bottom", style="solid"];\n' % (parent, child)
                        # both parent and child possess the selected phenotype
                        if selected_layer.intersection(self.phenomes[child]) and selected_layer.intersection(self.phenomes[parent]):
                            row = ('/*top*/ %d -> %d [color="red", layer="top", style="bold"];\n'
                                           % (parent, child))
                        #elif frozenset(self.phenomes[child]).intersection(frozenset(self.phenomes[parent])):
                        #    row = ('/*top*/ %d -> %d [color="red", layer="top", style="bold"];\n'
                        #                  % (parent, child))
                        edges.append(row)
    
        edges.sort()
    
        # get the path
        full_path = os.path.realpath(__file__)
        start_path = os.path.dirname(full_path)

        output_file = 'top_' + str(len(interest)) + '.dot'
        final_path = os.path.join(start_path, 'network', 'to_file', output_file)
        file = open(final_path, 'w')
    
    
        # general attributes
        file.write(
"""digraph inheritance {
center=true;
ratio = .77
size = 5
node [shape=square, style = filled, fixedsize=false, height = .3, width=.3, fillcolor = black, label = ""]
node [layer=all];
edge [arrowhead=none];

"""
)
        # guide rank
        file.write('/*guide*/ { node [color=invis, fillcolor = invis]; edge [style=invis]; ')
        for i in range(self.num_records//self.gen_len - 1):
            s = ('gen_',str(i),' -> ')
            s = ''.join(s)      
            file.write(s)
        s = ('gen_',str(self.num_records//self.gen_len-1))
        s = ''.join(s) 
        file.write(s)
        file.write(';}\n')
    
    
        # inheritance interactions of interest
        # not using this right now, don't know why I was
        #                        
        ii_set = [set(i) for i in self.inheritance_interactions]
        iis = set()
        for i in range(self.num_records):
            if len(ii_set[i]) != 0:
                iis.add(i)
                iis = iis.union(ii_set[i])
        iiis = frozenset(iis)
        iiis = iiis.intersection(descendents)

        #
        # patent ranks
        #
        # generation
        for i in range(self.num_records//self.gen_len):
            s = ('{ rank = same; gen_',str(i),'; ')            
            s = ''.join(s)
            file.write(s)
            # patent nodes            
            for j in range(self.gen_len):
                # genealogy                
                 rec = i*self.gen_len + j
                 if frozenset(interest).intersection(frozenset(self.ancestors[rec])) or rec in interest:             
                    s = (str(rec),'; ')
                    s = ''.join(s)           
                    file.write(s)
                        
            # close subgraph
            file.write('}\n')

        # color patent nodes (red for trait of interest)
        for patent, phenome in enumerate(self.phenomes):

            relatives_of_interest = frozenset(interest).intersection(frozenset(self.ancestors[patent]))
            relatives_of_interest = list(relatives_of_interest)
            if relatives_of_interest or patent in interest: 
                # does this patent have the phenotype of interest?
                if selected_layer.intersection(phenome):
                    string = str(patent) + ' [color = red, fillcolor = red]\n'
                    file.write(string)
        
        #
        # edges
        for row in edges:
            file.write(row)
        file.write('}\n')
        file.close()

    def all_dot(self, selected_layer, focus, count):
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -n -Tps -o sample.ps dot_for_graphviz.dot (prints paths which can be opened in Illustrator)
    
        phylo_colors = self.colors_for_graphviz("rainbow")
        
        phylo_prefix = "phylo_"
        keyword_prefix = "keyword_"
        both_prefix = "both_"    
        edges = []

        for child, parents in enumerate(self.parentage):
            if parents:
                for parent in parents:
                    row = '/*bottom*/ %d -> %d [color="black", layer="bottom", style="solid"];\n' % (parent, child)
                    if selected_layer in self.phenomes[child] and selected_layer in self.phenomes[parent]:
                        row = ('/*top*/ %d -> %d [color="red", layer="top", style="bold"];\n'
                                       % (parent, child))
                    edges.append(row)
    
        edges.sort()
    
        # get the path
        full_path = os.path.realpath(__file__)
        start_path = os.path.dirname(full_path)
    
        output_file = 'top_' + str(count) + '.dot'

        final_path = os.path.join(start_path, 'network', 'to_file', output_file)
        file = open(final_path, 'w')
    
        layer_select = selected_layer    
        if not selected_layer in ("all", "bottom"):
            layer_select = "top"
        
        # general attributes
        file.write(
"""digraph inheritance {
center=true;
ratio = .77
size = 5
node [shape=square, style = filled, fixedsize=false, height = 1, width= 1, fillcolor = black, label = ""]
node [layer=all];
edge [arrowhead=none];
/*layers="bottom:top";*/
/*layerselect="%s";*/

""" % layer_select
)
        # guide rank
        file.write('/*guide*/ { node [color=invis, fillcolor = invis]; edge [style=invis]; ')
        for i in range(self.num_records//self.gen_len - 1):
            s = ('gen_',str(i),' -> ')
            s = ''.join(s)      
            file.write(s)
        s = ('gen_',str(self.num_records//self.gen_len-1))
        s = ''.join(s) 
        file.write(s)
        file.write(';}\n')

        #
        # patent ranks
        #
        # generation
        for i in range(self.num_records//self.gen_len):
            s = ('{ rank = same; gen_',str(i),'; ')            
            s = ''.join(s)
            file.write(s)
            # patent nodes            
            for j in range(self.gen_len):
                # genealogy                
                rec = i*self.gen_len + j            
                s = (str(rec),'; ')
                s = ''.join(s)           
                file.write(s)
                        
            # close subgraph
            file.write('}\n')

        # color patent nodes (red for trait of interest)
        for patent, phenome in enumerate(self.phenomes):
            if selected_layer in phenome:
                string = str(patent) + ' [color = red, fillcolor = red]\n'
                file.write(string)
        
        #
        # edges
        for row in edges:
            file.write(row)
        file.write('}\n')
        file.close()