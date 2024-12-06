import sys

'''
The runNTM class runs and traces the Turing Machine outlined in the csv file on the user inputted string.
'''
class runNTM():
    def __init__(self, file, string, max, limit):
        '''
        Initializes all of the class's attributes.
        '''
        self.read_input(file)  # extracts the data from the file to initialize the machine's attributes
        self.string = string  # the string the machine is evaluating
        self.configurations = [[["", self.start, self.string]]]  # the first level of the configuration tree
        self.depth = 0  # the depth of the tree starts at 0
        self.transition_count = 0  # the total number of transitions starts at 0
        self.result = "Reject"  # the result attribute to determine if the machine accepts, rejects, or runs too long
        self.maxdepth = -1  # set initially to -1 so maxdepth will never be used to terminate unless changed by user
        self.maxtrans = -1  # set initially to -1 so maxtrans will never be used to terminate unless changed by user

        # check which type of termination limit the user specified
        if limit == "d":
            self.maxdepth = max  # the max depth that the machine can run to until being stopped for running too long
        else:
            self.maxtrans = max  # the max number of transitions that the machine can run to until being stopped for running too long

    def read_input(self, file):
        '''
        Reads the formatted csv file and extracts the Turing Machine's information.
        Saves the machine's information as attributes of the class to be accessed by other functions.
        '''
        # open and read the contents of the file
        with open(file, 'r') as f:
            contents = f.readlines() 

        # extract the machine's name, start state, accept state, and reject state from the file
        self.name = contents[0].strip()
        self.start = contents[4].strip()
        self.accept = contents[5].strip()
        self.reject = contents[6].strip()

        # build the transition list from the rest of the lines in the file
        self.transitions = []
        for line in contents[7:]:
            line = line.strip()
            line = line.split(',')
            # add each transition to the list in the form of a dictionary to be easily accessed
            transition = {"cur_state": line[0], "cur_tape": line[1], "new_state": line[2], "new_tape": line[3], "direction": line[4]}
            self.transitions.append(transition)

    def bfs(self):
        '''
        Runs breadth first search on the configurations, adding each new configuration level to the tree.
        Evaluates each configuration using the transitions and adds new configurations to the tree using Turing Machine rules.
        Returns True if the machine has halted (either accepted, rejected, or ran too long).
        Returns False if the machine should continue running.
        '''
        new_configurations = []  # new level of the tree to be added

        # iterate through each configuration in the current last level of the configuration tree
        for configuration in self.configurations[-1]:
            if configuration[1] != self.reject:  # only transition if the state is not the reject state
                transitioned = False  # flag if no transition was made on the current configuration

                # check the configuration against each transition
                for transition in self.transitions:
                    # check if the current state and the tape character under the head matches the transition
                    if transition["cur_state"] == configuration[1] and transition["cur_tape"] == configuration[2][0]:
                        # create a new configuration for moving the tape head right and changing the tape character and state
                        if transition["direction"] == "R":
                            if len(configuration[2]) > 1:
                                new = [configuration[0]+transition["new_tape"], transition["new_state"], configuration[2][1:]]
                            else: # if the head reaches the end of the tape string, show a "_" to indicate blanks for the rest of the tape
                                new = [configuration[0]+transition["new_tape"], transition["new_state"], "_"]
                        
                        # create a new configuration for moving the tape head left and changing the tape character and state
                        else:
                            new = [configuration[0][:-1], transition["new_state"], configuration[0][-1]+transition["new_tape"]+configuration[2][1:]]
                        
                        # add the new configuration to the current tree level
                        new_configurations.append(new)
                        self.transition_count += 1  # increment the total transition count
                        transitioned = True  # indicate that a transition did occur on the current configuration

                        # check if transition_count is equal to the max transition number (if maxtrans never set by user, this will never happen)
                        if self.transition_count == self.maxtrans:
                            # if so, the machine ran too long so end running by adding new configuration level to the tree, increment depth, indicate the result and return
                            self.configurations.append(new_configurations) 
                            self.depth += 1
                            self.result = "Ran Too Long"
                            return True

                        # check if the new state is the accept state
                        if transition["new_state"] == self.accept:
                            # add the new configuration level to the tree, increment the depth, indicate the result is accept and return
                            self.configurations.append(new_configurations) 
                            self.depth += 1
                            self.result = "Accept"
                            return True  # indicates that the bfs has halted
                        
                # check if no transition matched the configuration
                if not transitioned:
                    # if so, have the configuration transition to a reject state
                    if len(configuration[2]) > 1:
                        new = [configuration[0]+configuration[2][0], self.reject, configuration[2][1:]]
                    else:
                        new = [configuration[0]+configuration[2][0], self.reject, "_"] 
                    # add the new configuration to the current tree level
                    new_configurations.append(new) 
                    self.transition_count += 1
                    
                    # check if transition_count is equal to the max transition number (if max not set by user, this will never happen)
                    if self.transition_count == self.maxtrans:
                        # if so, the machine should halt for running too long so add new configuration level, increment depth, and return
                        self.configurations.append(new_configurations) 
                        self.depth += 1
                        self.result = "Ran Too Long"
                        return True 
        
        # check if no new configurations were created (all the configurations in the last level are in the reject state)
        if not new_configurations:
            # indicate that the machine should halt and reject
            self.result = "Reject"
            return True
        
        # add the new level of configurations to the configuration tree and increment the depth 
        self.configurations.append(new_configurations)
        self.depth += 1

        # check if the tree has reached the max depth (if max not set by user, this will never happen)
        if self.depth == self.maxdepth:
            # indicate that the machine should halt for running too long
            self.result = "Ran Too Long"
            return True
        
        # indicate that the machine has not halted and should run again on the next level of configurations
        return False
    
    def run(self):
        '''
        Runs the machine until the breadth first search indicates that it has halted.
        '''
        while not self.bfs(): 
            pass
        

