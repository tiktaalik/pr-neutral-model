# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 19:30:33 2014

@author: Zackary Okun DUnivin
"""

from random import random, randint, shuffle
import matplotlib.pyplot as plt
from operator import itemgetter
import time
import csv
import os
import numpy




class Patents(object):

    def __init__(self, num_records=1000, num_parents=5, avg=True,
                 min_parents=0, gen_len=100):
        self.num_records = num_records
        self.num_parents = num_parents
        self.avg = avg
        self.gen_len = gen_len

        # set min and max so that number of parents averages num_parents
        if avg:
            self.min_parents = min_parents
            self.max_parents = self.num_parents * 2 - self.min_parents

        else:
            self.min_parents = self.num_parents
            self.max_parents = self.num_parents

        self.define_prior_to_forming()

#==============================================================================
    def define_prior_to_forming(self):
        """Calls the procedures requisite for patent formation"""
        self.define_citation_count()
        self.define_weights()
        self.open_files()

    def define_citation_count(self):
        """Initial citaiton count"""
        self.citation_count = [0 for i in range(self.num_records)]

    def define_weights(self):
        """Initial weights and probabilities"""
        self.weights = []
        self.probs = []

    def output_path(self, out_variety):
        """Paths for output csvs"""
        if self.avg:
            average = "avg"
        else:
            average = "noavg"
        mode = type(self).__name__

        full_path = os.path.realpath(__file__)
        start_path = os.path.dirname(full_path)

        output_file = "%s_rec-%d_par-%d_gen-%i_%s.csv" % (mode, self.num_records/1000, self.num_parents, self.gen_len, average)
        final_path = os.path.join(start_path, 'output', out_variety, output_file)

        return final_path

    def open_files(self):
        """Opens a csv for the citation counts for each patent at t and the 
        parentage of each patent"""
        self.p_file = open('parentage.csv', 'wb')
        self.c_file = open('counts.csv', 'wb')        
        #self.p_file = open(self.output_path('parentage'), 'wb') #for storage
        #self.c_file = open(self.output_path('counts'), 'wb')

        self.p_writer = csv.writer(self.p_file)
        self.c_writer = csv.writer(self.c_file)
        
    def close_file(self, f):
        """Dumps all remaining data into a file and then closes it"""
        f.flush()
        os.fsync(f.fileno())    
        f.close()   

    def new_counts_and_parentage(self):
        """Starts a new list for the counts at t and the parentage to be dumped
         into output files"""
        self.counts = []
        self.parentage = []

    def first_counts_and_parentage(self):
        """The first counts and parentages. These are special because the first
        generation of patents has no citations."""
        self.gen_num = 1

        self.counts = [self.citation_count for i in range(self.gen_len)]
        self.parentage = ['' for i in range(self.gen_len)]
        self.c_writer.writerows(self.counts)
        self.p_writer.writerows(self.parentage)

        self.new_counts_and_parentage()

        self.new_pool()

    def cleanup(self):
        """Securely closes all open output files"""
        self.close_file(self.p_file)
        self.close_file(self.c_file)
        
#==============================================================================
    def form_patents(self):
        """Initiates the formation of patents"""
        self.first_counts_and_parentage()
        while self.now_forming + 1 < self.num_records:
            self.generation()

    def generation(self):
        """Starts a new generation of patents. Patents in the same generation
        do not cite one another."""
        while (self.gen_num + 1) * self.gen_len > self.now_forming:
                self.citing()
        
        self.next_generation()

    def next_generation(self):
        """Wraps up the current generation and starts a new one"""
        self.c_writer.writerows(self.counts)
        self.p_writer.writerows(self.parentage)
        self.new_counts_and_parentage()

        print("Now forming patent_%i" % self.now_forming)
        self.update_weights()
        self.new_pool()
        self.gen_num += 1

    def new_pool(self):
        "Gets a new pool (of patent ids) from which to draw citaitons"""
        n = self.gen_len * self.num_parents * 2
        rwg = RandomWeightedGenerator()
        self.pool = rwg.new_generate(n, self.probs)
        
    def citing(self):
        """Assigns the parents for the patents in the current generation"""
        parents = set()
        x = randint(self.min_parents, self.max_parents)
        
        while len(parents) < x:
            parent = self.pool.pop()
            parents.add(parent)
 
            if len(self.pool) == 0:
                self.new_pool()
                
            if len(parents) == self.now_forming//self.gen_len:
                break
              
        for parent in parents:
            self.update_count(parent)
        self.parentage.append(list(parents))
        self.counts.append(self.citation_count)

        # form next record
        self.now_forming += 1

    def update_count(self, citation):
        """When a patent is cited, it's count is incremented"""
        self.citation_count[citation] += 1

    def update_weights(self):
        """Update the weights and probs according to the number of children each patent
         had at the end of the last generation""" 
        self.summed_weights = sum(self.weights)
        self.probs = [weight/float(self.summed_weights) for weight in self.weights]
        #self.probs = numpy.array(self.weights)/float(self.summed_weights)

    def write_count(self):
        """Write the last set of citation counts for each patent at the end of
         the final generaiton"""
        with open(self.output_path('final_count'), 'wb') as final_count_file:
            writer = csv.writer(final_count_file)
            writer.writerow(self.citation_count)

