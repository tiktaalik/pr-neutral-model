import csv
import os
import numpy
import rwg
from random import randint




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
        """Calls the requisite procedures for keyword assignment"""
        self.define_weights()
        self.define_phenomes()

    def define_weights(self):
        """Reads probabilities from a csv for which each row corresponds
         to a keyword and the column (only one) represents the probability
         that it will be cited."""
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
        """Opens the csv to which the phenomes will be written"""
        self.p_file = open('phenomes.csv', 'wb')
        self.p_writer = csv.writer(self.p_file)
        
    def close_file(self, f):
        """Dumps all remaining data into a file and then closes it"""
        f.flush()
        os.fsync(f.fileno())
        f.close()
        
    def cleanup(self):
        """Securely closes all open files"""
        self.close_file(self.p_file)
    
#==============================================================================
# csv    
#==============================================================================
    def write_phenomes(self):
        """Writes the phenomes (assigned triats) to a csv for which each
         row corresponds to a patent and each column a trait which has
         been assigned to that patent."""
        with open('phenomes.csv', 'w') as f:
            writer = csv.writer(f)
            list_of_lists = [list(i) for i in self.phenomes]
            writer.writerows(list_of_lists)
            
#==============================================================================
# assignment
#==============================================================================
    def assign_keywords(self):
        """Assigns keywords to each patent"""
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
                self.new_pool()   
                
    def new_pool(self):
        """Generates the pool of keywords from which traits will be
         assigned"""
        if self.keywords_file:
            n = self.gen_len * self.num_traits * 2
            self.pool = rwg.generate(n, self.weights)
        else:
            n = self.num_traits * 1000 * 2
            self.pool = list(numpy.random.randint(0, self.num_keywords, n))