def main():
    '''
    Extracts the machine's filename, string, and other attributes from the command line arguments.
    Creates the runNTM object and runs the machine on the string.
    Writes the results to stdout and a new file.
    '''
    # extract the filename and string from the command line arguments
    machine_file = sys.argv[1]
    string = sys.argv[2]

    # set initial values 
    max = 0 
    limit = "d"
    # if the argument is -d, indicate that the machine should stop if it reaches the max depth specified in the following argument
    if sys.argv[3] == "-d":
        max = int(sys.argv[4])
    # if the argument is -t, indicate that the machine should stop if it reaches the max transition number specified in the following argument
    elif sys.argv[3] == "-t":
        limit = "t"
        max = int(sys.argv[4])

    # create the runNTM object with the user-inputted attributes and run the machine
    machine = runNTM(machine_file, string, max, limit)
    machine.run()

    # print the machine's attributes to stdout
    print(f"Machine: {machine.name}")
    print(f"String: {machine.string}")
    print(f"Depth: {machine.depth}")
    print(f"Total Number of Transitions: {machine.transition_count}")
    print(f"Average Nondeterminism: {machine.transition_count/machine.depth:.3}")
    # change the output depending on the result of the machine
    if machine.result == "Accept":
        print(f"String accepted in {machine.depth}")
        print("Tree:")
        for num, level in enumerate(machine.configurations):
                print(f"Level {num}: {level}")
    elif machine.result == "Reject":
        print(f"String rejected in {machine.depth}")
    else:
        if limit == "d":
            print(f"Execution stopped after limit of {machine.maxdepth} configuration tree depth reached")
        else:
            print(f"Execution stopped after limit of {machine.maxtrans} total transitions reached")

    # write the machine's attributes to the output file
    with open(f"output_traceTM_mfues.txt", "a") as f:
        f.write(f"Machine: {machine.name}\n")
        f.write(f"String: {machine.string}\n")
        f.write(f"Depth: {machine.depth}\n")
        f.write(f"Total Number of Transitions: {machine.transition_count}\n")
        f.write(f"Average Nondeterminism: {machine.transition_count/machine.depth:.3}\n")
        # change the output depending on the result of the machine
        if machine.result == "Accept":
            f.write(f"String accepted in {machine.depth}\n")
            f.write("Tree:\n")
            for num, level in enumerate(machine.configurations):
                f.write(f"Level {num}: {level}\n")
        elif machine.result == "Reject":
            f.write(f"String rejected in {machine.depth}\n")
        else:
            if limit == "d":
                f.write(f"Execution stopped after limit of {machine.maxdepth} configuration tree depth reached\n")
            else:
                f.write(f"Execution stopped after limit of {machine.maxtrans} total transitions reached\n")
        f.write("\n")


if __name__ == "__main__":
    main()