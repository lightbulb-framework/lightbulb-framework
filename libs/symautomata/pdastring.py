"""
This module retrieves a simple string from a PDA
using the state removal method
"""
from pda import PDAState


class PdaString():
    """Retrieves a string from a PDA"""

    def __init__(self):
        """Class Initialization"""
        self.statediag = []
        self.quickresponse = {}
        self.quickresponse_types = {}
        pass
    
    def _combine_rest_push(self):
        """Combining Rest and Push States"""
        new = []
        change = 0
        # DEBUG
        # logging.debug('Combining Rest and Push')
        i = 0
        examinetypes = self.quickresponse_types[3]
        for state in examinetypes:
            if state.type == 3:
                for nextstate_id in state.trans.keys():
                    found = 0
                    # if nextstate_id != state.id:
                    if nextstate_id in self.quickresponse:
                        examines = self.quickresponse[nextstate_id]
                        for examine in examines:
                            if examine.id == nextstate_id and examine.type == 1:
                                temp = PDAState()
                                temp.type = 1
                                temp.sym = examine.sym
                                temp.id = state.id
                                for nextnextstate_id in examine.trans:
                                    # if nextnextstate_id != examine.id :

                                    for x_char in state.trans[nextstate_id]:
                                        for z_char in examine.trans[
                                                nextnextstate_id]:
                                            if nextnextstate_id not in temp.trans:
                                                temp.trans[
                                                    nextnextstate_id] = []
                                            if x_char != 0 and z_char != 0:
                                                temp.trans[
                                                    nextnextstate_id].append(x_char + z_char)
                                                # DEBUGprint 'transition is now
                                                # '+x_char +' + '+ z_char
                                            elif x_char != 0 and z_char == 0:
                                                temp.trans[
                                                    nextnextstate_id].append(x_char)
                                                # DEBUGprint 'transition is now
                                                # '+x_char
                                            elif x_char == 0 and z_char != 0:
                                                temp.trans[
                                                    nextnextstate_id].append(z_char)
                                                # DEBUGprint 'transition is now
                                                # '+z_char
                                            elif x_char == 0 and z_char == 0:
                                                temp.trans[
                                                    nextnextstate_id].append(0)
                                                # DEBUGprint 'transition is now
                                                # empty'
                                            else:
                                                pass
                                found = 1
                                new.append(temp)

                    if found == 1:
                        # print 'Lets combine one with id '+`state.id`+'(rest)
                        # and one with id '+`nextstate_id`+'(push)'
                        change = 1
                        # del(state.trans[nextstate_id])
            i = i + 1
        if change == 0:
            return []
        else:
            return new

    def _combine_push_rest(self):
        """Combining Push and Rest"""
        new = []
        change = 0
        # DEBUG
        # logging.debug('Combining Push and Rest')
        i = 0
        examinetypes = self.quickresponse_types[1]
        for state in examinetypes:
            if state.type == 1:
                for nextstate_id in state.trans.keys():
                    found = 0
                    # if nextstate_id != state.id:
                    if nextstate_id in self.quickresponse:
                        examines = self.quickresponse[nextstate_id]
                        for examine in examines:
                            if examine.id == nextstate_id and examine.type == 3:
                                temp = PDAState()
                                temp.type = 1
                                temp.sym = state.sym
                                temp.id = state.id
                                for nextnextstate_id in examine.trans:
                                    # if nextnextstate_id != examine.id :
                                    for x_char in state.trans[nextstate_id]:
                                        for z_char in examine.trans[
                                                nextnextstate_id]:
                                            if nextnextstate_id not in temp.trans:
                                                temp.trans[
                                                    nextnextstate_id] = []
                                            if x_char != 0 and z_char != 0:
                                                temp.trans[
                                                    nextnextstate_id].append(x_char + z_char)
                                                # DEBUGprint 'transition is now
                                                # '+x_char +' + '+ z_char
                                            elif x_char != 0 and z_char == 0:
                                                temp.trans[
                                                    nextnextstate_id].append(x_char)
                                                # DEBUGprint 'transition is now
                                                # '+x_char
                                            elif x_char == 0 and z_char != 0:
                                                temp.trans[
                                                    nextnextstate_id].append(z_char)
                                                # DEBUGprint 'transition is now
                                                # '+z_char
                                            elif x_char == 0 and z_char == 0:
                                                temp.trans[
                                                    nextnextstate_id].append(0)
                                                # DEBUGprint 'transition is now
                                                # empty'
                                            else:
                                                pass
                                found = 1
                                new.append(temp)

                    if found == 1:
                        # DEBUGprint 'Lets combine one with id
                        # '+`state.id`+'(push) and one with id
                        # '+`nextstate_id`+'(rest)'
                        change = 1
                        del state.trans[nextstate_id]
            i = i + 1
        if change == 0:
            return []
        else:
            return new


    def _combine_pop_rest(self):
        """Combining Pop and Rest"""
        new = []
        change = 0
        # DEBUG
        # logging.debug('Combining Pop and Rest')
        i = 0
        examinetypes = self.quickresponse_types[2]
        for state in examinetypes:
            if state.type == 2:
                for nextstate_id in state.trans.keys():
                    found = 0
                    # if nextstate_id != state.id:
                    if nextstate_id in self.quickresponse:
                        examines = self.quickresponse[nextstate_id]
                        for examine in examines:
                            if examine.id == nextstate_id and examine.type == 3:
                                if state.sym != 0:
                                    temp = PDAState()
                                    temp.type = 2
                                    temp.sym = state.sym
                                    temp.id = state.id
                                    for nextnextstate_id in examine.trans:
                                        # if nextnextstate_id != examine.id:

                                        for x_char in state.trans[nextstate_id]:
                                            for z_char in examine.trans[
                                                    nextnextstate_id]:
                                                if nextnextstate_id not in temp.trans:
                                                    temp.trans[
                                                        nextnextstate_id] = []
                                                if x_char != 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char + z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char +' + '+ z_char
                                                elif x_char != 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char
                                                elif x_char == 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+z_char
                                                elif x_char == 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(0)
                                                    # DEBUGprint 'transition is
                                                    # now empty'
                                                else:
                                                    pass
                                    found = 1
                                    new.append(temp)
                                else:
                                    for nextnextstate_id in examine.trans:
                                        # if nextnextstate_id != examine.id:

                                        for x_char in state.trans[nextstate_id]:
                                            temp = PDAState()
                                            temp.type = 2
                                            temp.id = state.id
                                            temp.sym = x_char
                                            temp.trans[nextnextstate_id] = []
                                            for z_char in examine.trans[
                                                    nextnextstate_id]:
                                                if z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+z_char
                                                elif z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(0)
                                                    # DEBUGprint 'transition is
                                                    # now empty'
                                                else:
                                                    pass
                                            found = 1
                                            new.append(temp)

                    if found == 1:
                        # DEBUGprint 'Lets combine one with id
                        # '+`state.id`+'(push) and one with id
                        # '+`nextstate_id`+'(rest)'
                        change = 1
                        del state.trans[nextstate_id]
            i = i + 1
        if change == 0:
            return []
        else:
            return new

    def _combine_rest_rest(self):
        """Combining Rest and Rest"""
        new = []
        change = 0
        # DEBUG
        # logging.debug('Combining Rest and Rest')
        i = 0
        examinetypes = self.quickresponse_types[3]
        for state in examinetypes:
            if state.type == 3:
                found = 0
                for nextstate_id in state.trans.keys():
                    secondfound = 0
                    # if nextstate_id != state.id:
                    if nextstate_id in self.quickresponse:
                        examines = self.quickresponse[nextstate_id]
                        for examine in examines:
                            if examine.id == nextstate_id and examine.type == 3:
                                temp = PDAState()
                                temp.type = 3
                                temp.sym = state.sym
                                temp.id = state.id
                                for nextnextstate_id in examine.trans:
                                    if nextnextstate_id != examine.id:
                                        for x_char in state.trans[nextstate_id]:
                                            for z_char in examine.trans[
                                                    nextnextstate_id]:
                                                if nextnextstate_id not in temp.trans:
                                                    temp.trans[
                                                        nextnextstate_id] = []
                                                if x_char != 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char + z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char +' + '+ z_char
                                                elif x_char != 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char
                                                elif x_char == 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+z_char
                                                elif x_char == 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(0)
                                                    # DEBUGprint 'transition is
                                                    # now empty'
                                                else:
                                                    pass
                                                secondfound = 1
                                if secondfound == 1:
                                    new.append(temp)
                                    found = 1

                    if found == 1:
                        # DEBUGprint 'Lets combine one with id
                        # '+`state.id`+'(rest) and one with id
                        # '+`nextstate_id`+'(rest)'
                        change = 1
                        del state.trans[nextstate_id]
            i = i + 1
        if change == 0:
            return []
        else:
            return new

    def _combine_push_pop(self):
        """Combining Push and Pop"""
        new = []
        change = 0
        # DEBUG
        # logging.debug('Combining Push and Pop')
        i = 0
        examinetypes = self.quickresponse_types[1]
        for state in examinetypes:
            if state.type == 1:
                found = 0
                for nextstate_id in state.trans.keys():
                    # if nextstate_id != state.id:
                    if nextstate_id in self.quickresponse:
                        examines = self.quickresponse[nextstate_id]
                        for examine in examines:
                            secondfound = 0
                            if examine.id == nextstate_id and examine.type == 2:
                                temp = PDAState()
                                temp.type = 3
                                temp.sym = 0
                                temp.id = state.id
                                if examine.sym == 0:
                                    for nextnextstate_id in examine.trans:
                                        # if nextnextstate_id != examine.id :
                                        for z_char in examine.trans[
                                                nextnextstate_id]:
                                            if state.sym == z_char:
                                                for x_char in state.trans[
                                                        nextstate_id]:
                                                    # DEBUGprint state.sym+' vs
                                                    # '+z_char
                                                    if nextnextstate_id not in temp.trans:
                                                        temp.trans[
                                                            nextnextstate_id] = []
                                                    if x_char != 0:
                                                        temp.trans[
                                                            nextnextstate_id].append(x_char)
                                                        # DEBUGprint
                                                        # 'transition is now
                                                        # '+x_char
                                                    else:
                                                        temp.trans[
                                                            nextnextstate_id].append(0)
                                                        # DEBUGprint
                                                        # 'transition is now
                                                        # empty'

                                                    secondfound = 1

                                elif state.sym == examine.sym:
                                    for nextnextstate_id in examine.trans:
                                        # if nextnextstate_id != examine.id :
                                        for x_char in state.trans[nextstate_id]:
                                            for z_char in examine.trans[
                                                    nextnextstate_id]:
                                                if nextnextstate_id not in temp.trans:
                                                    temp.trans[
                                                        nextnextstate_id] = []
                                                if x_char != 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char + z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char +' + '+ z_char
                                                elif x_char != 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(x_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+x_char
                                                elif x_char == 0 and z_char != 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(z_char)
                                                    # DEBUGprint 'transition is
                                                    # now '+z_char
                                                elif x_char == 0 and z_char == 0:
                                                    temp.trans[
                                                        nextnextstate_id].append(0)
                                                    # DEBUGprint 'transition is
                                                    # now empty'
                                                else:
                                                    pass
                                                secondfound = 1

                                if secondfound == 1:
                                    new.append(temp)
                                    found = 1
                    if found == 1:
                        # DEBUGprint 'Lets combine one with id
                        # '+`state.id`+'(push) and one with id
                        # '+`nextstate_id`+'(pop)'
                        change = 1
                        # DEBUGprint 'delete '+`nextstate_id`+' from
                        # '+`state.id`
                        del state.trans[nextstate_id]
            i = i + 1
        if change == 0:
            return []
        else:
            return new

    def _check(self, accepted):
        """_check for string existence"""
        # logging.debug('A check is now happening...')
        # for key in self.statediag[1].trans:
        #    logging.debug('transition to '+`key`+" with "+self.statediag[1].trans[key][0])
        total = []
        if 1 in self.quickresponse:
            total = total + self.quickresponse[1]
        if (1, 0) in self.quickresponse:
            total = total + self.quickresponse[(1, 0)]
        for key in total:
            if (key.id == 1 or key.id == (1, 0)) and key.type == 3:
                if accepted is None:
                    if 2 in key.trans:
                        # print 'Found'
                        return key.trans[2]
                else:
                    for state in accepted:
                        if (2, state) in key.trans:
                            # print 'Found'
                            return key.trans[(2, state)]
        return -1

    def _stage(self, accepted, count=0):
        """This is a repeated state in the state removal algorithm"""
        new5 = self._combine_rest_push()
        new1 = self._combine_push_pop()
        new2 = self._combine_push_rest()
        new3 = self._combine_pop_rest()
        new4 = self._combine_rest_rest()
        new = new1 + new2 + new3 + new4 + new5
        del new1
        del new2
        del new3
        del new4
        del new5
        if len(new) == 0:
            # self.printer()
            # print 'PDA is empty'
            # logging.debug('PDA is empty')
            return None

        self.statediag = self.statediag + new
        del new
        # print 'cleaning...'

        # It is cheaper to create a new array than to use the old one and
        # delete a key
        newstates = []
        for key in self.statediag:
            if len(key.trans) == 0 or key.trans == {}:
                # rint 'delete '+`key.id`
                # self.statediag.remove(key)
                pass
            else:
                newstates.append(key)

        del self.statediag
        self.statediag = newstates
        self.quickresponse = {}
        self.quickresponse_types = {}
        self.quickresponse_types[0] = []
        self.quickresponse_types[1] = []
        self.quickresponse_types[2] = []
        self.quickresponse_types[3] = []
        self.quickresponse_types[4] = []
        for state in self.statediag:
            if state.id not in self.quickresponse:
                self.quickresponse[state.id] = [state]
            else:
                self.quickresponse[state.id].append(state)
            self.quickresponse_types[state.type].append(state)

            # else:
            #     print `key.id`+' (type: '+`key.type`+' and sym:'+`key.sym`+')'
            #     print key.trans
        # print 'checking...'
        exists = self._check(accepted)
        if exists == -1:
            # DEBUGself.printer()
            # raw_input('next step?')
            return self._stage(accepted, count + 1)
        else:
            # DEBUGself.printer()
            # print 'Found '
            print exists
            # return self._stage(accepted, count+1)
            return exists

    def printer(self):
        """Visualizes the current state"""
        for key in self.statediag:
            if key.trans is not None and len(key.trans) > 0:
                print '****** ' + repr(key.id) + '(' + repr(key.type)\
                      + ' on sym ' + repr(key.sym) + ') ******'
                print key.trans

    def init(self, states, accepted):
        """Initialization of the indexing dictionaries"""
        self.statediag = []
        for key in states:
            self.statediag.append(states[key])
        self.quickresponse = {}
        self.quickresponse_types = {}
        self.quickresponse_types[0] = []
        self.quickresponse_types[1] = []
        self.quickresponse_types[2] = []
        self.quickresponse_types[3] = []
        self.quickresponse_types[4] = []
        for state in self.statediag:
            if state.id not in self.quickresponse:
                self.quickresponse[state.id] = [state]
            else:
                self.quickresponse[state.id].append(state)
            self.quickresponse_types[state.type].append(state)
        # self.printer()
        # raw_input('next stepA?')
        return self._stage(accepted, 0)
