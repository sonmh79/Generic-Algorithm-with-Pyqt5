import pandas as pd
import time
import random
from collections import OrderedDict


class Heuristic:
    """ Make Initial Solution For GA """

    def __init__(self):
        initial_trips = {}
        for i in range(1, len(self.data) + 1):
            initial_trips[i] = (self.data.loc[i]["Demand"], self.travel_time([0, i, 0]))
            sorted_initial_trips = OrderedDict(sorted(initial_trips.items(), key=lambda x: x[1][1], reverse=True))
        feasible_trips = []
        while len(initial_trips) > 0:
            a = sorted_initial_trips.popitem(last=False)
            del initial_trips[a[0]]
            temp = []
            temp_2 = []
            if len(initial_trips) != 0:
                for i in initial_trips.keys():
                    if initial_trips[i][0] + a[1][0] == 3:  # robot capa = 3
                        temp.append((i, self.d_data[i][a[0]]))

                    elif initial_trips[i][0] + a[1][0] < 3:
                        temp_2.append((i, self.d_data[i][a[0]]))

                if len(temp) != 0:
                    temp.sort(key=lambda x: x[1])
                    next_node = temp[0][0]
                    next_node_demand = initial_trips[next_node][0]
                    feasible_trips.append([a[0], next_node])
                    del sorted_initial_trips[next_node]
                    del initial_trips[next_node]

                else:
                    if len(temp_2) != 0:
                        temp_2.sort(key=lambda x: x[1])
                        next_node = temp_2[0][0]
                        next_node_demand = initial_trips[next_node][0]
                        del sorted_initial_trips[next_node]
                        del initial_trips[next_node]
                        temp_3 = []
                        if len(initial_trips) != 0:
                            for i in initial_trips.keys():
                                if a[1][0] + next_node_demand + initial_trips[i][0] == 3:
                                    temp_3.append((i, self.d_data[next_node][i]))
                            if len(temp_3) != 0:
                                temp_3.sort(key=lambda x: x[1])
                                next_next_node = temp_3[0][0]
                                feasible_trips.append([a[0], next_node, next_next_node])
                                del sorted_initial_trips[next_next_node]
                                del initial_trips[next_next_node]

                            else:
                                feasible_trips.append([a[0], next_node])

                        else:
                            feasible_trips.append([a[0], next_node])

                    else:
                        feasible_trips.append([a[0]])
            else:
                feasible_trips.append([a[0]])
        res = []
        for trip in feasible_trips:
            for t in trip:
                res += [t]
        return res

    def travel_time(self, route):
        total_tt = 0
        for i in range(0, len(route) - 1):
            total_tt = total_tt + self.d_data.iloc[route[i],route[i + 1]]
        return total_tt


