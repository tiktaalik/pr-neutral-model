import patents
import keywords
import networkanalysis
import time
import csv
import numpy

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
    return self.some_patents

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
    return self.key_up

  def lets_network_and_analyze(self):
    self.na = networkanalysis.NetworkAnalysis('parentage.csv',
                              'phenomes.csv',
                              'final_count.csv',
                              num_traits=self.num_traits, 
                              num_keywords=self.num_keywords,
                              gen_len=self.gen_len)
                              
    self.na.first_degree_chains()
   # self.na.write_inheritance_count()



#      self.na.all_dot(0, "keyword", 20)

#      top_keywords = self.na.get_top_keywords(10)
#      print(self.na.get_top_keywords(100))
#      for keyword, count in top_keywords:
#        self.na.dot_for_graphviz(keyword, "keyword")
#
#      some_ancestors = [0, 25, 100]
#      for ancestor in some_ancestors:
#        self.na.genealogy_dot(ancestor, "phylo")

#      print(self.na.inheritance_average_random())
#      print(self.na.inheritance_average_related())
    return self.na

start_time = time.time()

num_records = 200
num_parents = 4
dist = 'flat'
gen_len = 20
num_traits = 1
num_keywords = 2
age_exp = 0
cites_exp = 0

test = Testing(num_records,num_parents,dist,gen_len,num_traits,num_keywords,age_exp,cites_exp)

test.lets_cite()
test.lets_keyword()
na = test.lets_network_and_analyze()

xs = [(len(descendents), i) for i, descendents in enumerate(na.descendents[0:20])]
xs.sort()
# just the patent ids
xs = [x[1] for x in xs]
print(xs)

#na.colors_for_graphviz("rainbow")

levels = [xs[19:],xs[18:],xs[10:],xs]
for r in levels:
  na.genealogy_dot("keyword", r, na.phenomes[r[0]])

elapsed_time = time.time() - start_time
print(elapsed_time)