class Uniform(Patents):

    def form_patents(self):
        """Initiates the formation of patents"""
        self.now_forming = self.gen_len
        self.new_pool()
        super(Uniform, self).form_patents()

    def new_pool(self):
        """Does not use multinomial sampling (RandomWeightedGenerator)"""
        n = self.gen_len * self.num_parents * 30
        upper_bound = (self.now_forming - (self.now_forming % self.gen_len) - 1) # randint() includes upper bound       
        self.pool = [randint(0, upper_bound) for i in range(n)]

class Preferential(Patents):
    def form_patents(self):
        """Initiates the formation of patents"""
        self.now_forming = self.gen_len
        self.update_weights()
        super(Preferential, self).form_patents()

    def update_weights(self):
        self.weights = [1 + (self.citation_count[i] * 3) for i in range(self.now_forming)]
        super(Preferential, self).update_weights()

class Aging(Patents):

    def define_prior_to_forming(self):
        """Calls the procedures requisite for patent formation"""
        super(Aging, self).define_prior_to_forming()
        self.define_aging_coefficients()

    def form_patents(self):
        """Initiates the formation of patents"""
        self.now_forming = self.gen_len
        self.update_weights()
        super(Aging, self).form_patents()

    def define_aging_coefficients(self):
        """Get the aging coefficients for the first generation"""
        self.aging_coefficients = []
        for i in range(self.num_parents):
            self.aging_coefficients.append((self.num_parents + 1 - i) ** -1.45)
        print(self.aging_coefficients)

    def update_weights(self):
        """Updates the weights and probs according the age of its generation. 
         Citation counts are not considered here!""" 
        self.update_aging_coefficients()
        # probability(k) ~ 1 * (d^a)
        # d is the age (t - i), and a is the aging attachment factor            
        self.weights = [1 * self.aging_coefficients[i//self.gen_len] for i in range(self.now_forming)]

        super(Aging, self).update_weights()

    def update_aging_coefficients(self):
        """Inserts the new "oldest" coefficient of the oldest generation at the
         front of the list. Aging coefficients for each generation are assinged
         by the "age" (id) of the "oldest" (lowest id) in the generation"""
        self.aging_coefficients.insert(0, self.now_forming ** -1.45)

class PrefAging(Aging):
    
    def update_weights(self):
        """Updates the weights and probs according the patents generation and
         prior hit count.""" 
        self.update_aging_coefficients()
        # probability(k) ~ 1 + (k ^ w)(d^a) where k is the patent, w is the weight,
        # d is the age (t - i), and a is the aging attachment factor
        self.weights = [1 + (self.citation_count[i] ** 2) * self.aging_coefficients[i//self.gen_len] for i in range(self.now_forming)]

        super(PrefAging, self).update_weights()


class RandomWeightedGenerator(object):
    """Multinomial sampling"""
    def generate(self, weights, sum):
        rnd = random() * sum
        for i, w in enumerate(weights):
            rnd -= w
            if rnd < 0:
                return i

    def new_generate(self, n, probs):
        samples = numpy.random.multinomial(n, probs)
        instances = []
        for i, num_instances in enumerate(samples):
            for n in range(num_instances):
                instances.append(i)
        shuffle(instances)
        return instances


class Keywords(object):

    def __init__(self, keywords_file=None, num_records=1000, num_traits=5, avg=True, min_traits=0, num_keywords=100, gen_len=100):
        self.keywords_file = keywords_file        
        self.num_records = num_records
        self.num_traits = num_traits
        self.num_keywords = num_keywords
        self.gen_len = gen_len
        if avg:
            self.min_traits = min_traits
            self.max_traits = (self.num_traits - self.min_traits) * 2
        else:
            self.min_traits = self.num_traits
            self.max_traits = self.num_traits
            
        self.define_prior_to_assignment()

    def define_prior_to_assignment(self):
        self.define_weights()
        self.define_phenomes()

    def define_weights(self):
        # read weights into list
        keyword_weights = []
        if self.keywords_file:
            with open(self.keywords_file, 'wb') as f:
                for row in csv.reader(f, delimiter=""):
                    keyword_weights.append(row)
        
        # probabilities
        summed_weights = sum(keyword_weights)
        self.probs = [weight/float(summed_weights) for weight in keyword_weights]

    def define_phenomes(self):
        self.phenomes = []
    
    def open_files(self):
        self.p_file = open('phenomes.csv', 'wb')
        self.p_writer = csv.writer(self.p_file)
        
    def close_file(self, f):
        f.flush()
        os.fsync(f.fileno())
        f.close()
        
    def cleanup(self):
        self.close_file(self.p_file)
    
#==============================================================================
# csv    
#==============================================================================
    def write_phenomes(self):   
        with open('phenomes.csv', 'w') as f:
            writer = csv.writer(f)
            list_of_lists = [list(i) for i in self.phenomes]
            writer.writerows(list_of_lists)
            
#==============================================================================
# assignment
#==============================================================================
    def assign_keywords(self):
        self.new_pool()
        for i in range(self.num_records):
            
            if self.pool < self.num_traits*5:
                self.new_pool()            
            traits = set()
            while len(traits) < randint(self.min_traits, self.max_traits):
                trait = self.pool.pop(0)
                traits.add(trait)
            
            self.phenomes.append(frozenset(traits))
            
            if i % self.gen_len == 0:
                print("Now assigning patent_%d" % i)
                self.new_pool()   
                
    def new_pool(self):
        if self.keywords_file:
            n = self.gen_len * self.num_traits * 2
            rwg = RandomWeightedGenerator()
            self.pool = rwg.new_generate(n, self.weights)
        else:
            n = self.num_traits * 1000 * 2
            self.pool = list(numpy.random.randint(0, self.num_keywords, n))

# * * * * * * * * * * * * * * NetworkAnalysis * * * * * * * * * * * * * * * * *
#
# 
class NetworkAnalysis(object):

    def __init__(self, parentage_file, phenomes_file, num_traits=5, num_keywords=100, gen_len=100):
        self.parentage_file = parentage_file
        self.phenomes_file = phenomes_file
        self.num_traits = num_traits
        self.num_keywords = num_keywords
        self.gen_len = gen_len
        self.setup()

    def setup(self):
        self.define_phenomes()
        self.define_parentage()
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
        direct_descendents = [[] for i in range(len(self.parentage))]
        descendents = [frozenset() for i in range(len(self.parentage))]
        
        # ancestors
        for child, parents in enumerate(parentage_sets):
            ancestors[child] = parents
            for parent in parents:
                ancestors[child] = ancestors[child].union(ancestors[parent])

        # descendents
        for child, parents in enumerate(parentage_sets):
            for parent in parents:
                direct_descendents[parent].append(child)
        """
        # This isn't working properly!
        # list of frozensets        
        direct_descendents = [frozenset(i) for i in direct_descendents]
        
        enum_dds = [(child, parents) for child, parents in enumerate(direct_descendents)]     
        reversed_e_dds = enum_dds[::-1]
        for parent, children in reversed_e_dds:
            for child in children:
                descendents[parent] = direct_descendents[parent].union(descendents[child])
        """
             
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
    def dot_for_hiver(self):
        edges = []
        for child, parents in enumerate(self.parentage):
            if not parents:
                pass
                row = "%i;\n" % child
                edges.append(row)
            else:
                for parent in parents:
                    initial_weight = 1

                    if child in self.inheritance_interactions[parent]:
                        initial_weight = 1
                        weight = initial_weight + self.inheritance_interactions[parent].count(child)*initial_weight
                        row = "%i -> %i [color=red]\n" % (parent, child)
#                    else:
#                        row = "/*bottom*/ %i -> %i [color=grey]\n" % (parent, child)
                    edges.append(row)

        edges.sort()

        file = open('dot_for_hiver.dot', 'w')

        file.write("graph inheritance {\n")
        for n in range(len(self.parentage)):
            file.write('%d;\n' % n)
        for row in edges:
            file.write(row)
        file.write('}\n')
        file.close()

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

    def genealogy_dot(self, selected_layer, focus):
        # In command line: dot -Kfdp -n -Textension -o out_name.extension in_name.dot
        # e.g., dot -Kfdp -n -Tps -o sample.ps  dot_for_graphviz.dot (prints paths which can be opened in Illustrator)
        
        interest = 0
        descendents = [interest]
        for i in range(self.num_records):
             if (interest in self.ancestors[i]):
                 descendents.append(i)
                 
        phylo_prefix = "phylo_"
        keyword_prefix = "keyword_"
        both_prefix = "both_"
    
        phylo_colors = self.colors_for_graphviz("rainbow")
        
        edges = []
        for child, parents in enumerate(self.parentage):
            if parents:
                for parent in parents:
                    if parent in descendents or parent == interest:
                        row = "/*bottom*/ %d -> %d [color=black, layer=\"bottom\", style=\"solid\"];\n" % (parent, child)
        
                        # selected genealogy
                        if 'phylo' in focus:
                           if (selected_layer in self.ancestors[parent]) or (parent == selected_layer):
                                # write rows
                                row = ("/*top*/ %d -> %d [color=%s, layer=\"top\", style=\"bold\"];\n"
                                       % (parent, child, 'red')) #phylo_colors[0]
        
                        # entire genealogy
                        elif selected_layer == "all":
                            pass
        
                        # traits and/or selected genealogy
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
    
        layer_select = selected_layer    
        if not selected_layer in ("all", "bottom"):
            layer_select = "top"
    
        # general attributes
        file.write(
"""digraph inheritance {
center=true;
node [shape=point]
node [layer=all];
edge [arrowhead=none];
/*layers="bottom:top";*/
/*layerselect="%s";*/

""" % layer_select
)
        # guide rank
        file.write('/*guide*/ { node [color=invis]; edge [style=invis]; ')
        for i in range(self.num_records//self.gen_len - 1):
            s = ('gen_',str(i),' -> ')
            s = ''.join(s)      
            file.write(s)
        s = ('gen_',str(self.num_records//self.gen_len-1))
        s = ''.join(s) 
        file.write(s)
        file.write(';}\n')
    
    
        # inheritance interactions of interest
        #                        
        ii_set = [set(i) for i in self.inheritance_interactions]
        iis = set()
        for i in range(self.num_records):
            if len(ii_set[i]) != 0:
                iis.add(i)
                iis = iis.union(ii_set[i])
        iiis = frozenset(iis)
        iiis = iiis.intersection(self.descendents[interest])

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
                 if (interest in self.ancestors[rec]) or rec == interest:             
                    s = (str(rec),'; ')
                    s = ''.join(s)           
                    file.write(s)
                        
            # close subgraph
            file.write('}\n')
        
        #
        # edges
        for row in edges:
            file.write(row)
        file.write('}\n')
        file.close()
#
#
# * * * * * * * * * * * * * * NetworkAnalysis * * * * * * * * * * * * * * * * *

class LineGraph(object):
    
    def csv_to_list(self, f):
        l = []
        with open(f) as i_f:
            for row in csv.reader(i_f, delimiter=","):
                l.append(row)

        # convert lists of strings to lists of ints
        l = [map(int, i) for i in l]
        return l

    def prep_counts(self, counts):
        num_to_plot = 1000

        final_count = counts[-1]
        
        # Empty lists for each patent
        self.counts_by_patent = [[] for i in range(num_to_plot)]

        # most cited patents
        ordered_ps_and_cs = sorted(enumerate(final_count), key=itemgetter(1))
        reversed_ps_and_cs = ordered_ps_and_cs[::-1]
        most_cited_ps_and_cs = reversed_ps_and_cs[0:num_to_plot]

        most_cited = []
        for tuple in most_cited_ps_and_cs:
            most_cited.append(tuple[0])

        # Counts vs time for 100 most cited patents
        for i, patent in enumerate(most_cited):
            for count_at_t in counts:
                # count at t for patent_i
                l = self.counts_by_patent[i]
                l.append(count_at_t[patent])

        return self.counts_by_patent

    def plot_counts(self, to_plot):

        for i, v in enumerate(to_plot):
            plt.plot(v)
            #plt.xlim(0, 5000)
            plt.ylabel("Number of Citations")
            plt.xlabel("Time")
            print "List %r done" % i

        plt.show()




class Testing(object):
    def __init__(self):
        self.num_records = 100
        self.num_parents = 4
        self.gen_len = 10
        self.num_traits = 1
        self.num_keywords = 2
    
    def lets_cite(self):
        self.some_patents = Aging(num_records=self.num_records, 
                                         num_parents=self.num_parents,
                                         avg=False,
                                         min_parents=0, 
                                         gen_len=self.gen_len)
                                         
        self.some_patents.form_patents()

        self.some_patents.write_count()
        self.some_patents.cleanup()

    def lets_plot(self):
        self.my_plot = LineGraph()

        # prep
        counts_f = open('counts.csv', 'r')        
        counts = self.my_plot.csv_to_list(counts_f)

        counts_by_patent = self.my_plot.prep_counts(counts)
        
        # plot
        self.my_plot.plot_counts(counts_by_patent)

    def lets_keyword(self):
        self.key_up = Keywords(num_records = self.num_records,
                               num_traits=self.num_traits,
                               avg=False,
                               min_traits=0,
                               num_keywords=self.num_keywords,
                               gen_len=self.num_traits)
                               
        self.key_up.assign_keywords()
        self.key_up.write_phenomes()

    def lets_network_and_analyze(self):
        self.na = NetworkAnalysis('parentage.csv',
                                  'phenomes.csv',
                                  num_traits=self.num_traits, 
                                  num_keywords=self.num_keywords,
                                  gen_len=self.gen_len)
                                  
        self.na.first_degree_chains()
#        self.na.write_inheritance_count()

        self.na.colors_for_graphviz("rainbow")

        layers = ['top']
        for layer in layers:
            self.na.genealogy_dot(layer, "keyword")

#        top_keywords = self.na.get_top_keywords(10)
#        print(self.na.get_top_keywords(100))
#        for keyword, count in top_keywords:
#            self.na.dot_for_graphviz(keyword, "keyword")
#
#        some_ancestors = [0, 25, 100]
#        for ancestor in some_ancestors:
#            self.na.genealogy_dot(ancestor, "phylo")

#        print(self.na.inheritance_average_random())
#        print(self.na.inheritance_average_related())

start_time = time.time()

test = Testing()
#test.lets_plot()
test.lets_cite()
test.lets_keyword()
test.lets_network_and_analyze()
#test

elapsed_time = time.time() - start_time
print elapsed_time
