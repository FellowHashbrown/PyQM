class QM:
    """A class to handle processing the Quine-McCluskey Algorithm.
    """

    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Initialize
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, variables, values):
        self._variables = variables
        self._values = values
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Helper Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __get_bits(self, value):
        """Returns the binary digit for the specified value.
        """

        # Pad the result with extra 0's at the beginning to match how many variables
        # there are being used
        return bin(value)[2:].rjust(len(self._variables), "0")
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Grouping Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __initial_group(self):
        """Creates the initial grouping for the bits from the values
        given to the Quine-McCluskey Algorithm
        """

        # Keep track of groups by 2-dimensional list
        groups = []
        for count in range(len(self._variables) + 1):
            groups.append([])

        # Iterate through values
        for value in self._values:

            # Count number of 1's in value's bit equivalent
            count = self.__get_bits(value).count("1")

            # Add count to proper group
            groups[count].append(Minterm([value], self.__get_bits(value)))
        
        return groups
    
    def __power_set(self, values, prime_implicants):
        """Creates a power set of all valid prime implicants that covers
        the rest of an expression. This is used after the essential prime implicants have been found.
        """

        # Get the power set of all the prime_implicants
        prime_implicants = list(prime_implicants)
        power_set = []

        # Iterate through decimal values from 1 to 2 ** size - 1
        for i in range(1, 2 ** len(prime_implicants)):
            current_set = []

            # Get the binary value of the decimal value
            bin_value = bin(i)[2:].rjust(len(prime_implicants), "0")

            # Find which indexes have 1 in the bin_value string
            for index in range(len(bin_value)):
                if bin_value[index] == "1":
                    current_set.append(prime_implicants[index])
            power_set.append(current_set)
        
        # Remove all subsets that do not cover the rest of the implicants
        minSet = power_set[0]
        for subset in power_set:

            # Get all the values the set covers
            temp_values = []
            for implicant in subset:
                for value in implicant.get_values():
                    if value not in temp_values and value in values:
                        temp_values.append(value)
            temp_values.sort()

            # Check if this subset covers the rest of the values
            if temp_values == values:
                if len(subset) < len(minSet):
                    minSet = subset
        
        return minSet
        
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Compare Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __get_prime_implicants(self, groups = None):
        """Recursively gets the prime implicants for the expression.
        """

        # Get initial group if group is None
        if groups == None:
            groups = self.__initial_group()
        
        # If there is only 1 group, return all the minterms in it
        if len(groups) == 1:
            return groups[0]
        
        # Try comparing the rest
        else:
            unused = []
            comparisons = range(len(groups) - 1)
            new_groups = [[] for c in comparisons]

            for compare in comparisons:
                group1 = groups[compare]
                group2 = groups[compare + 1]

                # Compare every term in group1 with every term in group2
                for term1 in group1:
                    for term2 in group2:
                        
                        # Try combining it
                        term3 = term1.combine(term2)

                        # Only add it to the new group if term3 is not None
                        #   term3 will only be None if term1 and term2 could not
                        #   be combined
                        if term3 != None:
                            term1.use()
                            term2.use()
                            if term3 not in new_groups[compare]:
                                new_groups[compare].append(term3)
            
            # Get list of all unused minterms
            for group in groups:
                for term in group:
                    if not term.used() and term not in unused:
                        unused.append(term)
            
            # Add recursive call
            for term in self.__get_prime_implicants(new_groups):
                if not term.used() and term not in unused:
                    unused.append(term)

            return unused
    
    # # # # # # # # # # # # # # # # # # # # # # # # #
    # Solving Methods
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __solve(self):
        """Solves for the expression returning the minimal amount of prime implicants needed
        to cover the expression.
        """

        # Get the prime implicants
        prime_implicants = self.__get_prime_implicants(self.__initial_group())
        
        # Keep track of values with only 1 implicant
        #   These are the essential prime implicants
        essential_prime_implicants = []
        values_used = [False] * len(self._values)

        for i in range(len(self._values)):
            value = self._values[i]

            uses = 0
            last = None
            for minterm in prime_implicants:
                if value in minterm.get_values():
                    uses += 1
                    last = minterm
            if uses == 1 and last not in essential_prime_implicants:
                for v in last.get_values():
                    values_used[self._values.index(v)] = True
                essential_prime_implicants.append(last)
        
        # Check if all values were used
        if values_used.count(False) == 0:
            return essential_prime_implicants
        
        # Keep track of prime implicants that cover as many values as possible
        #   with as few variables as possible
        prime_implicants = [prime_implicant for prime_implicant in prime_implicants if prime_implicant not in essential_prime_implicants]

        # Check if there is only one implicant left (very rare but just in case)
        if len(prime_implicants) == 1:
            return essential_prime_implicants + prime_implicants

        # Create a power set from the remaining prime implicants and check which
        #   combination of prime implicants gets the simplest form
        return essential_prime_implicants + self.__power_set([
            self._values[index]
            for index in range(len(self._values))
            if not values_used[index]
        ], prime_implicants)
    
    def get_function(self):
        """Returns the expression in readable form.
        """

        # Get the prime implicants and variables
        prime_implicants = self.__solve()

        # Check if there are no prime_implicants; Always False
        if len(prime_implicants) == 0:
            return "0"
        
        if len(prime_implicants) == 1:
            if prime_implicants[0].get_value().count("-") == len(self._variables):
                return "1"

        result = ""

        # Iterate through prime implicants
        for j in range(len(prime_implicants)):
            implicant = prime_implicants[j]

            # Iterate through all bits in the implicants value
            for i in range(len(implicant.get_value())):
                if implicant.get_value()[i] == "0":
                    result += "NOT "
                if implicant.get_value()[i] != "-":
                    result += self._variables[i]
                if implicant.get_value().count("-", i + 1) < len(implicant.get_value()) - i - 1 and implicant.get_value()[i] != "-":
                    result += " AND "
            
            if j < len(prime_implicants) - 1:
                result += " OR "
        
        return result
