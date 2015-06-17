import csv
import os
import numpy
import rwg



class Patents(object):


    def __init__(self, num_records=1000, num_parents=5, dist='flat',
                 min_parents=0, gen_len=100, age_exp=-1.45, cites_exp=2):
        self.num_records = num_records
        self.num_parents = num_parents
        # 'flat', 'ave' or 'poisson' 
        self.dist = dist
        self.gen_len = gen_len
        self.age_exp = age_exp
        self.cites_exp = cites_exp

        # set min and max so that number of parents averages num_parents
        if dist == 'ave':
            self.min_parents = min_parents
            self.max_parents = self.num_parents * 2 - self.min_parents

        else:
            self.min_parents = self.num_parents
            self.max_parents = self.num_parents

        self.define_prior_to_forming()
        
#==============================================================================
    def define_prior_to_forming(self):
        """Calls the requisite procedures for patent formation"""
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
        """Starts the first generation of patents. Patents in the same generation
        do not cite one another."""
        while (self.gen_num + 1) * self.gen_len > self.now_forming:
                self.citing()
        
        self.next_generation()

    def next_generation(self):
        """Wraps up the current generation and starts a new one"""
        self.c_writer.writerows(self.counts)
        self.p_writer.writerows(self.parentage)
        self.new_counts_and_parentage()

        #print("Now forming patent_%i" % self.now_forming)
        self.update_weights()
        self.new_pool()
        self.gen_num += 1
        
    def citing(self):
        """Assigns the parents for the patents in the current generation"""
        parents = set()
        
        # number of parents for this patent 
        if self.dist == 'poisson':
            x = numpy.random.poisson(self.num_parents)
        else:
            x = numpy.random.randint(self.min_parents, self.max_parents+1) # randint is high exclusive

        while len(parents) < x:
            parent = self.pool.pop()
            parents.add(parent)
            
            # pool is empty! get a new one
            if len(self.pool) == 0:
                self.new_pool()
            
            # for when citing within own generation
            # if first generation, don't keep looking 
            # for new patents to cite when there are none
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
        # with open(self.output_path('final_count'), 'wb') as final_count_file: # storage
        with open('final_count.csv', 'wb') as final_count_file:
            writer = csv.writer(final_count_file)
            writer.writerow(self.citation_count)

class Uniform(Patents):

    def form_patents(self):
        """Initiates the formation of patents"""
        self.now_forming = self.gen_len
        self.new_pool()
        super(Uniform, self).form_patents()

    def new_pool(self):
        """Sample with maximum entropy"""
        n = self.gen_len * self.num_parents * 30
        upper_bound = (self.now_forming - (self.now_forming % self.gen_len) - 1) # randint() includes upper bound       
        self.pool = [randint(0, upper_bound) for i in range(n)]

class PrefAging(Patents):

    def define_prior_to_forming(self):
        """Calls the procedures required for patent formation"""
        super(PrefAging, self).define_prior_to_forming()
        self.define_aging_coefficients()

    def form_patents(self):
        """Initiates the formation of patents"""
        self.now_forming = self.gen_len
        self.update_weights()
        super(PrefAging, self).form_patents()

    def new_pool(self):
        "Gets a new pool (of patent IDs) from which to draw citaitons"""
        n = self.gen_len * self.num_parents * 2
        self.pool = rwg.generate(n, self.probs)

    def define_aging_coefficients(self):
        """Get the aging coefficients for the first generation"""
        self.aging_coefficients = []
        for i in range(self.gen_len):
            self.aging_coefficients.append(1)
    
    def update_weights(self):
        """Updates the weights and probs according the patents generation and
         prior hit count.""" 
        self.update_aging_coefficients()
        # probability(k) ~ (1 + k ^ w)(d^-a) where k is the patent, w is the prior cites weight,
        # d is the age (t - i), and a is the aging attachment factor
        self.weights = [(1 + (self.citation_count[i] ** self.cites_exp)) * self.aging_coefficients[i//self.gen_len] for i in range(self.now_forming)]

        super(PrefAging, self).update_weights()

    def update_aging_coefficients(self):
        """Inserts the new "oldest" coefficient of the oldest generation at the
         front of the list. Aging coefficients for each generation are assinged
         by the "age" (id) of the "oldest" (lowest id) in the generation"""
        self.aging_coefficients.insert(0, self.now_forming ** -self.age_exp)