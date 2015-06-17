import patents
import keywords
import networkanalysis
import time
import csv

class Testing(object):
    def __init__(self, 
                 num_records = 200, 
                 num_parents = 1, 
                 dist = 'poisson',
                 gen_len = 20,
                 num_traits = 1,
                 num_keywords = 2,
                 age_exp = 1,
                 cites_exp = 1):

      self.num_records = num_records
      self.num_parents = num_parents
      self.dist = dist
      self.gen_len = gen_len
      self.num_traits = num_traits
      self.num_keywords = num_keywords
      self.age_exp = age_exp
      self.cites_exp = cites_exp
    
    def lets_cite(self):
      self.some_patents = patents.PrefAging(num_records=self.num_records, 
                                            num_parents=self.num_parents,
                                            dist = self.dist,
                                            min_parents = 0, 
                                            gen_len=self.gen_len,
                                            age_exp = self.age_exp,
                                            cites_exp = self.cites_exp
                                            )
                                       
      self.some_patents.form_patents()

      self.some_patents.write_count()
      self.some_patents.cleanup()

    def lets_keyword(self):
      self.key_up = keywords.Keywords(num_records = self.num_records,
                             num_traits=self.num_traits,
                             avg=False,
                             min_traits=0,
                             num_keywords=self.num_keywords,
                             gen_len=self.num_traits)
                             
      self.key_up.assign_keywords()
      #print('Finished assigning keywords')
      self.key_up.write_phenomes()

    def lets_network_and_analyze(self):
      self.na = networkanalysis.NetworkAnalysis('parentage.csv',
                                'phenomes.csv',
                                'final_count.csv',
                                num_traits=self.num_traits, 
                                num_keywords=self.num_keywords,
                                gen_len=self.gen_len)
                                
      self.na.first_degree_chains()
     # self.na.write_inheritance_count()

      xs = [(len(descendents), i) for i, descendents in enumerate(self.na.descendents[0:20])]
      xs.sort()
      return(xs[9][0], xs[10][0], xs[19][0])
      """
      print(xs)
      print('median:')
      print(xs[9][1], xs[10][1])
      print('max:')
      print(xs[18][1], xs[19][1])
      """


"""
      self.na.colors_for_graphviz("rainbow")

      for i in range(20):
          trait = list(self.na.phenomes[i])[0]
          self.na.genealogy_dot(trait, "keyword", i)

      self.na.all_dot(0, "keyword", 20)
"""
#      top_keywords = self.na.get_top_keywords(10)
#      print(self.na.get_top_keywords(100))
#      for keyword, count in top_keywords:
#          self.na.dot_for_graphviz(keyword, "keyword")
#
#      some_ancestors = [0, 25, 100]
#      for ancestor in some_ancestors:
#          self.na.genealogy_dot(ancestor, "phylo")

#      print(self.na.inheritance_average_random())
#      print(self.na.inheritance_average_related())

start_time = time.time()

num_records = 200
num_parents = 16
dist = 'poisson'
gen_len = 20
num_traits = 1
num_keywords = 2
age_exp = 0
cites_exp = 0


medians = [[] for i in range(1000)]
maxes = [[] for i in range(1000)]
"""
with open('median.csv', 'rb') as f:
  for row in csv.reader(f):
    medians.append(row)

with open('max.csv', 'rb') as f:
  for row in csv.reader(f):
    maxes.append(row)
"""

for i in range(4):
  age_exp = i
  for j in range(4):
    cites_exp = j
        
    for k in range(1000):
      test = Testing(num_records, num_parents, dist, gen_len, num_traits, 
                     num_keywords, age_exp, cites_exp)
      test.lets_cite()
      test.lets_keyword()
      x = test.lets_network_and_analyze()
      median = (x[0] + x[1])/2
      medians[k] += [str(median)]
      maximum = (x[2])
      maxes[k] += [str(maximum)]

    print('Finished %d-%d' % (cites_exp, age_exp))

median_file = open('median.csv', 'w')
max_file = open('max.csv', 'w')

median_writer = csv.writer(median_file)
max_writer = csv.writer(max_file)

median_writer.writerows(medians)
max_writer.writerows(maxes)

elapsed_time = (time.time() - start_time) / 60
print(elapsed_time)