class VRP(Heuristic):
    def __init__(self, df, d_data, capacity=3, cnum=100, mutation_prob=0.2, ev_times=100, robots=3):
        self.n = len(d_data)
        self.c = capacity
        self.data = df
        self.d_data = d_data
        self.cnum = cnum
        self.cnt = 0
        self.mutation_prob = mutation_prob
        self.ev_times = ev_times
        self.dist = 0
        self.robots = robots
        self.min_route = []
        self.info = []
        self.gen = []
        # Choose Initial Solution between Heuristic Alg. and Simple Alg.
        self.initial_input = super().__init__()
        if self._calc_route(self.initial_input) > self._calc_route(list(range(1, len(self.data) + 1))):
            self.initial_input = list(range(1, len(self.data) + 1))
            print("Simple Algorithm Selected for Initial Soultion !")
        else:
            print("Heuristic Algorithm Selected for Initial Soultion !")

    def _chromo(self, t=1):

        """ 1. Make Random Chromos """

        res = []
        for _ in range(t):
            res.append(random.sample(range(1, self.n), self.n - 1))
        return res

    def calc_trips(self, trips):
        dist_list = []
        for trip in trips:
            d = 0
            for i in range(len(trip) - 1):
                d += self.d_data.loc[trip[i]][trip[i + 1]]
            dist_list.append(d)

        res = list(zip(dist_list, trips))
        res.sort()
        return res

    def split_trip(self, trip):

        """ Split Trip to Trips """

        stack = 0
        trips = []
        t = [0]
        for node in trip:
            if node == 0:
                stack += 1
            else:
                t.append(node)
            if stack == 2:
                stack = 1
                t.append(0)
                trips.append(t)
                t = [0]
        return trips

    def show_trip(self, route):

        """ Print the Trip of Min Route """

        stack = 0
        new_trips = [0]
        for i in range(len(route)):
            cur_demand = self.data.loc[route[i]]["Demand"]
            if stack + cur_demand <= self.c:
                stack += cur_demand
                new_trips.append(route[i])
            else:
                stack = cur_demand
                new_trips = new_trips + [0]
                new_trips.append(route[i])
        new_trips += [0]
        return new_trips

    def _calc_route(self, route):

        """ 2-1-1 Calculate Distance Considering D Demands """
        stack = 0
        new_trips = [0]
        for i in range(len(route)):
            cur_demand = self.data.loc[route[i]]["Demand"]
            if stack + cur_demand <= self.c:
                stack += cur_demand
                new_trips.append(route[i])
            else:
                stack = cur_demand
                new_trips = new_trips + [0]
                new_trips.append(route[i])
        new_trips += [0]

        res = 0
        for i in range(len(new_trips) - 1):
            res += self.d_data.loc[new_trips[i]][new_trips[i + 1]]
        return res

    def _getdist(self, chromos):

        """ 2-1 Return Distance of Each Chromo """

        dist_list = []

        for chromo in chromos:
            dist_list.append(self._calc_route(chromo))

        fit = list(zip(dist_list, chromos))
        fit.sort(key=lambda x: x[0])
        return fit

    def _rand(self, x, y):
        return int(random.uniform(x, y))

    def _crossover(self, p1, p2, hard_mode=False):

        """ 2-2-2. Crossover and Mutation """

        swap_point = self._rand(1, len(p1))
        c1, c2 = [], []

        i = 0
        while i < swap_point:
            c1.append(p1[i])
            c2.append(p2[i])
            i += 1

        for e in p2:
            if e not in c1:
                c1.append(e)

        for e in p1:
            if e not in c2:
                c2.append(e)

        # mutation
        if random.uniform(0, 1) <= self.mutation_prob and len(c1) > 2 and not hard_mode:
            e1, e2 = random.sample(range(0, len(c1)), 2)
            # target will select mutation child
            if e1 > e2:
                target = e1
            else:
                target = e2

            if target % 2 == 0:
                c1[e1], c1[e2] = c1[e2], c1[e1]
            else:
                c2[e1], c2[e2] = c2[e2], c2[e1]

        if hard_mode:
            e1, e2 = random.sample(range(0, len(c1) - 1), 2)
            c1[e1], c1[e1 + 1] = c1[e1 + 1], c1[e1]
            c2[e2], c2[e2 + 1] = c2[e2 + 1], c2[e2]

        next_gen = self._getdist([c1, c2, p1, p2])
        # print("next_gen: ",next_gen)
        c1, c2 = next_gen[0][1], next_gen[1][1]
        # print("c1,c2: ",c1,c2)
        return [c1, c2]

    def _select_parent(self, parents):

        """ 2-2-1. Select Parents with Roulette Algorithm  """

        fitness = [1 / route[0] for route in parents]
        sum = 0

        for f in fitness:
            sum += f
        p_index = set()

        while len(p_index) < 2:
            fit = 0
            target = random.uniform(0, sum)
            for i in range(len(fitness)):
                fit += fitness[i]
                if fit > target:
                    p_index.add(i)
                    break
        return list(p_index)

    def _make_child(self, dist_routes):

        """ 2-2. Compare Parents with Childs and Return Best Routes  """

        self.cnt += 1
        parents = dist_routes.copy()
        routes = [route[1] for route in parents]
        child = []

        # select top 100 chromos
        while parents and len(child) < self.cnum:
            selected_parents = self._select_parent(parents)
            p1, p2 = routes.pop(selected_parents[0]), routes.pop(selected_parents[1] - 1)
            parents.pop(selected_parents[0]), parents.pop(selected_parents[1] - 1)
            c1, c2 = self._crossover(p1, p2)
            child += c1, c2

        return child

    def evolution(self, chromo):

        """ 2. Make Childs """

        dist_routes = self._getdist(chromo)  # (dist,routes)
        child = self._make_child(dist_routes)
        return child

    def ga(self):

        """ 0. Start Genetic Algorithm !! """

        chromos = self._chromo(99)
        chromos.append(self.initial_input)
        gen = self.evolution(chromos)
        self.info = self._getdist(gen)
        print("First Genenration Minimun Route: ", (self.info[0][0], self.info[0][1]))
        self.gen.append((1, self.info[0][0]))
        stack = 0
        for i in range(self.ev_times):
            gen = self.evolution(gen)
            self.info = self._getdist(gen)
            t = self.cnt
            if t % 10 == 0:
                print("{}/{}th Evolution Min Route: ".format(t, self.ev_times), (self.info[0][0], self.info[0][1]))
                self.gen.append((t,self.info[0][0]))

            # to avoid local minimum
            if t == 30:
                self.mutation_prob = t / 100
                print(f"==================== Mutation Prob Upgrade to {self.mutation_prob} ==================== ")
            elif t == 50:
                self.mutation_prob = t / 100
                print(f"==================== Mutation Prob Upgrade to {self.mutation_prob} ==================== ")
            elif t == 70:
                self.mutation_prob = t / 100
                print(f"==================== Mutation Prob Upgrade to {self.mutation_prob} ==================== ")

            cur_dist = self.info[0][0]
            if self.dist == cur_dist:
                stack += 1
            else:
                stack = 0

            if stack == 30:
                self.dist, self.min_route = self.info[0][0], self.info[0][1]
                print(f'Repeated {stack}times ------------------------------------------BREAK')
                break

            self.dist, self.min_route = self.info[0][0], self.info[0][1]
        self.gen.append((t, self.info[0][0]))

        print("----------------------------------------Finish----------------------------------------")
        print("Total Travel Time / Min Route: ", self.dist, " / ", self.min_route)
        print(self.show_trip(self.info[0][1]))